import gzip
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "player"))
import play  # noqa: E402


def test_load_frames_splits_on_formfeed(tmp_path):
    p = tmp_path / "f.txt.gz"
    with gzip.open(p, "wt", encoding="utf-8") as fh:
        fh.write("ab\ncd\fef\ngh")
    assert play.load_frames(str(p)) == ["ab\ncd", "ef\ngh"]


def test_to_mask_marks_non_space():
    assert play.to_mask("# \n #") == [[True, False], [False, True]]


def test_fit_keeps_small_mask():
    m = [[True, False]]
    assert play.fit(m, 10, 10) is m


def test_fit_shrinks_to_bounds():
    m = [[True] * 64 for _ in range(40)]
    out = play.fit(m, 32, 20)
    assert len(out) == 20 and len(out[0]) == 32


def test_log_screen_dimensions():
    s = play.log_screen(3, rows=5, cols=12)
    assert len(s) == 5 and all(len(line) == 12 for line in s)


def test_erode_screen_extremes():
    base = ["abc", "def"]
    mask = [[True, False, False], [False, False, True]]
    order = [[0.5] * 3, [0.5] * 3]
    assert play.erode_screen(base, mask, order, 0.0) == base
    assert play.erode_screen(base, mask, order, 1.0) == ["a  ", "  f"]


def test_masked_screen_blank_outside_mask():
    out = play.masked_screen([[True, False], [False, True]], 0, "xyz")
    assert out[0][1] == " " and out[1][0] == " "
    assert out[0][0] != " " and out[1][1] != " "


def test_build_sequence_phases():
    masks = [play.to_mask("#  \n # "), play.to_mask(" # \n#  ")]
    screens = play.build_sequence(masks)
    assert len(screens) == 20 + 20 + 2
    assert all(len(s) == 2 and all(len(line) == 3 for line in s) for s in screens)


def test_play_stops_when_asked_and_restores_cursor():
    out = []
    answers = iter([False, False, True])
    shown = play.play([["a"], ["b"], ["c"], ["d"]], out.append, lambda s: None,
                      lambda: next(answers))
    assert shown == 2
    assert out[0].startswith("\x1b[?25l")
    assert out[-1].endswith("\x1b[?25h")


def test_play_restores_cursor_on_interrupt():
    out = []

    def boom(_):
        raise KeyboardInterrupt

    try:
        play.play([["a"], ["b"]], out.append, boom, lambda: False)
    except KeyboardInterrupt:
        pass
    assert out[-1].endswith("\x1b[?25h")


def test_erode_screen_fills_figure_spaces():
    assert play.erode_screen(["a c"], [[True, True, False]], [[0.5] * 3], 1.0) == ["a# "]


def test_build_sequence_figure_is_solid():
    masks = [play.to_mask("\n".join(["#" * 40] * 5))] * 2
    screens = play.build_sequence(masks)
    for s in screens[20:]:
        assert all(ch != " " for line in s for ch in line)
