from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "docs" / "prototype_mindmap_rag_graphrag.png"

W, H = 1920, 1080

COLORS = {
    "bg": "#f6f8fb",
    "grid": "#e8edf4",
    "ink": "#102033",
    "muted": "#516173",
    "blue": "#0b5fa5",
    "blue_dark": "#083c6e",
    "cyan": "#0097b2",
    "green": "#2f855a",
    "orange": "#b7791f",
    "red": "#c6403a",
    "purple": "#6b46c1",
    "white": "#ffffff",
    "shadow": "#c7d1de",
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = [
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = load_font(44, True)
FONT_SUBTITLE = load_font(24)
FONT_CARD_TITLE = load_font(27, True)
FONT_BODY = load_font(22)
FONT_SMALL = load_font(18)
FONT_TINY = load_font(16)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    line_gap: int = 8,
) -> None:
    lines = text.split("\n")
    heights = [text_size(draw, line, font)[1] for line in lines]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total_h) / 2
    for line, line_h in zip(lines, heights):
        line_w, _ = text_size(draw, line, font)
        x = box[0] + (box[2] - box[0] - line_w) / 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h + line_gap


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            candidate = word if not line else f"{line} {word}"
            if text_size(draw, candidate, font)[0] <= max_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    outline: str,
    radius: int = 22,
    shadow: bool = True,
) -> None:
    if shadow:
        sx1, sy1, sx2, sy2 = box[0] + 8, box[1] + 10, box[2] + 8, box[3] + 10
        draw.rounded_rectangle((sx1, sy1, sx2, sy2), radius=radius, fill=COLORS["shadow"])
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=3)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str,
    width: int = 5,
) -> None:
    draw.line([start, end], fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    head_len = 18
    spread = math.pi / 7
    points = [
        end,
        (
            int(end[0] - head_len * math.cos(angle - spread)),
            int(end[1] - head_len * math.sin(angle - spread)),
        ),
        (
            int(end[0] - head_len * math.cos(angle + spread)),
            int(end[1] - head_len * math.sin(angle + spread)),
        ),
    ]
    draw.polygon(points, fill=color)


def draw_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    body: str,
    accent: str,
) -> None:
    rounded_box(draw, box, COLORS["white"], "#d6e0ec")
    draw.rounded_rectangle((box[0], box[1], box[0] + 14, box[3]), radius=8, fill=accent)
    x = box[0] + 36
    y = box[1] + 26
    draw.text((x, y), title, font=FONT_CARD_TITLE, fill=COLORS["ink"])
    y += 44
    for line in wrap_text(draw, body, FONT_BODY, box[2] - box[0] - 72):
        draw.text((x, y), line, font=FONT_BODY, fill=COLORS["muted"])
        y += 31


def draw_flow(
    draw: ImageDraw.ImageDraw,
    y: int,
    x1: int,
    labels: list[str],
    color: str,
) -> None:
    box_w = 158
    gap = 34
    x = x1
    for i, label in enumerate(labels):
        box = (x, y, x + box_w, y + 58)
        rounded_box(draw, box, "#fbfdff", color, radius=14, shadow=False)
        draw_centered_text(draw, box, label, FONT_SMALL, COLORS["ink"], line_gap=2)
        if i < len(labels) - 1:
            arrow(draw, (x + box_w + 4, y + 29), (x + box_w + gap - 6, y + 29), color, width=3)
        x += box_w + gap


def main() -> None:
    image = Image.new("RGB", (W, H), COLORS["bg"])
    draw = ImageDraw.Draw(image)

    for x in range(0, W, 80):
        draw.line((x, 0, x, H), fill=COLORS["grid"], width=1)
    for y in range(0, H, 80):
        draw.line((0, y, W, y), fill=COLORS["grid"], width=1)

    draw.text((80, 48), "Prototyp der Bachelorarbeit", font=FONT_TITLE, fill=COLORS["ink"])
    draw.text(
        (80, 105),
        "Classic RAG vs GraphRAG fuer technische Docker-Compose-Troubleshooting-Fragen",
        font=FONT_SUBTITLE,
        fill=COLORS["muted"],
    )

    center = (650, 385, 1270, 655)
    rounded_box(draw, center, COLORS["blue_dark"], COLORS["blue_dark"], radius=26)
    draw_centered_text(
        draw,
        (center[0] + 30, center[1] + 30, center[2] - 30, center[3] - 30),
        "Forschungsfrage\nWann verbessert GraphRAG die\nAntwortqualitaet gegenueber\nklassischem RAG?",
        FONT_CARD_TITLE,
        COLORS["white"],
        line_gap=12,
    )

    cards = {
        "problem": (80, 210, 560, 390),
        "classic": (80, 515, 610, 755),
        "data": (700, 180, 1220, 335),
        "graph": (1310, 515, 1840, 755),
        "eval": (710, 735, 1210, 945),
        "result": (1320, 210, 1840, 390),
    }

    draw_card(
        draw,
        cards["problem"],
        "Problem",
        "Troubleshooting-Fragen brauchen oft Beziehungen: Problem, Komponente, Ursache, Diagnose und Loesung.",
        COLORS["red"],
    )
    draw_card(
        draw,
        cards["data"],
        "Datenbasis",
        "12 Docker-Quellen, 23 kontrollierte Support-Faelle und 48 Testfragen.",
        COLORS["cyan"],
    )
    draw_card(
        draw,
        cards["result"],
        "Hypothese",
        "GraphRAG hilft besonders bei relationalen, Multi-Hop- und Nachvollziehbarkeitsfragen.",
        COLORS["green"],
    )
    draw_card(
        draw,
        cards["classic"],
        "Variante A: Klassisches RAG",
        "Dokumente werden als Textabschnitte gesucht. Gut fuer direkte Fakten und klare Schritte.",
        COLORS["blue"],
    )
    draw_flow(draw, 665, 125, ["Dokumente", "Chunks", "Retrieval"], COLORS["blue"])

    draw_card(
        draw,
        cards["graph"],
        "Variante B: GraphRAG",
        "Knoten und Beziehungen machen technische Antwortpfade sichtbar.",
        COLORS["purple"],
    )
    draw_flow(draw, 665, 1355, ["Problem", "Ursache", "Loesung"], COLORS["purple"])

    draw_card(
        draw,
        cards["eval"],
        "Evaluation",
        "Korrektheit, Vollstaendigkeit, Nachvollziehbarkeit und Konsistenz pro Fragekategorie.",
        COLORS["orange"],
    )

    arrow(draw, (560, 300), (650, 455), COLORS["red"])
    arrow(draw, (960, 335), (960, 385), COLORS["cyan"])
    arrow(draw, (1320, 300), (1270, 455), COLORS["green"])
    arrow(draw, (610, 635), (650, 560), COLORS["blue"])
    arrow(draw, (1310, 635), (1270, 560), COLORS["purple"])
    arrow(draw, (960, 735), (960, 655), COLORS["orange"])

    footer_box = (245, 980, 1675, 1035)
    draw.rounded_rectangle(footer_box, radius=18, fill="#eaf3fb", outline="#c9dff0", width=2)
    draw_centered_text(
        draw,
        footer_box,
        "Ziel: differenziert zeigen, bei welchen technischen Fragen GraphRAG wirklich Mehrwert bringt.",
        FONT_BODY,
        COLORS["blue_dark"],
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT_PATH, quality=95)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
