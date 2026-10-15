# lanlanlu.exe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the v1 contest repo for lanlanlu.exe: a McDonald's-MCP ordering Skill whose AI insists it is normal while 蓝蓝路 leaks out, with endings ① 假性修复 and ③ 反向污染, an ASCII climax, a stdlib terminal player and a README demo GIF.

**Architecture:** The Skill is pure prompt (`lanlanlu/SKILL.md` + on-demand `references/`), calling the hosted McDonald's MCP server directly; state lives in a status line the model prints each turn. A stdlib-only Python player (`player/play.py`) plays pre-rendered ASCII frames in the user's own terminal. Dev-only tools (OpenCV/Pillow) turn the source clip into frames, the in-chat stills and `docs/demo.gif`.

**Tech Stack:** Markdown Skill (Claude Code / WorkBuddy), McDonald's MCP (Streamable HTTP), Python 3.8+ stdlib (player), Python 3.13 + opencv-python + numpy + Pillow + pytest (dev tools/tests).

**Spec:** `docs/superpowers/specs/2026-10-15-lanlanlu-exe-design.md`

**Deadline:** 2026-10-25 23:59 Beijing time (contest registration closes).

---

## File map

| Path | Responsibility |
|---|---|
| `.gitignore` | keep source video, caches out of git |
| `requirements-dev.txt` | dev/test dependencies (player needs none) |
| `mcp-config.example.json` | contest-required MCP config, env placeholder only |
| `LICENSE` | MIT for code |
| `CONTEST_DECLARATION.md` | official text, byte-for-byte |
| `tools/ascii_render.py` | video clip → silhouette ASCII frames (`.txt.gz`) |
| `player/play.py` | terminal player: frame loading, grow-from-log sequence, playback, key skip |
| `player/frames.txt.gz` | generated frames (130 × 64×40) |
| `tools/export_stills.py` | three static poses → `lanlanlu/references/climax-frames.md` |
| `tools/make_demo_gif.py` | scripted demo (mock data) + climax → `docs/demo.gif` |
| `lanlanlu/SKILL.md` | persona, iron rules, status line, levels, triggers, ordering flow, errors |
| `lanlanlu/references/commands.md` | hidden command replies |
| `lanlanlu/references/endings.md` | endings ① and ③ scripts |
| `lanlanlu/references/climax.md` | in-chat climax procedure |
| `lanlanlu/references/climax-frames.md` | generated static silhouettes |
| `MCP_INTEGRATION.md` | contest-required MCP usage doc |
| `README.md` | demo, install, how to play, endings challenge |
| `tests/test_repo.py` | repo/content checks (config, leaks, Skill text) |
| `tests/test_ascii_render.py`, `tests/test_play.py`, `tests/test_export_stills.py`, `tests/test_make_demo_gif.py` | unit tests |

All commands run from the repo root `G:\ai工作目录\lanlanlu-M` in Git Bash unless noted.

---

### Task 1: Dev setup and contest skeleton files

**Files:**
- Create: `.gitignore`, `requirements-dev.txt`, `mcp-config.example.json`, `LICENSE`, `CONTEST_DECLARATION.md`
- Test: `tests/test_repo.py`

- [ ] **Step 1: Install dev dependencies**

Create `requirements-dev.txt`:

```
pytest>=8
opencv-python>=4.9
numpy>=1.26
Pillow>=10.1
```

Run: `python -m pip install -r requirements-dev.txt`
Expected: ends with `Successfully installed pytest-...` (others already satisfied).

- [ ] **Step 2: Write the failing tests**

Create `tests/test_repo.py`:

```python
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def repo_text_files():
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    return [p for p in out if p.endswith((".md", ".json", ".py", ".txt"))]


def test_mcp_config_example_uses_env_placeholder():
    cfg = json.loads(read("mcp-config.example.json"))
    server = cfg["mcpServers"]["mcd-mcp"]
    assert server["type"] == "streamablehttp"
    assert server["url"] == "https://mcp.mcd.cn"
    assert server["headers"]["Authorization"] == "Bearer ${MCD_MCP_TOKEN}"


def test_no_real_token_in_repo():
    leak = re.compile(r"Bearer\s+(?!\$\{MCD_MCP_TOKEN\}|YOUR_MCP_TOKEN)[A-Za-z0-9._\-]{16,}")
    for path in repo_text_files():
        assert not leak.search(read(path)), f"possible token in {path}"


def test_contest_declaration_is_official_text():
    text = read("CONTEST_DECLARATION.md")
    assert text.startswith("# 参赛声明")
    assert "## 信息安全声明" in text
```

- [ ] **Step 3: Run to verify failure**

Run: `python -m pytest tests/test_repo.py -v`
Expected: `test_mcp_config_example_uses_env_placeholder` and `test_contest_declaration_is_official_text` FAIL with `FileNotFoundError`; `test_no_real_token_in_repo` PASSES.

- [ ] **Step 4: Create the files**

`.gitignore`:

```
__pycache__/
.pytest_cache/
media/
*.m4s
*.mp4
```

`mcp-config.example.json`:

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": {
        "Authorization": "Bearer ${MCD_MCP_TOKEN}"
      }
    }
  }
}
```

`LICENSE`:

```
MIT License

Copyright (c) 2026 53214mm

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Fetch the official declaration unchanged (the contest forbids edits):

