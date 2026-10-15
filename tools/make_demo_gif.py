"""Render docs/demo.gif: scripted chat (mock data) -> climax -> fake recovery.

usage: python tools/make_demo_gif.py player/frames.txt.gz docs/demo.gif
       [--cjk-font C:/Windows/Fonts/msyh.ttc] [--mono-font C:/Windows/Fonts/consola.ttf]
Dev-only: needs Pillow.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "player"))
from play import RECOVER, build_sequence, load_frames, to_mask  # noqa: E402

W, H = 900, 600
BG, FG, DIM, WARN, USER = (14, 14, 14), (225, 225, 225), (120, 120, 120), (255, 196, 60), (120, 200, 255)
COLORS = {"user": USER, "ai": FG, "log": DIM, "warn": WARN}
LABEL = "演示动画 · 模拟数据"

CHAT = [
    ("user", "我想吃个汉堡，预算 20 块"),
    ("ai", "好的，正在为您查询附近门店及优惠信息。"),
    ("log", "[INFO] 正在通过 MCP 获取菜单..."),
    ("warn", "[WARN] 检测到未知进程：lanlanlu.exe"),
    ("ai", "请不要在意，那是正常的系统组件。"),
    ("user", "啥蓝蓝路？"),
    ("ai", "我们的宗旨是为您提供高效、便捷、蓝蓝路的点餐体验。"),
    ("warn", "[ERROR] 非预期输出已被检测"),
    ("ai", "刚刚那句话不是我说的。"),
    ("user", "kill -9 lanlanlu.exe"),
    ("ai", "进程已终止。"),
    ("warn", "[INFO] lanlanlu.exe 已自动重启（PID 1024）"),
    ("warn", "[CRITICAL] 污染率：100%"),
]

TAIL = [("log", line) for line in RECOVER if line] + [
    ("ai", "您好，系统已恢复正常。请核对餐品与价格后决定是否下单。"),
    ("log", "事故编号：LANLANLU-001"),
    ("log", "Root Cause：人类饥饿"),
    ("log", "Impact：客服情绪过于稳定"),
    ("log", "Remaining Issues：无"),
    ("log", "报告审核人：麦当劳叔叔"),
    ("warn", "[WARN] 报告审核人数：2"),
]


def text_frame(items, font, status):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((W - 200, 8), LABEL, font=font, fill=DIM)
    y = 36
    for kind, text in items[-17:]:
        d.text((24, y), ("> " if kind == "user" else "") + text, font=font, fill=COLORS[kind])
        y += 28
    d.line((0, H - 44, W, H - 44), fill=DIM)
    d.text((24, H - 34), status, font=font, fill=DIM)
    return im.quantize(colors=16)


def screen_frame(screen, mono, font):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((W - 200, 8), LABEL, font=font, fill=DIM)
    cw = mono.getbbox("M")[2]
    ch = int(mono.size * 1.15)
    x0 = (W - cw * len(screen[0])) // 2
    y0 = (H - ch * len(screen)) // 2
    for r, line in enumerate(screen):
        d.text((x0, y0 + r * ch), line, font=mono, fill=FG)
    return im.quantize(colors=16)


def build_frames(frames_text, font, mono):
    out = []
    shown = []
    for i, item in enumerate(CHAT):
        shown.append(item)
        level = min(4, i // 3)
        status = f"lanlanlu.exe [{'#' * level}{'-' * (4 - level)}] | 自检：100% 正常"
        out += [text_frame(shown, font, status)] * 5
    seq = build_sequence([to_mask(f) for f in frames_text])
    out += [screen_frame(s, mono, font) for s in seq[10:90]]
    shown = []
    for item in TAIL:
        shown.append(item)
        out += [text_frame(shown, font, "lanlanlu.exe [----] | 自检：100% 正常")] * 3
    out += [out[-1]] * 20
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("frames")
    ap.add_argument("out")
    ap.add_argument("--cjk-font", default=r"C:\Windows\Fonts\msyh.ttc")
    ap.add_argument("--mono-font", default=r"C:\Windows\Fonts\consola.ttf")
    a = ap.parse_args(argv)
    font = ImageFont.truetype(a.cjk_font, 18)
    mono = ImageFont.truetype(a.mono_font, 12)
    frames = build_frames(load_frames(a.frames), font, mono)
    frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True)
    print(f"{len(frames)} frames -> {a.out} ({os.path.getsize(a.out) // 1024} KB)")


if __name__ == "__main__":
    main()
