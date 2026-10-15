"""Export three static poses for the in-chat climax.

usage: python tools/export_stills.py player/frames.txt.gz lanlanlu/references/climax-frames.md
       [--picks 57,101,120] [--cols 32]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "player"))
from play import fit, load_frames, to_mask  # noqa: E402

LABELS = ["蓝（拍肩）", "蓝（拍胸）", "路（举手）"]


def render(mask):
    return "\n".join("".join("#" if c else " " for c in row).rstrip() for row in mask)


def build_markdown(frames, picks, cols):
    parts = ["# 高潮静态剪影", "", "按顺序原样输出下面三个代码块，每块上方带它的粗体标题。", ""]
    for label, idx in zip(LABELS, picks):
        mask = fit(to_mask(frames[idx]), cols, cols)
        parts += [f"**{label}**", "", "```", render(mask), "```", ""]
    return "\n".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("frames")
    ap.add_argument("out")
    ap.add_argument("--picks", default="57,101,120")
    ap.add_argument("--cols", type=int, default=32)
    a = ap.parse_args(argv)
    picks = [int(i) for i in a.picks.split(",")]
    md = build_markdown(load_frames(a.frames), picks, a.cols)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
