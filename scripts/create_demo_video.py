"""Create a narrated 1080p BrightPath assignment demonstration video."""

from __future__ import annotations

import math
import re
import shutil
import subprocess
from pathlib import Path
from textwrap import wrap

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "tmp" / "video"
OUTPUT_DIR = ROOT / "output" / "video"
OUTPUT = OUTPUT_DIR / "brightpath_tutoring_demo.mp4"
WIDTH, HEIGHT = 1920, 1080

BG_TOP = (7, 20, 38)
BG_BOTTOM = (14, 42, 67)
NAVY = (21, 52, 88)
BLUE = (54, 147, 255)
TEAL = (45, 211, 193)
PALE = (229, 242, 250)
WHITE = (247, 250, 252)
MUTED = (164, 186, 204)
GREEN = (79, 214, 140)
AMBER = (255, 194, 92)
RED = (255, 112, 122)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


F_TITLE = font(70, True)
F_H1 = font(54, True)
F_H2 = font(35, True)
F_BODY = font(29)
F_BODY_BOLD = font(29, True)
F_SMALL = font(23)
F_MONO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22) if Path("/System/Library/Fonts/Menlo.ttc").exists() else F_SMALL


def background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG_TOP)
    px = image.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = tuple(round(BG_TOP[i] * (1 - t) + BG_BOTTOM[i] * t) for i in range(3))
        for x in range(WIDTH):
            px[x, y] = color
    draw = ImageDraw.Draw(image)
    draw.ellipse((1480, -300, 2150, 370), fill=(16, 60, 91))
    draw.ellipse((-260, 760, 400, 1420), fill=(9, 50, 72))
    return image


def text_width(draw: ImageDraw.ImageDraw, text: str, use_font) -> int:
    box = draw.textbbox((0, 0), text, font=use_font)
    return box[2] - box[0]


def wrapped_lines(draw, text: str, use_font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and text_width(draw, candidate, use_font) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, xy, text, use_font, fill, max_width, line_gap=10, max_lines=None):
    x, y = xy
    lines = wrapped_lines(draw, text, use_font, max_width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".,;:") + "..."
    line_height = draw.textbbox((0, 0), "Ag", font=use_font)[3] + line_gap
    for line in lines:
        draw.text((x, y), line, font=use_font, fill=fill)
        y += line_height
    return y


def add_header(draw, title: str, subtitle: str, index: int):
    draw.rounded_rectangle((70, 55, 135, 120), radius=18, fill=TEAL)
    draw.text((91, 68), "B", font=font(35, True), fill=BG_TOP)
    draw.text((160, 51), title, font=F_H1, fill=WHITE)
    draw.text((162, 117), subtitle, font=F_SMALL, fill=MUTED)
    draw.rounded_rectangle((1712, 62, 1848, 112), radius=25, outline=BLUE, width=2)
    draw.text((1754, 72), f"{index}/8", font=F_SMALL, fill=PALE)
    draw.rectangle((70, 1018, 1850, 1024), fill=(37, 68, 92))
    draw.rectangle((70, 1018, 70 + int(1780 * index / 8), 1024), fill=TEAL)


def card(draw, box, title=None, accent=BLUE, fill=(16, 43, 68)):
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=(47, 87, 116), width=2)
    if title:
        x1, y1, _, _ = box
        draw.rounded_rectangle((x1 + 24, y1 + 20, x1 + 36, y1 + 68), radius=6, fill=accent)
        draw.text((x1 + 54, y1 + 20), title, font=F_H2, fill=WHITE)


def bullet_list(draw, items, x, y, width, accent=TEAL, gap=24):
    for item in items:
        draw.ellipse((x, y + 11, x + 14, y + 25), fill=accent)
        y = draw_wrapped(draw, (x + 34, y), item, F_BODY, PALE, width - 34, line_gap=8) + gap
    return y


def chat_bubble(draw, box, label, message, user=False):
    fill = (24, 81, 112) if user else (21, 58, 82)
    outline = BLUE if user else TEAL
    draw.rounded_rectangle(box, radius=25, fill=fill, outline=outline, width=2)
    x1, y1, x2, _ = box
    draw.text((x1 + 26, y1 + 20), label, font=F_BODY_BOLD, fill=outline)
    draw_wrapped(draw, (x1 + 26, y1 + 66), message, F_BODY, WHITE, x2 - x1 - 52, line_gap=9)


