import gzip
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import ascii_render as ar  # noqa: E402


def figure_on_wall():
    img = np.full((120, 160, 3), 235, np.uint8)   # near-white wall
    img[20:100, 50:110] = (0, 0, 220)              # red body (BGR)
    img[40:60, 70:90] = (240, 240, 240)            # white face enclosed by the body
    return img


def test_mask_fills_enclosed_face():
    m = ar.foreground_mask(figure_on_wall())
    assert m[50, 80]
    assert m[30, 60]
    assert not m[5, 5]


def test_to_silhouette_shape_and_chars():
    s = ar.to_silhouette(figure_on_wall(), cols=16, rows=6)
    lines = s.split("\n")
    assert len(lines) == 6 and all(len(line) == 16 for line in lines)
    assert set(s) <= {"#", " ", "\n"}
    assert lines[0][0] == " "
    assert "#" in lines[3]


def test_crop_trims_edges_then_xcrop():
    f = np.zeros((240, 320, 3), np.uint8)
    assert ar.crop(f).shape[:2] == (228, 304)
    assert ar.crop(f, (70, 250)).shape[:2] == (228, 180)


def test_write_frames_roundtrip(tmp_path):
    p = tmp_path / "f.txt.gz"
    ar.write_frames(["a", "b"], str(p))
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        assert fh.read() == "a\fb"


def test_write_frames_uses_lf_bytes(tmp_path):
    p = tmp_path / "f.txt.gz"
    ar.write_frames(["a\nb", "c"], str(p))
    with gzip.open(p, "rb") as fh:
        assert b"\r" not in fh.read()


def test_main_exits_clearly_when_no_frames(tmp_path):
    import pytest
    with pytest.raises(SystemExit) as exc:
        ar.main([str(tmp_path / "missing.mp4"), str(tmp_path / "o.txt.gz"),
                 "--start", "0", "--end", "1"])
    assert "no frames read" in str(exc.value)
