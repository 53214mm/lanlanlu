"""lanlanlu.exe terminal player. Standard library only.

usage: python player/play.py      (press q or Ctrl+C to skip)
"""
import gzip
import os
import random
import shutil
import sys
import time

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