def terminal(draw, lines, box):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=24, fill=(4, 12, 23), outline=(55, 83, 105), width=2)
    for i, color in enumerate((RED, AMBER, GREEN)):
        draw.ellipse((x1 + 25 + i * 28, y1 + 22, x1 + 39 + i * 28, y1 + 36), fill=color)
    y = y1 + 66
    for line, color in lines:
        draw.text((x1 + 28, y), line, font=F_MONO, fill=color)
        y += 38


def slide_1() -> Image.Image:
    img = background(); d = ImageDraw.Draw(img)
    d.rounded_rectangle((730, 185, 1190, 645), radius=80, fill=(12, 44, 70), outline=TEAL, width=4)
    d.rounded_rectangle((855, 280, 1065, 490), radius=58, fill=TEAL)
    d.text((916, 322), "B", font=font(115, True), fill=BG_TOP)
    d.text((437, 710), "BrightPath Tutoring", font=F_TITLE, fill=WHITE)
    d.text((560, 800), "Agent-Powered Business Assistant", font=F_H2, fill=TEAL)
    d.rounded_rectangle((660, 890, 1260, 950), radius=30, fill=(19, 66, 94))
    d.text((748, 905), "C3 - Introduction to Agents", font=F_BODY, fill=PALE)
    return img


def slide_2() -> Image.Image:
    img = background(); d = ImageDraw.Draw(img); add_header(d, "Business identity", "A realistic tutoring center with complete source material", 2)
    card(d, (80, 205, 910, 940), "BrightPath at a glance")
    bullet_list(d, [
        "Private and small-group tutoring for school and university students",
        "Mathematics, physics, programming, and English",
        "Four tutor profiles, transparent prices, schedules, and policies",
        "Learn-Practice-Reflect teaching method",
    ], 125, 310, 720)
    card(d, (980, 205, 1840, 940), "Required deliverables", accent=TEAL)
    files = [
        ("about_business.pdf", "Business profile"),
        ("business_summary.txt", "Knowledge source"),
        ("business_agent.ipynb", "Main notebook"),
        ("app.py", "Gradio deployment"),
        ("requirements.txt", "Dependencies"),
    ]
    y = 310
    for name, desc in files:
        d.rounded_rectangle((1030, y, 1790, y + 84), radius=18, fill=(13, 53, 79))
        d.text((1060, y + 13), name, font=F_BODY_BOLD, fill=WHITE)
        d.text((1490, y + 19), desc, font=F_SMALL, fill=MUTED)
        y += 105
    return img


def slide_3() -> Image.Image:
    img = background(); d = ImageDraw.Draw(img); add_header(d, "Agent architecture", "Every message follows a visible, testable path", 3)
    steps = [
        ("1", "User message", "Question, enrollment interest, or feedback"),
        ("2", "Simple router", "general_question  |  lead_collection  |  feedback_unanswered"),
        ("3", "Gemini agent", "Persona + instructions + business knowledge + short-term history"),
        ("4", "Tools", "Record qualified leads and feedback through real function calls"),
        ("5", "Reflection", "Review the draft, revise if needed, and log both versions"),
    ]
    y = 205
    for idx, title, desc in steps:
        d.rounded_rectangle((150, y, 1770, y + 125), radius=28, fill=(15, 47, 73), outline=(43, 91, 122), width=2)
        d.ellipse((185, y + 27, 255, y + 97), fill=TEAL)
        d.text((210, y + 40), idx, font=F_BODY_BOLD, fill=BG_TOP)
        d.text((295, y + 20), title, font=F_H2, fill=WHITE)
        d.text((295, y + 70), desc, font=F_SMALL, fill=MUTED)
        if y < 725:
            d.polygon([(950, y + 132), (936, y + 150), (964, y + 150)], fill=BLUE)
        y += 150
    return img