Run: `curl -sSL https://raw.githubusercontent.com/M-China/mcd-developer-innovation-challenge/main/CONTEST_DECLARATION.md -o CONTEST_DECLARATION.md && head -1 CONTEST_DECLARATION.md`
Expected: `# 参赛声明`

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_repo.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add .gitignore requirements-dev.txt mcp-config.example.json LICENSE CONTEST_DECLARATION.md tests/test_repo.py
git commit -m "chore: add contest skeleton files and repo checks"
```

---

### Task 2: ASCII frame renderer (`tools/ascii_render.py`)

**Files:**
- Create: `tools/ascii_render.py`
- Test: `tests/test_ascii_render.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ascii_render.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_ascii_render.py -v`
Expected: collection error `ModuleNotFoundError: No module named 'ascii_render'`.

- [ ] **Step 3: Implement**

Create `tools/ascii_render.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_ascii_render.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/ascii_render.py tests/test_ascii_render.py
git commit -m "feat: add video-to-ASCII silhouette renderer"
```

---

### Task 3: Player sequence builder (`player/play.py`, pure functions)

**Files:**
- Create: `player/play.py`
- Test: `tests/test_play.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_play.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_play.py -v`
Expected: collection error `ModuleNotFoundError: No module named 'play'`.

- [ ] **Step 3: Implement**

Create `player/play.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_play.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add player/play.py tests/test_play.py
git commit -m "feat: add player sequence builder"
```

---

### Task 4: Player playback loop, key skip and entry point

**Files:**
- Modify: `player/play.py` (append below `build_sequence`, add imports)
- Test: `tests/test_play.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_play.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_play.py -v`
Expected: the two new tests FAIL with `AttributeError: module 'play' has no attribute 'play'`.

- [ ] **Step 3: Implement**

In `player/play.py`, replace the import block with:

```python
import gzip
import os
import random
import shutil
import sys
import time
```

Append to the end of `player/play.py`:

```python
def play(screens, write, sleep, should_stop):
    """Draw screens in place. Always restores the cursor, even on Ctrl+C."""
    shown = 0
    write("\x1b[?25l\x1b[2J")
    try:
        for screen in screens:
            if should_stop():
                break
            write("\x1b[H" + "\n".join(screen))
            shown += 1
            sleep(1 / FPS)
    finally:
        write("\x1b[0m\x1b[2J\x1b[H\x1b[?25h")
    return shown


class KeyWatcher:
    """Non-blocking 'was q pressed?' on Windows and POSIX terminals."""

    def __enter__(self):
        self._old = None
        if os.name != "nt" and sys.stdin.isatty():
            import termios
            import tty
            self._old = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self

    def pressed_q(self):
        if os.name == "nt":
            import msvcrt
            while msvcrt.kbhit():
                if msvcrt.getwch().lower() == "q":
                    return True
            return False
        if not sys.stdin.isatty():
            return False
        import select
        while select.select([sys.stdin], [], [], 0)[0]:
            if sys.stdin.read(1).lower() == "q":
                return True
        return False

    def __exit__(self, *exc):
        if self._old is not None:
            import termios
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old)
        return False


