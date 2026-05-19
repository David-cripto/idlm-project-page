import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
GIF_OUT = ROOT / "assets" / "idlm-generation.gif"
PREVIEW_OUT = ROOT / "assets" / "idlm-generation-preview.png"

WIDTH, HEIGHT = 1920, 900
BG = "#ffffff"
TEXT = "#111111"
MUTED = "#777777"
LIGHT = "#edf0f4"
RED = "#b94a3a"
GREEN = "#168442"
BLUE = "#245d9a"

MONO_FONT = "/System/Library/Fonts/SFNSMono.ttf"
BODY_FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

TARGET_WORDS = (
    "diffusion language models generate text by iteratively refining masked "
    "tokens across long sequences until a fluent sample appears inverse "
    "distillation trains a compact student sampler to match the teacher "
    "distribution while using far fewer model calls the same target sentence "
    "can therefore be produced with lower latency and less compute which makes "
    "discrete diffusion generation more practical for interactive applications "
    "long context experiments and fast research prototyping without changing "
    "the output quality"
).split()

ROWS = 8
COLS = 9
SEQUENCE_LENGTH = ROWS * COLS
DLM_TOTAL_CALLS = 64
IDLM_TOTAL_CALLS = 4
DLM_CALLS = [0, 8, 16, 24, 32, 40, 48, 56, 64]
IDLM_CALLS = [0, 1, 2, 3, 4, 4, 4, 4, 4]
DURATIONS = [350, 350, 350, 450, 650, 550, 550, 650, 1200]


def font(path, size):
    return ImageFont.truetype(path, size)


TITLE = font(BOLD_FONT, 32)
HEADER = font(MONO_FONT, 30)
COUNTER = font(MONO_FONT, 26)
WORD = font(MONO_FONT, 24)
SMALL = font(BODY_FONT, 21)
SMALL_BOLD = font(BOLD_FONT, 21)
CALLOUT = font(BOLD_FONT, 24)


class FitTracker:
    def __init__(self):
        self.violations = []

    def check(self, label, box, bounds):
        x1, y1, x2, y2 = box
        bx1, by1, bx2, by2 = bounds
        if x1 < bx1 or y1 < by1 or x2 > bx2 or y2 > by2:
            self.violations.append((label, box, bounds))


def text_box(draw, xy, text, fnt):
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=fnt)
    return bbox


def draw_text(draw, xy, text, fill, fnt, tracker=None, bounds=None, label=None):
    draw.text(xy, text, fill=fill, font=fnt)
    if tracker and bounds:
        tracker.check(label or text, text_box(draw, xy, text, fnt), bounds)


def draw_center(draw, y, text, fill, fnt, tracker=None):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = (WIDTH - (bbox[2] - bbox[0])) / 2
    draw_text(draw, (x, y), text, fill, fnt, tracker, (0, 0, WIDTH, HEIGHT), text)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def mask_for(word):
    return "-" * max(2, len(word))


REVEAL_ORDER = list(range(SEQUENCE_LENGTH))
random.Random(7).shuffle(REVEAL_ORDER)


def visible_indices(call_count, total_calls):
    if call_count <= 0:
        return set()
    if call_count >= total_calls:
        return set(range(SEQUENCE_LENGTH))
    n_visible = round(SEQUENCE_LENGTH * call_count / total_calls)
    return set(REVEAL_ORDER[:n_visible])


def draw_word_grid(draw, top, visible, tracker, strip_bounds):
    left = 50
    col_w = (WIDTH - 100) / COLS
    row_h = 33
    for index, word in enumerate(TARGET_WORDS):
        row = index // COLS
        col = index % COLS
        x = left + col * col_w
        y = top + row * row_h
        if index in visible:
            text = word
            color = TEXT
        else:
            text = mask_for(word)
            color = TEXT
        draw_text(draw, (x, y), text, color, WORD, tracker, (x, y, x + col_w - 18, y + row_h), f"word:{index}:{text}")


def draw_status(draw, y, calls, total, color, done_label, active_label, tracker):
    progress_left = 50
    progress_top = y
    progress_width = 500
    rounded(draw, (progress_left, progress_top, progress_left + progress_width, progress_top + 12), 6, LIGHT)
    fill_width = max(0, int(progress_width * calls / total))
    if fill_width:
        rounded(draw, (progress_left, progress_top, progress_left + fill_width, progress_top + 12), 6, color)

    label = done_label if calls == total else active_label
    label_color = GREEN if calls == total else MUTED
    draw_text(draw, (progress_left + progress_width + 28, progress_top - 8), label, label_color, SMALL_BOLD, tracker, (0, 0, WIDTH, HEIGHT), label)


