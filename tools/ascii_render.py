"""Convert a video segment into silhouette ASCII frames for player/play.py.

usage: python tools/ascii_render.py SRC OUT.txt.gz --start 50 --end 63
       [--fps 10] [--cols 64] [--xcrop 70:250]

Dev-only: needs opencv-python and numpy. The player itself is stdlib-only.
"""
import argparse
import gzip

import cv2
import numpy as np

EDGE_Y, EDGE_X = 6, 8  # the source clip has a dark letterbox edge


def foreground_mask(bgr):
    """Figure on a near-white wall: saturated or darkish pixels are foreground;
    holes the border can't reach (the white face) are filled in."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    s, v = hsv[..., 1], hsv[..., 2]
    fg = ((s > 55) | (v < 165)).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    h, w = fg.shape
    flood = fg * 255
    ff_mask = np.zeros((h + 2, w + 2), np.uint8)
    border = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + \
             [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    for x, y in border:
        if flood[y, x] == 0:
            cv2.floodFill(flood, ff_mask, (x, y), 128)
    return flood != 128


def to_silhouette(bgr, cols, rows):
    mask = foreground_mask(cv2.resize(bgr, (cols * 4, rows * 4)))
    small = cv2.resize(mask.astype(np.uint8), (cols, rows), interpolation=cv2.INTER_AREA) > 0
    return "\n".join("".join("#" if small[y, x] else " " for x in range(cols))
                     for y in range(rows))


def crop(frame, xcrop=None):
    f = frame[EDGE_Y:-EDGE_Y, EDGE_X:-EDGE_X]
    if xcrop:
        f = f[:, xcrop[0]:xcrop[1]]
    return f


def extract(src, start, end, fps):
    cap = cv2.VideoCapture(src)
    t = start
    while t < end:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        yield frame
        t += 1 / fps


def write_frames(frames, path):
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write("\f".join(frames))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--start", type=float, required=True)
    ap.add_argument("--end", type=float, required=True)
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--cols", type=int, default=64)
    ap.add_argument("--xcrop", default="", help="x0:x1 crop applied after edge trim")
    a = ap.parse_args(argv)
    xcrop = tuple(map(int, a.xcrop.split(":"))) if a.xcrop else None
    frames = [crop(f, xcrop) for f in extract(a.src, a.start, a.end, a.fps)]
    h, w = frames[0].shape[:2]
    rows = int(a.cols * h / w / 2)  # terminal cells are ~2:1
    write_frames([to_silhouette(f, a.cols, rows) for f in frames], a.out)
    print(f"{len(frames)} frames {a.cols}x{rows} -> {a.out}")


if __name__ == "__main__":
    main()