def slide_4() -> Image.Image:
    img = background(); d = ImageDraw.Draw(img); add_header(d, "Live general-question route", "Gemini answers only from BrightPath's verified information", 4)
    chat_bubble(d, (120, 210, 1800, 370), "STUDENT", "What mathematics tutoring and prices do you offer for Grade 11?", user=True)
    chat_bubble(d, (120, 410, 1800, 890), "PATHY", "For Grade 11, BrightPath supports algebra, geometry, trigonometry, pre-calculus, and exam preparation. Private school-level tutoring costs USD 28 per 60-minute lesson. Small-group tutoring costs USD 16 per student, with two to four students at a similar level. Tutor availability and bookings require staff confirmation.")
    d.rounded_rectangle((1330, 918, 1800, 972), radius=26, fill=(15, 68, 78))
    d.text((1370, 928), "ROUTER: general_question", font=F_SMALL, fill=TEAL)
    return img


def slide_5() -> Image.Image:
    img = background(); d = ImageDraw.Draw(img); add_header(d, "Course recommendation", "The assistant matches the learner's level and goal", 5)
    chat_bubble(d, (100, 210, 1820, 390), "STUDENT", "I am a first-year engineering student struggling with mechanics. What should I choose?", user=True)
    card(d, (100, 440, 1820, 920), "Recommended path", accent=TEAL)
    bullet_list(d, [
        "University-level physics focused on mechanics",
        "Private tutoring for individual pacing, or a matched small group",
        "Learn-Practice-Reflect sessions with a clear next-step plan",
        "Normal price: USD 35 private or USD 20 per student in a university group",
        "Final tutor and time require staff confirmation",
    ], 165, 545, 1550, gap=18)
    return img


def slide_6() -> Image.Image:
    img = background(); d = ImageDraw.Draw(img); add_header(d, "Lead collection with a real tool call", "The model requests the tool only after name and email are available", 6)
    chat_bubble(d, (90, 200, 1830, 390), "FICTIONAL STUDENT", "My name is Maya Haddad and my email is maya.haddad@example.com. I need private Grade 11 mathematics tutoring on weekday evenings.", user=True)
    terminal(d, [
        ("[ROUTER] lead_collection", BLUE),
        ("[TOOL] record_customer_interest -> LEAD-********", GREEN),
        ("[MODEL TOOL CALL] record_customer_interest(email, message, name)", TEAL),
        ("[REFLECTION] draft and revised reply logged", AMBER),
    ], (90, 440, 1830, 690))
    d.rounded_rectangle((90, 735, 1830, 930), radius=24, fill=(16, 55, 76), outline=TEAL, width=2)
    d.text((125, 770), "Result", font=F_H2, fill=TEAL)
    draw_wrapped(d, (125, 830), "The interest is recorded for staff follow-up. The assistant does not invent a confirmed tutor, time, or booking.", F_BODY, WHITE, 1620)
    return img


def slide_7() -> Image.Image:
    img = background(); d = ImageDraw.Draw(img); add_header(d, "Feedback, unknown questions, and reflection", "Complaints are recorded; drafts are checked before sending", 7)
    chat_bubble(d, (90, 200, 1830, 355), "STUDENT", "I have a complaint: a tutor arrived late. Please record this for your staff.", user=True)
    terminal(d, [
        ("[ROUTER] feedback_unanswered", BLUE),
        ("[TOOL] record_feedback -> FDBK-********", GREEN),
        ("[MODEL TOOL CALL] record_feedback(question)", TEAL),
    ], (90, 405, 920, 650))
    card(d, (970, 405, 1830, 650), "Reflection bonus", accent=AMBER)
    draw_wrapped(d, (1025, 500), "The agent checks for invented facts, unsupported promises, and missed contact requirements. Both the original draft and revised reply are logged.", F_SMALL, PALE, 740, line_gap=10)
    chat_bubble(d, (90, 700, 1830, 925), "PATHY", "Thank you for letting us know. I recorded your feedback regarding the late tutor, and our staff can follow up with you.")
    return img


