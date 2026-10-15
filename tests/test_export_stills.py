import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import export_stills as es  # noqa: E402


def test_build_markdown_has_three_labelled_blocks():
    frame = "\n".join(["#" * 8] * 4)
    md = es.build_markdown([frame] * 3, [0, 1, 2], cols=4)
    assert md.count("```") == 6
    for label in es.LABELS:
        assert label in md