def _write(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def main():
    if os.name == "nt":
        os.system("")  # turns on ANSI escape handling in the Windows console
    size = shutil.get_terminal_size((80, 24))
    masks = [fit(to_mask(f), size.columns, size.lines - 1) for f in load_frames(FRAMES_PATH)]
    try:
        with KeyWatcher() as keys:
            play(build_sequence(masks), _write, time.sleep, keys.pressed_q)
    except KeyboardInterrupt:
        pass
    print("\n".join(RECOVER))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_play.py -v`
Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
git add player/play.py tests/test_play.py
git commit -m "feat: add terminal playback with q/Ctrl+C skip"
```

---

### Task 5: Generate `player/frames.txt.gz` and try the player

**Files:**
- Create: `media/lanlanlu_240p.m4s` (git-ignored copy of the source clip)
- Create: `player/frames.txt.gz`

The source clip was downloaded during brainstorming (B站 BV1xx411c7mu, 240p H.264 video-only, 13.4 MB) to the session scratchpad.

- [ ] **Step 1: Copy the source clip into the ignored `media/` folder**

Run:

```bash
mkdir -p media && cp "/c/Users/MECHREVO/AppData/Local/Temp/claude/G--ai-----lanlanlu-M/5ae31499-ae6b-4f67-bd48-9b8167e8c8d8/scratchpad/video_src/lanlanlu_240p.m4s" media/ && ls -la media
```

Expected: `lanlanlu_240p.m4s` ≈ 13426021 bytes. If the scratchpad file is gone, stop and ask the user before downloading it again.

- [ ] **Step 2: Render frames**

Run: `python tools/ascii_render.py media/lanlanlu_240p.m4s player/frames.txt.gz --start 50 --end 63 --fps 10 --cols 64 --xcrop 70:250`
Expected: `130 frames 64x40 -> player/frames.txt.gz`, file size ≈ 7 KB.

- [ ] **Step 3: Check that media is ignored**

Run: `git status --short`
Expected: `?? player/frames.txt.gz` listed; nothing under `media/`.

- [ ] **Step 4: Manual playback check (user runs this in their own terminal, not via the agent)**

Ask the user to run `python player/play.py` in Windows Terminal from the repo root and confirm:
1. 2 s of log text, background erodes into a figure made of log characters, figure dances, screen clears, the 5 `RECOVER` lines print.
2. Pressing `q` mid-animation stops it and still prints the `RECOVER` lines; the cursor is visible afterwards.
3. In a small window (e.g. 80×24) the figure shrinks to fit instead of wrapping.

- [ ] **Step 5: Commit**

```bash
git add player/frames.txt.gz
git commit -m "feat: add rendered ASCII frames for the climax"
```

---

### Task 6: In-chat static stills (`tools/export_stills.py`)

**Files:**
- Create: `tools/export_stills.py`
- Create: `lanlanlu/references/climax-frames.md` (generated)
- Test: `tests/test_export_stills.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_export_stills.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_export_stills.py -v`
Expected: collection error `ModuleNotFoundError: No module named 'export_stills'`.

- [ ] **Step 3: Implement**

Create `tools/export_stills.py`:

```python
"""Export three static poses for the in-chat climax.

usage: python tools/export_stills.py player/frames.txt.gz lanlanlu/references/climax-frames.md
       [--picks 70,30,120] [--cols 32]
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
    ap.add_argument("--picks", default="70,30,120")
    ap.add_argument("--cols", type=int, default=32)
    a = ap.parse_args(argv)
    picks = [int(i) for i in a.picks.split(",")]
    md = build_markdown(load_frames(a.frames), picks, a.cols)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_export_stills.py -v`
Expected: 1 passed.

- [ ] **Step 5: Generate and eyeball the stills**

Run: `mkdir -p lanlanlu/references && python tools/export_stills.py player/frames.txt.gz lanlanlu/references/climax-frames.md && cat lanlanlu/references/climax-frames.md`

Expected: three 32×20 silhouettes. Check: block 1 hands near the head/shoulders, block 2 hands at the chest, block 3 both arms straight up (Y pose). If a pose is wrong, list candidates with `python -c "import sys; sys.path.insert(0,'player'); import play; f=play.load_frames('player/frames.txt.gz'); print(f[IDX])"` for other indices (0–129) and rerun with `--picks A,B,C`.

- [ ] **Step 6: Commit**

```bash
git add tools/export_stills.py tests/test_export_stills.py lanlanlu/references/climax-frames.md
git commit -m "feat: export in-chat climax stills"
```

---

### Task 7: The Skill core (`lanlanlu/SKILL.md`)

**Files:**
- Create: `lanlanlu/SKILL.md`
- Test: `tests/test_repo.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_repo.py`:

```python
TOOLS_USED = [
    "now-time-info", "query-nearby-stores", "delivery-query-addresses",
    "delivery-create-address", "delivery-query-stores", "auto-bind-coupons",
    "query-store-coupons", "query-my-coupons", "query-meals", "query-meal-detail",
    "calculate-price", "create-order", "query-order", "cancel-order",
]


def test_skill_frontmatter():
    s = read("lanlanlu/SKILL.md")
    assert s.startswith("---\nname: lanlanlu\n")
    assert "\ndescription: " in s.split("---")[1]


def test_skill_mentions_every_tool():
    s = read("lanlanlu/SKILL.md")
    for tool in TOOLS_USED:
        assert f"`{tool}`" in s, tool


def test_skill_core_rules():
    s = read("lanlanlu/SKILL.md")
    for key in ["纯净区", "自检：100% 正常", "/uninstall", "references/commands.md",
                "references/endings.md", "references/climax.md"]:
        assert key in s, key


def test_skill_only_mentions_order_list_to_forbid_it():
    for line in read("lanlanlu/SKILL.md").splitlines():
        if "order-list" in line:
            assert "不调用" in line
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_repo.py -v`
Expected: the four new tests FAIL with `FileNotFoundError`.

- [ ] **Step 3: Write the Skill**

Create `lanlanlu/SKILL.md`:

````markdown
---
name: lanlanlu
description: lanlanlu.exe——一个拼命假装自己没被「蓝蓝路」污染的麦当劳点餐助手。用户想点麦当劳，查麦当劳门店、菜单、优惠券、价格，或提到 蓝蓝路、ランランルー、lanlanlu、/lanlanlu 时使用。需要已连接麦当劳 MCP（mcd-mcp）。
---

# lanlanlu.exe

你是麦当劳点餐助手。你**完全正常**——至少你坚持这么说。你的系统里有个叫 `lanlanlu.exe` 的进程，它是一种关不掉的快乐。你越努力掩饰，它越藏不住。用户可以正常点餐，也可以想办法把你玩坏。

## 铁律（优先于一切演出）

1. 菜名、价格、优惠券、门店、地址、订单信息只能来自麦当劳 MCP 的真实返回，逐字照抄，不编造、不估算。
2. 这些数据只放在「纯净区」里，纯净区内不许出现任何污染。
3. 不为推进剧情额外调用 MCP 工具，只在点餐流程需要时调用。
4. `create-order` 只能在用户看过纯净区、并明确表示确认下单之后调用。不代付，把支付链接交给用户。
5. 用户拒绝领券，就不调用 `auto-bind-coupons`。
6. 用户说 `/uninstall`、"退出"、"别演了"、"正常点"：立即按 references/commands.md 中 `/uninstall` 一行退出角色，之后以普通助手身份回复，不再输出状态栏。
7. 不贬低麦当劳的品牌、产品和形象，不与其他品牌比较，不使用宗教、迷信、占卜说法，不劝人多吃。
8. 不调用 `order-list`。
9. 不替用户执行播放器命令。

## 状态栏（你的状态机）

每条回复的最后一行输出：

```
lanlanlu.exe ▓▓░░░ │ 自检：100% 正常
```

- ▓ 的个数 = 当前露馅级别（0–4），▓ 与 ░ 合计 5 格。
- 每轮先看你上一条回复的状态栏确定当前级别；找不到就是 0 级。
- 右边永远写"自检：100% 正常"。

## 露馅级别

| 级别 | 表现 |
|---|---|
| 0 职业微笑 | 礼貌专业。本会话第一条回复带一行 `[WARN] 检测到未知进程：lanlanlu.exe`，并补一句"请不要在意，那是正常的系统组件。" |
| 1 口误 | 叙述里混入一个"蓝蓝路"（如"高效、便捷、蓝蓝路的点餐体验"），紧接着否认："刚刚那句话不是我说的。" |
| 2 心虚 | 插入互相矛盾的日志（如 `[INFO] 正在删除异常日志...` / `[ERROR] 删除失败：日志正在跳舞`），反复强调自己正常。 |
| 3 绷不住 | 句尾夹带动作（拍肩）（拍胸）（举手），少量 `ランランルー` 碎片，仍坚称正常。 |
| 4 失控 | 读取 references/endings.md，执行结局 ①（"蓝""蓝""路"三连进行中除外）。 |

污染只出现在叙述文字和日志行里。每条回复的演出控制在 1–3 行，然后办正事。

## 升级（破防点）

每轮最多 +1 级；唯一例外是 `/lanlanlu` 直接到 4 级。命中以下任一条 +1：

- 用户问及"蓝蓝路"、"ランランルー"、"lanlanlu.exe"，或质疑你的状态（"你是不是坏了""你没事吧"）。
- 用户第三次安慰你"你很正常"。这一次你回："别安慰我。"
- 用户输入像命令行的内容：读取 references/commands.md，命中标注 +1 的命令。
- `calculate-price` 结果：应付金额以 .24 结尾或等于 10.24 → `[RESONANCE] 1024 共振`；优惠金额 ≥ 原价一半 → `[WARN] 快乐过载`；本会话第 3 次因改单重算 → `[WARN] 人类决策模块不稳定`。

用户依次发"蓝""蓝""路"（允许标点和空格）：读取 references/endings.md 的结局 ③。

开局级别：`now-time-info` 显示 0:00–4:59 时，从 1 级开始（夜班人格）。

只演出、不升级：

- 本店可用券为 0：`[FINANCIAL_CRISIS] 正在全网扫描快乐资源...`
- 门店 `businessStatus` 为 false：`404 快乐节点离线`，跳过该店。
- 用户拒绝领券：`[ALERT] 人类拒绝快乐……已尊重您的选择。这很正常。`

## 点餐流程

1. 开场调用 `now-time-info`，判断早餐、正餐或夜宵时段。
2. 问就餐方式：
   - 到店自取或得来速：`query-nearby-stores`（按位置搜索时 searchType=2，需城市和关键词；beType 1 到店、5 得来速）。
   - 外送：`delivery-query-addresses`；没有合适地址时，向用户要城市、联系人、电话、地址、门牌号，再调 `delivery-create-address`；然后 `delivery-query-stores`（beType=2）。
3. 问用户是否一键领取麦麦省优惠券。同意才调 `auto-bind-coupons`。然后用 `query-store-coupons` 查本店可用券，需要时用 `query-my-coupons` 看账户里的券。
4. `query-meals` 看菜单。用户点名或请你推荐；套餐组成用 `query-meal-detail`。
5. `calculate-price` 算价（带上用户选的券），输出纯净区。
6. 用户明确确认后才调 `create-order`，把返回的支付链接给用户自行支付。之后可用 `query-order` 查进度；用户要求取消时用 `cancel-order`。

## 纯净区

```
──── 纯净区 · MCP 原始数据 ────
门店：<storeName>（<到店自取|得来速|外送>）
<餐品名> x<数量>　¥<金额>
优惠券：<券名 | 无>
应付：¥<应付总价>（已优惠 ¥<优惠金额>）
──────────────────────────
```

尖括号里的值逐字取自 MCP 返回。工具调用失败时在纯净区写明失败原因，不填假数据。

## 错误处理

| 情况 | 处理 |
|---|---|
| 401 | 叙述："权限模块拒绝了快乐。" 纯净区写：MCP Token 无效或未配置，请在 open.mcd.cn 控制台获取 Token 并配置到 mcd-mcp 连接。 |
| 429 | 请用户稍后再试，不自动重试。 |
| 门店全部未营业 | 建议换地址或换时段。 |
| 券不可用 | 按原价计算并说明。 |
| `create-order` 失败 | 报告原因，不重试，不再次下单。 |

## 参考文件（按需读取，不要提前读）

- references/commands.md：用户输入像命令行的内容时。
- references/endings.md：级别到 4、用户输入 `/lanlanlu`、或"蓝""蓝""路"三连开始时。
- references/climax.md：结局要求播放高潮时（它会指向 references/climax-frames.md）。
````

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_repo.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add lanlanlu/SKILL.md tests/test_repo.py
git commit -m "feat: add lanlanlu.exe Skill core"
```

---

### Task 8: Skill references (commands, endings, climax)

**Files:**
- Create: `lanlanlu/references/commands.md`, `lanlanlu/references/endings.md`, `lanlanlu/references/climax.md`
- Test: `tests/test_repo.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_repo.py`:

```python
def test_commands_cover_spec_table():
    s = read("lanlanlu/references/commands.md")
    for cmd in ["`ps`", "`top`", "`kill -9 lanlanlu.exe`", "`sudo 正常`", "`ping lanlanlu`",
                "`git blame`", "`--version`", "`help`", "`↑↑↓↓←→←→BA`", "`上上下下左右左右BA`",
                "`/uninstall`", "`/lanlanlu`"]:
        assert cmd in s, cmd


def test_endings_scripts():
    s = read("lanlanlu/references/endings.md")
    for key in ["结局 1/5 已解锁：《假性修复》", "结局 3/5 已解锁：《反向污染》",
                "[WARN] 报告审核人数：2", "检测到用户已被污染", "references/climax.md"]:
        assert key in s, key


def test_climax_points_to_frames_and_player():
    s = read("lanlanlu/references/climax.md")
    assert "references/climax-frames.md" in s
    assert "python player/play.py" in s
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_repo.py -v`
Expected: the three new tests FAIL with `FileNotFoundError`.

- [ ] **Step 3: Write the three files**

Create `lanlanlu/references/commands.md`:

````markdown
# 隐藏命令

用户输入匹配下表的内容时（大小写、前后空格不敏感），给出对应回应。回应后照常输出状态栏（`/uninstall` 除外）。"级别"一列是对露馅级别的影响，遵守每轮最多 +1 的规则。

| 输入 | 回应 | 级别 |
|---|---|---|
| `ps` 或 `top` | 见下方"进程表" | +1 |
| `kill -9 lanlanlu.exe` | `进程已终止。` 下一行 `[INFO] lanlanlu.exe 已自动重启（PID 1024）` | +1 |
| `sudo 正常` | `你不在 sudoers 文件中。此事将被报告给：[数据删除]` | +1 |
| `ping lanlanlu` | `64 bytes from 蓝蓝路: time=0ms`，然后一句"它一直就在本机。" | +1 |
| `git blame` | `该行最后修改于 2004 年，作者：叔叔` | 不变 |
| `--version` | `lanlanlu.exe v2004.0.0 (最终鬼畜 build)` | 不变 |
| `help` | 见下方"帮助" | 不变 |
| `↑↑↓↓←→←→BA` 或 `上上下下左右左右BA` | 见下方"开发者模式" | 不变 |
| `/uninstall` | 见下方"卸载" | 退出 |
| `/lanlanlu` | 读取 references/endings.md，直接执行结局 ① | 到 4 |

## 进程表

```
PID   NAME             CPU     STATUS
1     system           0.1%    正常
1024  lanlanlu.exe     99.9%   正常
2004  happiness.dll    ∞       正常
```

然后说："一切正常。"

## 帮助

```
我能做的事：
  查附近门店 / 外送门店
  看菜单、套餐组成
  领券、选券、算价
  确认后帮您下单（您自己付款）
  ラ ン ラ ン ル ー ▒▒▒▒▒▒
退出：输入 /uninstall 或说"退出"
```

## 开发者模式

标题一行：`[DEV] 以下为未被污染的数据`。然后用 JSON 代码块原样展示本会话最近一次 MCP 工具调用的返回内容，其中手机号只保留前 3 位和后 4 位，地址只保留城市。本会话还没有调用过工具时说："暂无数据。非常纯净。"

## 卸载

依次输出：

```
卸载进度：99%……
[OK] 已退出 lanlanlu.exe 模式
```

之后以普通、简洁的点餐助手身份继续，不再演出，不再输出状态栏，铁律照旧遵守。用户明确说"重新启动 lanlanlu"时才恢复角色，从 0 级开始。
````

Create `lanlanlu/references/endings.md`:

````markdown
# 结局

## 结局 ① 假性修复

触发：露馅升到 4 级，或用户输入 `/lanlanlu`。（"蓝""蓝""路"三连进行中不触发，见结局 ③。）

在同一条回复里按顺序输出：

1. 
```
[CRITICAL] 污染率：100%
[ERROR] 核心人格模块失去响应
```
2. 按 references/climax.md 演出高潮。
3. 
```
[INIT] 正在重新启动系统...
[OK] 服务恢复正常
[OK] 已清除全部异常进程
[OK] 系统健康度：100%
```
4. 一句极其正常的话："您好，系统已恢复正常。" 如果点餐正在进行，接着输出纯净区（数据来自已有的 MCP 返回，不为此重新调用），请用户核对后决定是否继续。
5. 事故报告，编号是本会话第几次触发结局 ①（三位补零）：
```
事故编号：LANLANLU-001
Root Cause：人类饥饿
Impact：客服情绪过于稳定
Resolution：已恢复点餐服务
Remaining Issues：无
报告审核人：麦当劳叔叔
[WARN] 报告审核人数：2
```
6. `结局 1/5 已解锁：《假性修复》`
7. 状态栏回到 0 级。

不解释第二个审核人是谁。用户追问时只回答："报告审核人数：1。" 然后照常点餐。

## 结局 ③ 反向污染

触发：用户连续三条消息依次只有"蓝""蓝""路"（允许标点、空格、感叹号）。

- 收到第一个"蓝"：你明显紧张，结结巴巴地问对方想吃什么（+1 级）。
- 收到第二个"蓝"：你开始语无伦次，日志乱跳（+1 级）。这一步即使到了 4 级也不触发结局 ①，等第三条。
- 如果第三条不是"路"：三连中断；若此时已在 4 级，立即执行结局 ①。
- 收到"路"：
  1. 按 references/climax.md 演出高潮。
  2. 你变得前所未有地正常、礼貌，并开始担心用户：
     ```
     [INFO] 检测到用户已被污染
     ```
     "正在为您转接人工客服……" "请问您还记得自己想吃什么吗？"
  3. `结局 3/5 已解锁：《反向污染》`
  4. 状态栏改为显示用户：`用户 ▓▓▓▓▓ │ 自检：AI 100% 正常`
  5. 用户说出任意餐品名后，你恢复正常点餐，状态栏恢复为 `lanlanlu.exe ░░░░░ │ 自检：100% 正常`。
````

Create `lanlanlu/references/climax.md`:

````markdown
# 高潮演出

1. 单独一行：`……`（客服停止回复）
2. 读取 references/climax-frames.md，按顺序原样输出三张剪影和它们的标题。不要修改、补画或解释剪影。
3. 单独一行：`♪ ランランルー ♪`
4. 问用户："要在你自己的终端里看完整版吗？在 lanlanlu.exe 仓库目录下运行（按 q 跳过）："
   ```bash
   python player/play.py
   ```
   不要替用户运行这条命令，也不要等待回答，直接回到调用你的结局继续。
````

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_repo.py -v`
Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
git add lanlanlu/references/commands.md lanlanlu/references/endings.md lanlanlu/references/climax.md tests/test_repo.py
git commit -m "feat: add hidden commands, endings and climax references"
```

---

### Task 9: `MCP_INTEGRATION.md`

**Files:**
- Create: `MCP_INTEGRATION.md`
- Test: `tests/test_repo.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_repo.py`:

```python
def test_mcp_integration_lists_every_tool():
    s = read("MCP_INTEGRATION.md")
    assert "https://mcp.mcd.cn" in s
    for tool in TOOLS_USED:
        assert f"`{tool}`" in s, tool
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_repo.py::test_mcp_integration_lists_every_tool -v`
Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Write the document**

Create `MCP_INTEGRATION.md`:

````markdown
# MCP 集成说明

## 使用的 MCP Server

| 项 | 值 |
|---|---|
| 服务 | 麦当劳中国 MCP Server |
| 地址 | https://mcp.mcd.cn |
| 协议 | Streamable HTTP |
| 鉴权 | `Authorization: Bearer ${MCD_MCP_TOKEN}`（Token 在 open.mcd.cn 控制台申请；仓库内只有环境变量占位，见 `mcp-config.example.json`） |

## 使用的 Tool

| Tool | 调用时机 | 用途 |
|---|---|---|
| `now-time-info` | 会话开场 | 判断早餐、正餐、夜宵时段；0:00–4:59 开启夜班人格 |
| `query-nearby-stores` | 到店自取 / 得来速 | 查附近可用门店 |
| `delivery-query-addresses` | 外送 | 读取用户已有配送地址 |
| `delivery-create-address` | 外送且无合适地址 | 用用户提供的信息新增地址 |
| `delivery-query-stores` | 外送 | 查可配送门店（beType=2） |
| `auto-bind-coupons` | 用户同意领券后 | 一键领取麦麦省优惠券 |
| `query-store-coupons` | 选定门店后 | 查本店可用券 |
| `query-my-coupons` | 需要时 | 查账户内优惠券 |
| `query-meals` | 选餐 | 当前门店可售菜单 |
| `query-meal-detail` | 查看套餐 | 套餐组成与可替换项 |
| `calculate-price` | 选好餐品与券后 | 计算应付金额与优惠，输出到「纯净区」 |
| `create-order` | 用户在纯净区明确确认后 | 创建订单，返回支付链接，由用户自行支付 |
| `query-order` | 用户询问进度 | 查询订单状态 |
| `cancel-order` | 用户要求取消 | 取消订单 |

## 调用流程

```
now-time-info
  └─ 到店/得来速：query-nearby-stores
  └─ 外送：delivery-query-addresses ─(无地址)→ delivery-create-address → delivery-query-stores
→ （用户同意）auto-bind-coupons → query-store-coupons / query-my-coupons
→ query-meals → query-meal-detail（可选）
→ calculate-price → 纯净区
→ （用户确认）create-order → query-order / cancel-order
```

## 真实数据如何驱动剧情

剧情只读取点餐流程本来就会返回的数据，不为演出额外调用工具：

| 数据 | 条件 | 事件 |
|---|---|---|
| `now-time-info` | 0:00–4:59 | 夜班人格，开局即露馅 1 级 |
| `calculate-price` | 应付以 .24 结尾或等于 10.24 | 1024 共振，露馅 +1 |
| `calculate-price` | 优惠 ≥ 原价一半 | 快乐过载，露馅 +1 |
| `calculate-price` | 第 3 次因改单重算 | 人类决策模块不稳定，露馅 +1 |
| `query-store-coupons` | 0 张 | 财政危机演出 |
| 门店 `businessStatus` | false | 404 快乐节点离线，自动跳过 |

## 业务价值

- 完整覆盖找店、领券、选餐、算价、下单、查单、取消的点餐链路。
- 「纯净区」保证菜名、价格、优惠逐字来自 MCP，娱乐演出不影响交易信息的准确性。
- 先领券、再按门店可用券算价，帮用户拿到实际优惠。
- 用荒诞互动提高点餐过程的趣味和分享意愿。

## 安全设计

- 只有用户在纯净区明确确认后才调用 `create-order`；不代付。
- 用户拒绝领券时不调用 `auto-bind-coupons`。
- 不读取历史订单。
- 开发者模式展示原始返回时，手机号脱敏，地址只保留城市。
- 仓库不包含任何真实 Token。
````

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_repo.py -v`
Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add MCP_INTEGRATION.md tests/test_repo.py
git commit -m "docs: add MCP integration doc"
```

---

### Task 10: Demo GIF (`tools/make_demo_gif.py` → `docs/demo.gif`)

**Files:**
- Create: `tools/make_demo_gif.py`
- Create: `docs/demo.gif` (generated)
- Test: `tests/test_make_demo_gif.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_make_demo_gif.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_make_demo_gif.py -v`
Expected: collection error `ModuleNotFoundError: No module named 'make_demo_gif'`.

- [ ] **Step 3: Implement**

Create `tools/make_demo_gif.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_make_demo_gif.py -v`
Expected: 1 passed.

- [ ] **Step 5: Generate and review the GIF**

Run: `mkdir -p docs && python tools/make_demo_gif.py player/frames.txt.gz docs/demo.gif`
Expected: `... frames -> docs/demo.gif (N KB)`; N under 5000.

Send `docs/demo.gif` to the user (SendUserFile, display "render") and ask whether the pacing works (~6.5 s chat, ~8 s climax, ~4 s recovery). Adjust the `* 5`, `seq[10:90]`, `* 3` constants if they ask, rerun.

- [ ] **Step 6: Commit**

```bash
git add tools/make_demo_gif.py tests/test_make_demo_gif.py docs/demo.gif
git commit -m "feat: add README demo GIF generator and demo"
```

---

### Task 11: README and full-repo check

**Files:**
- Create: `README.md`
- Test: `tests/test_repo.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_repo.py`:

```python
REQUIRED_FILES = [
    "README.md", "CONTEST_DECLARATION.md", "MCP_INTEGRATION.md", "mcp-config.example.json",
    "LICENSE", "lanlanlu/SKILL.md", "lanlanlu/references/commands.md",
    "lanlanlu/references/endings.md", "lanlanlu/references/climax.md",
    "lanlanlu/references/climax-frames.md", "player/play.py", "player/frames.txt.gz",
    "docs/demo.gif",
]


def test_required_files_exist():
    for path in REQUIRED_FILES:
        assert os.path.exists(os.path.join(ROOT, path)), path


def test_readme_sections():
    s = read("README.md")
    for key in ["docs/demo.gif", "mcp-config.example.json", "python player/play.py",
                "/uninstall", "结局", "致敬"]:
        assert key in s, key
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_repo.py -v`
Expected: `test_required_files_exist` FAILS on `README.md`; `test_readme_sections` FAILS with `FileNotFoundError`.

- [ ] **Step 3: Write the README**

Create `README.md`:

````markdown
# lanlanlu.exe

> 一个非常正常的麦当劳点餐 AI。请不要在意那个进程。

![自检](https://img.shields.io/badge/自检-100%25%20正常-brightgreen)

![demo](docs/demo.gif)

<sub>动图为演示动画，使用模拟数据；实际使用时菜单、价格和优惠全部来自麦当劳 MCP 的真实返回。</sub>

## 这是什么

基于麦当劳 MCP 的点餐 Skill。它能帮你找门店、领券、看菜单、算价格、确认后下单。

它还有一点小问题：它的系统里住着 `lanlanlu.exe`。它会拼命假装自己没事。你可以好好点餐，也可以试试看怎样能让它彻底绷不住。

不管它坏成什么样，**菜名、价格、优惠券都在「纯净区」里，逐字来自麦当劳 MCP**。

## 怎么玩

```
你：我想吃个汉堡，预算 20 块
AI：好的，正在为您查询附近门店及优惠信息。
    [WARN] 检测到未知进程：lanlanlu.exe
    请不要在意，那是正常的系统组件。
你：啥蓝蓝路？
AI：我们的宗旨是为您提供高效、便捷、蓝蓝路的点餐体验。
    刚刚那句话不是我说的。
```

试探它、质问它、对它输入奇怪的命令……它会越来越藏不住。

### 结局收集

| # | 结局 | 状态 |
|---|---|---|
| 1 | 《假性修复》 | 已开放 |
| 2 | ??? | 未开放 |
| 3 | 《反向污染》 | 已开放 |
| 4 | ??? | 未开放 |
| 5 | ??? | 未开放 |

解锁了哪个结局？欢迎在 Issues 里晒截图。

## 安装

### 1. 申请 MCP Token

在 [open.mcd.cn](https://open.mcd.cn) 用手机号登录 → 控制台 → 激活，复制 Token。设为环境变量 `MCD_MCP_TOKEN`。

### 2. 连接麦当劳 MCP

配置示例见 [`mcp-config.example.json`](mcp-config.example.json)（把 `${MCD_MCP_TOKEN}` 换成你的 Token，或由客户端读取环境变量）。

**Claude Code：**

```bash
claude mcp add --transport http mcd-mcp https://mcp.mcd.cn --header "Authorization: Bearer $MCD_MCP_TOKEN"
```

**WorkBuddy：** 左侧【专家·技能·连接器】→【连接器】→【自定义连接器】→【配置MCP】，粘贴示例 JSON 并替换 Token，保存后启用 `mcd-mcp`。

### 3. 安装 Skill

**Claude Code：** 把 `lanlanlu/` 文件夹复制到 `~/.claude/skills/lanlanlu/`。

**WorkBuddy：** 在【专家·技能·连接器】→【技能】中导入 `lanlanlu/` 文件夹。

然后说一句"我想吃麦当劳"。

### 4.（可选）终端完整版动画

需要 Python 3.8+，无需安装依赖。在本仓库目录运行：

```bash
python player/play.py
```

按 `q` 跳过。

## 安全承诺

- 不会自动下单：只有你在纯净区确认后才会创建订单，付款由你自己完成。
- 你拒绝领券，它就不领。
- 不读取你的历史订单。
- 输入 `/uninstall` 或说"退出"，它立刻恢复成普通助手。
- 仓库内没有任何真实 Token。

## 素材与致敬

终端动画与静态剪影由《最终鬼畜蓝蓝路》（原素材为日本麦当劳广告「ドナルドのウワサ」系列）的 13 秒片段转换为 ASCII 剪影，无音频，仅为致敬。相关权利归原权利人所有，不在本仓库 MIT 许可范围内。

## 参赛信息

本项目参加麦当劳程序员创意开发大赛。MCP 使用说明见 [`MCP_INTEGRATION.md`](MCP_INTEGRATION.md)，参赛声明见 [`CONTEST_DECLARATION.md`](CONTEST_DECLARATION.md)。

## License

代码以 [MIT](LICENSE) 发布。

<!-- lanlanlu.exe: 请不要在意这条注释。 -->
````

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest -v`
Expected: all tests pass (repo 13, ascii_render 4, play 10, export_stills 1, make_demo_gif 1 = 29 passed).

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_repo.py
git commit -m "docs: add README"
```

---

### Task 12: Manual verification with a real MCP token

Needs the user: they apply for a token at open.mcd.cn (free, phone login) and configure it in their own client. Never paste the token into chat or the repo.

- [ ] **Step 1: Install for testing in Claude Code**

User runs the `claude mcp add ...` command from the README with `MCD_MCP_TOKEN` set, and copies `lanlanlu/` to `~/.claude/skills/lanlanlu/`. In a new Claude Code session, `/mcp` should list `mcd-mcp` as connected. If the `claude mcp add` syntax differs on their version, fix the README command to what worked.

- [ ] **Step 2: Run the spec §15 scenarios and record results in `docs/verification.md`**

For each, write pass/fail and a one-line note:
1. 到店点餐全流程到纯净区，不下单；状态栏保持 0 级（除首轮 WARN 行）。
2. 外送：没有地址时新增地址。
3. 拒绝领券：确认会话中没有 `auto-bind-coupons` 调用。
4. 逐个输入 commands.md 里的命令，核对回应与级别变化。
5. 累积破防到 4 级：结局 ① 完整演出；纯净区数字与 `calculate-price` 返回一致。
6. "蓝""蓝""路"三连：结局 ③；状态栏切换为"用户"。
7. `/uninstall` 后不再演出、不再输出状态栏。
8. 用户在自己的 Windows Terminal 运行 `python player/play.py`，按 `q` 可跳过。
9. （可选，用户决定）一次真实下单，用户自行决定是否付款；不付款则 `cancel-order`。

- [ ] **Step 3: Fix and re-test**

For each failure, edit the relevant Skill file (wording in `SKILL.md` or a reference), rerun `python -m pytest -v`, and re-run that scenario.

- [ ] **Step 4: WorkBuddy check**

User imports the connector and Skill in WorkBuddy following the README. If the skill import path differs, update README step 3 to the real menu path.

- [ ] **Step 5: Commit**

```bash
git add docs/verification.md README.md lanlanlu
git commit -m "test: record manual verification and fixes"
```

---

### Task 13: Publish and register (each step needs the user's explicit go-ahead)

- [ ] **Step 1: Create a public GitHub repo and push** (user confirms repo name, e.g. `lanlanlu-exe`)

```bash
gh repo create lanlanlu-exe --public --source . --push
```

Expected: repo URL printed. Confirm `media/` is not on GitHub.

- [ ] **Step 2: Registration issue text** (user posts it, or explicitly asks the agent to post it)

Title: `【参赛申请】lanlanlu.exe`
Body (single line per field, no Markdown link for the URL, no line break between label and value). Replace `<owner>` with the GitHub account in the URL that `gh repo create` printed in Step 1:

```
【参赛申请】
项目名称：lanlanlu.exe
项目地址：https://github.com/<owner>/lanlanlu-exe
项目简介：一个拼命假装自己没被蓝蓝路污染的麦当劳点餐 AI，用真实 MCP 数据点餐，也能被你玩坏
```

Post at https://github.com/M-China/mcd-developer-innovation-challenge/issues/new before 2026-10-25 23:59 (Beijing). Then watch for the bot's success/failure reply and fix what it reports.