def slide_8() -> Image.Image:
    img = background(); d = ImageDraw.Draw(img); add_header(d, "End-to-end verification complete", "Ready for GitHub and assignment submission", 8)
    checks = [
        ("3 automated tests passed", "Router, tools, schemas, and offline end-to-end behavior"),
        ("Live Gemini smoke test passed", "All three routes, both tools, memory, and reflection"),
        ("Gradio HTTP 200", "Real request completed through the running chatbot interface"),
        ("PDF visually verified", "Two polished pages with no clipping or overlap"),
        ("Secrets protected", ".env and runtime records are excluded from Git"),
        ("Free-tier only", "No paid model, search tool, or paid fallback configured"),
    ]
    y = 210
    for title, desc in checks:
        d.rounded_rectangle((120, y, 1800, y + 105), radius=24, fill=(14, 49, 72), outline=(37, 89, 113), width=2)
        d.ellipse((155, y + 27, 205, y + 77), fill=GREEN)
        d.line((168, y + 53, 177, y + 63), fill=BG_TOP, width=5)
        d.line((177, y + 63, 194, y + 42), fill=BG_TOP, width=5)
        d.text((240, y + 17), title, font=F_BODY_BOLD, fill=WHITE)
        d.text((240, y + 59), desc, font=F_SMALL, fill=MUTED)
        y += 125
    d.text((555, 947), "BrightPath Tutoring - clear paths to confident learning", font=F_H2, fill=TEAL)
    return img


SLIDES = [slide_1, slide_2, slide_3, slide_4, slide_5, slide_6, slide_7, slide_8]
NARRATIONS = [
    "Welcome to BrightPath Tutoring, an agent-powered business assistant created for the C3 Introduction to Agents assignment.",
    "BrightPath is a realistic fictional tutoring center for school and university students. It offers mathematics, physics, programming, and English through private or small-group lessons. The repository contains every required business and application file.",
    "Each message moves through a clear agent workflow. A simple router selects one of three paths. Gemini receives the persona, operational instructions, business knowledge, and recent chat history. Qualified leads and feedback use real tools, and a reflection pass checks the final answer.",
    "For a general question, the agent answers only from the supplied BrightPath information. Here it correctly explains the Grade Eleven mathematics options and prices while reminding the student that tutor availability requires staff confirmation.",
    "The assistant also recommends the right tutoring path. A first-year engineering student struggling with mechanics is directed to university-level physics and can compare private tutoring with an appropriately matched small group.",
    "When a student wants to enroll, the agent collects a name, email, subject, academic level, goals, format, and schedule. After a name and valid email are available, Gemini requests the customer-interest tool. The application executes the call and records the lead without promising a confirmed booking.",
    "Complaints and questions outside the business knowledge use the feedback tool. The bonus reflection stage then reviews the draft for invented facts or unsupported promises and logs both the original and revised response.",
    "The finished project passes automated tests, a live Gemini smoke test, and a request through the Gradio interface. The business PDF was visually verified, secrets are excluded from Git, and the chatbot uses a free-tier model with no paid fallback. BrightPath is ready for submission.",
]


def audio_duration(path: Path, ffmpeg: str) -> float:
    probe = subprocess.run(
        [ffmpeg, "-i", str(path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    match = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", probe.stderr)
    if not match:
        raise RuntimeError(f"Could not determine narration duration for {path.name}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    scene_paths: list[Path] = []

    for index, (builder, narration) in enumerate(zip(SLIDES, NARRATIONS), start=1):
        slide_path = WORK / f"slide_{index:02d}.png"
        audio_path = WORK / f"narration_{index:02d}.aiff"
        scene_path = WORK / f"scene_{index:02d}.mp4"
        builder().save(slide_path, quality=95)
        run(["say", "-v", "Samantha", "-r", "172", "-o", str(audio_path), narration])
        duration = max(5.0, audio_duration(audio_path, ffmpeg) + 1.1)
        fade_out = max(0.5, duration - 0.55)
        run([
            ffmpeg, "-y", "-loop", "1", "-i", str(slide_path), "-i", str(audio_path),
            "-t", f"{duration:.3f}", "-r", "30",
            "-vf", f"scale={WIDTH}:{HEIGHT},format=yuv420p,fade=t=in:st=0:d=0.35,fade=t=out:st={fade_out:.3f}:d=0.5",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2",
            "-movflags", "+faststart", str(scene_path),
        ])
        scene_paths.append(scene_path)

    concat_file = WORK / "concat.txt"
    concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in scene_paths), encoding="utf-8")
    run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart", str(OUTPUT),
    ])
    if not OUTPUT.exists() or OUTPUT.stat().st_size < 1_000_000:
        raise RuntimeError("Video output was not created correctly")
    print(OUTPUT)
    print(f"size_bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    main()
