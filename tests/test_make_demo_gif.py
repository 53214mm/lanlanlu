import os
import sys

from PIL import ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import make_demo_gif as md  # noqa: E402


def test_build_frames_smoke():
    font = ImageFont.load_default(size=12)
    frame = "\n".join(["#" * 8] * 4)
    frames = md.build_frames([frame] * 100, font, font)
    assert len(frames) > 100
    assert all(f.size == (md.W, md.H) for f in frames)