def draw_strip(draw, title, y, calls, total, color, tracker):
    strip_bounds = (0, y, WIDTH, y + 395)
    header_y = y + 8
    grid_top = y + 92

    draw_center(draw, header_y, title, TEXT, HEADER, tracker)
    step = f"Sampling step: {calls:02d}/{total}" if total >= 10 else f"Sampling step: {calls}/{total}"
    draw_text(draw, (WIDTH - 450, header_y), step, MUTED, COUNTER, tracker, strip_bounds, step)

    draw_word_grid(draw, grid_top, visible_indices(calls, total), tracker, strip_bounds)
    if title == "IDLM":
        draw_status(draw, y + 360, calls, total, color, "DONE: final output", "few-step distilled sampling", tracker)
    else:
        draw_status(draw, y + 360, calls, total, color, "DONE: final output", "long reverse denoising chain", tracker)


def draw_callout(draw, frame, tracker):
    idlm_done = IDLM_CALLS[frame] == IDLM_TOTAL_CALLS
    dlm_done = DLM_CALLS[frame] == DLM_TOTAL_CALLS
    if idlm_done and not dlm_done:
        text = "IDLM has already completed while the DLM is still sampling"
        color = GREEN
    else:
        text = "Same generation task; only the number of sampling calls changes"
        color = TEXT

    box = (410, 810, 1510, 870)
    rounded(draw, box, 30, "#f8fafc", "#d8dfe8", 2)
    bbox = draw.textbbox((0, 0), text, font=CALLOUT)
    x = (WIDTH - (bbox[2] - bbox[0])) / 2
    draw_text(draw, (x, 827), text, color, CALLOUT, tracker, box, "callout")


def draw_frame(frame):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    tracker = FitTracker()

    draw_strip(draw, "Diffusion Language Model", 15, DLM_CALLS[frame], DLM_TOTAL_CALLS, RED, tracker)
    draw.line((50, 425, WIDTH - 50, 425), fill="#d8d8d8", width=2)
    draw_strip(draw, "IDLM", 435, IDLM_CALLS[frame], IDLM_TOTAL_CALLS, GREEN, tracker)
    draw_callout(draw, frame, tracker)
    return image, tracker


def make_contact_sheet(frames):
    thumb_w, thumb_h = 640, 300
    sheet = Image.new("RGB", (thumb_w * 3, thumb_h * 3), "#ffffff")
    for index, frame in enumerate(frames):
        thumb = frame.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        x = (index % 3) * thumb_w
        y = (index // 3) * thumb_h
        sheet.paste(thumb, (x, y))
    return sheet


def evaluate(trackers):
    violations = [item for tracker in trackers for item in tracker.violations]
    idlm_finish = next(i for i, calls in enumerate(IDLM_CALLS) if calls == IDLM_TOTAL_CALLS)
    dlm_finish = next(i for i, calls in enumerate(DLM_CALLS) if calls == DLM_TOTAL_CALLS)
    return {
        "sequence_length": SEQUENCE_LENGTH,
        "sequence_length_gt_64": SEQUENCE_LENGTH > 64,
        "same_target_text": True,
        "dlm_total_calls": DLM_TOTAL_CALLS,
        "idlm_total_calls": IDLM_TOTAL_CALLS,
        "idlm_finishes_before_dlm": idlm_finish < dlm_finish,
        "frames_with_idlm_done_and_dlm_incomplete": sum(
            1 for i in range(len(DLM_CALLS)) if IDLM_CALLS[i] == IDLM_TOTAL_CALLS and DLM_CALLS[i] < DLM_TOTAL_CALLS
        ),
        "text_box_violations": len(violations),
        "dimensions": f"{WIDTH}x{HEIGHT}",
    }, violations


def main():
    assert len(TARGET_WORDS) == SEQUENCE_LENGTH
    rendered = [draw_frame(index) for index in range(len(DLM_CALLS))]
    frames = [item[0] for item in rendered]
    trackers = [item[1] for item in rendered]
    checks, violations = evaluate(trackers)

    GIF_OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        GIF_OUT,
        save_all=True,
        append_images=frames[1:],
        duration=DURATIONS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    make_contact_sheet(frames).save(PREVIEW_OUT)

    size_kb = GIF_OUT.stat().st_size / 1024
    checks["gif_size_kb"] = round(size_kb, 1)
    checks["gif_size_under_1000kb"] = size_kb < 1000

    print(f"wrote {GIF_OUT}")
    print(f"wrote {PREVIEW_OUT}")
    for key, value in checks.items():
        print(f"{key}: {value}")
    if violations:
        print("violations:")
        for label, box, bounds in violations[:12]:
            print(f"- {label}: {box} outside {bounds}")


if __name__ == "__main__":
    main()
