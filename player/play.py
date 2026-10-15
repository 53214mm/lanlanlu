"""lanlanlu.exe terminal player. Standard library only.

usage: python player/play.py      (press q or Ctrl+C to skip)
"""
import gzip
import os
import random

FPS = 10
HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES_PATH = os.path.join(HERE, "frames.txt.gz")

LOG = [
    "[INFO] connecting mcp.mcd.cn (streamable-http)",
    "[ OK ] auth: bearer token accepted",
    "[INFO] call now-time-info -> 12:03 lunch",
    "[INFO] call query-nearby-stores beType=1",
    "[ OK ] 3 stores open",
    "[INFO] call query-meals storeCode=****",
    "[ OK ] menu loaded",
    "[INFO] call query-store-coupons",
    "[ OK ] coupons loaded",
    "[WARN] unknown process: lanlanlu.exe",
    "[INFO] this is a normal system component",
    "[INFO] call calculate-price",
    "[ OK ] price calculated",
    "[WARN] customer service mood: too stable",
    "[INFO] ignoring lanlanlu.exe",
    "[INFO] ignoring lanlanlu.exe",
    "[ERR ] cannot ignore lanlanlu.exe",
]

RECOVER = [
    "[INIT] restarting service...",
    "[ OK ] all abnormal processes cleared",
    "[ OK ] system health: 100%",
    "",
    "Hello. The system is completely normal.",
]


def load_frames(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return fh.read().split("\f")


def to_mask(frame):
    return [[ch != " " for ch in line] for line in frame.split("\n")]


def fit(mask, cols, rows):
    """Nearest-neighbour shrink so the mask fits in cols x rows."""
    src_rows, src_cols = len(mask), len(mask[0])
    if src_cols <= cols and src_rows <= rows:
        return mask
    scale = min(cols / src_cols, rows / src_rows)
    out_rows = max(1, int(src_rows * scale))
    out_cols = max(1, int(src_cols * scale))
    return [[mask[int(r / scale)][int(c / scale)] for c in range(out_cols)]
            for r in range(out_rows)]


def log_screen(offset, rows, cols):
    return [LOG[(offset + r) % len(LOG)].ljust(cols)[:cols] for r in range(rows)]


def erode_screen(base, mask, order, p):
    """Figure cells keep their log char; a background cell vanishes once p > its order."""
    return ["".join(base[r][c] if mask[r][c] or order[r][c] >= p else " "
                    for c in range(len(mask[0])))
            for r in range(len(mask))]


def masked_screen(mask, shift, stream):
    cols = len(mask[0])
    return ["".join(stream[(shift + r * cols + c) % len(stream)] if mask[r][c] else " "
                    for c in range(cols))
            for r in range(len(mask))]


def build_sequence(masks, seed=7):
    """2 s of normal log, 2 s of the background eroding away, then the dance made of log text."""
    rows, cols = len(masks[0]), len(masks[0][0])
    screens = [log_screen(i // 2, rows, cols) for i in range(20)]
    rng = random.Random(seed)
    order = [[rng.random() for _ in range(cols)] for _ in range(rows)]
    base = log_screen(10, rows, cols)
    for i in range(20):
        screens.append(erode_screen(base, masks[0], order, (i + 1) / 20))
    stream = "  ".join(LOG)
    for i, m in enumerate(masks):
        screens.append(masked_screen(m, i * 7, stream))
    return screens
