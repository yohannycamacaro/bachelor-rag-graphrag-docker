from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "category_comparison_chart.png"

W, H = 1600, 960
MARGIN_X = 110
TOP = 170
BOTTOM = 820
BAR_H = 26
GAP = 34

COLORS = {
    "bg": "#f7f9fc",
    "ink": "#102033",
    "muted": "#536579",
    "grid": "#dce5ef",
    "classic": "#0b5fa5",
    "graph": "#6b46c1",
    "positive": "#2f855a",
    "panel": "#ffffff",
    "line": "#cbd8e6",
}


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
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


FONT_TITLE = load_font(42, True)
FONT_SUBTITLE = load_font(23)
FONT_LABEL = load_font(22, True)
FONT_SMALL = load_font(18)
FONT_NUM = load_font(19, True)


def latest_category_csv() -> Path:
    paths = sorted(
        RESULTS_DIR.glob("category_comparison_*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not paths:
        raise FileNotFoundError("No category_comparison_*.csv file found.")
    return paths[0]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    order = {
        "Relationale Troubleshooting-Frage": 0,
        "Nachvollziehbarkeit": 1,
        "Multi-Hop-Frage": 2,
        "Einfache Faktenfrage": 3,
        "Konfigurationskonflikt": 4,
        "Prozedurale Frage": 5,
    }
    return sorted(rows, key=lambda row: order.get(row["category_label"], 99))


def draw_legend(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rounded_rectangle((x, y, x + 24, y + 24), radius=6, fill=COLORS["classic"])
    draw.text((x + 34, y - 1), "Klassisches RAG", font=FONT_SMALL, fill=COLORS["ink"])
    draw.rounded_rectangle((x + 245, y, x + 269, y + 24), radius=6, fill=COLORS["graph"])
    draw.text((x + 279, y - 1), "GraphRAG", font=FONT_SMALL, fill=COLORS["ink"])


def draw() -> None:
    source = latest_category_csv()
    rows = read_rows(source)

    image = Image.new("RGB", (W, H), COLORS["bg"])
    canvas = ImageDraw.Draw(image)

    canvas.text((80, 58), "Voranalyse nach Fragekategorien", font=FONT_TITLE, fill=COLORS["ink"])
    canvas.text(
        (80, 112),
        "Keyword-Abdeckung: klassisches RAG vs GraphRAG, Datensatz mit 48 Fragen",
        font=FONT_SUBTITLE,
        fill=COLORS["muted"],
    )
    draw_legend(canvas, 1040, 78)

    plot_x = 610
    plot_w = 760
    axis_y = BOTTOM

    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        x = plot_x + int(plot_w * tick)
        canvas.line((x, TOP - 20, x, BOTTOM + 18), fill=COLORS["grid"], width=2)
        label = f"{tick:.2f}".replace(".", ",")
        canvas.text((x - 22, BOTTOM + 34), label, font=FONT_SMALL, fill=COLORS["muted"])

    canvas.line((plot_x, axis_y, plot_x + plot_w, axis_y), fill=COLORS["line"], width=3)

    y = TOP
    for row in rows:
        label = row["category_label"]
        classic = float(row["classic_keyword_coverage"])
        graph = float(row["graph_keyword_coverage"])
        delta = float(row["keyword_delta_graph_minus_classic"])

        canvas.text((MARGIN_X, y + 8), label, font=FONT_LABEL, fill=COLORS["ink"])
        canvas.text((MARGIN_X, y + 38), f"n={row['question_count']} | Ø Hops={float(row['avg_expected_relation_hops']):.2f}", font=FONT_SMALL, fill=COLORS["muted"])

        classic_w = int(plot_w * classic)
        graph_w = int(plot_w * graph)

        canvas.rounded_rectangle(
            (plot_x, y + 4, plot_x + classic_w, y + 4 + BAR_H),
            radius=8,
            fill=COLORS["classic"],
        )
        canvas.rounded_rectangle(
            (plot_x, y + 42, plot_x + graph_w, y + 42 + BAR_H),
            radius=8,
            fill=COLORS["graph"],
        )
        canvas.text((plot_x + classic_w + 12, y + 3), f"{classic:.3f}".replace(".", ","), font=FONT_NUM, fill=COLORS["classic"])
        canvas.text((plot_x + graph_w + 12, y + 41), f"{graph:.3f}".replace(".", ","), font=FONT_NUM, fill=COLORS["graph"])
        canvas.text((1390, y + 22), f"Delta {delta:+.3f}".replace(".", ","), font=FONT_NUM, fill=COLORS["positive"])
        y += 100

    note = (
        "Hinweis: Die Werte sind eine retrieval-basierte Voranalyse. "
        "Die finale Arbeit ergaenzt manuelle Bewertungen fuer Korrektheit, "
        "Vollstaendigkeit, Nachvollziehbarkeit und Konsistenz."
    )
    canvas.rounded_rectangle((80, 860, 1520, 920), radius=16, fill=COLORS["panel"], outline=COLORS["line"], width=2)
    canvas.text((110, 878), note, font=FONT_SMALL, fill=COLORS["muted"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT_PATH, quality=95)
    print(f"Chart written to: {OUTPUT_PATH}")
    print(f"Source CSV: {source}")


if __name__ == "__main__":
    draw()
