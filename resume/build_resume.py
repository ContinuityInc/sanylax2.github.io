#!/usr/bin/env python3
"""Generate Santosh_Lakshman_Resume.pdf.

Usage:  python3 resume/build_resume.py
Deps:   pip install reportlab

Fonts (Poppins + Font Awesome 5) are downloaded into resume/.fonts/ on
first run; that directory is git-ignored.
"""
from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

from reportlab.lib.colors import HexColor, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Santosh_Lakshman_Resume.pdf"
FONT_DIR = Path(__file__).resolve().parent / ".fonts"

FONTS = {
    "Poppins": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
    "Poppins-Bold": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
    "FA-Solid": "https://github.com/FortAwesome/Font-Awesome/raw/5.15.4/webfonts/fa-solid-900.ttf",
    "FA-Brands": "https://github.com/FortAwesome/Font-Awesome/raw/5.15.4/webfonts/fa-brands-400.ttf",
}

# Layout constants measured from the previous hand-made PDF.
PAGE_W, PAGE_H = 612, 792
MARGIN_L, MARGIN_R = 28.8, 28.8
TEXT_W = PAGE_W - MARGIN_L - MARGIN_R
BLUE = HexColor("#3644c2")
BODY = 9.96
SECTION = 11.96
NAME = 24.79
LINE = 12.0
BULLET_LINE = 12.55
BULLET_X, BULLET_TEXT_X = MARGIN_L + 4.5, MARGIN_L + 14.9
SQUEEZE_PT = 6.0  # max overflow we absorb by tightening word spacing on a one-line bullet
SECTION_GAP = 5.0  # extra space above a section title (on top of the preceding line advance)

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------
CONTACT = [
    ("FA-Solid", "\uf0e0", "sanylax01@gmail.com"),
    ("FA-Solid", "\uf095", "408-805-2164"),
    ("FA-Brands", "\uf08c", "linkedin.com/in/sanylax"),
    ("FA-Brands", "\uf09b", "github.com/sanylax2"),
    ("FA-Solid", "\uf3c5", "San Jose, CA"),
    (None, None, "US Citizen"),
]

EDUCATION = {
    "school": "University of California, Santa Cruz",
    "degree": "Computer Science B.S.",
    "date": "March 2023",
    "right": "GPA: 4.0",
    "lines": [
        ("Coursework:", "Algorithms & Data Structures, Operating Systems, Databases, Networking, "
                        "Machine Learning, Full-Stack Web Development"),
        ("Organizations:", "Google Developer Group, Alpha Kappa Psi (Business Fraternity)"),
    ],
}

EXPERIENCE = [
    {
        "org": "Traba ( Money )",
        "title": "Software Engineer II",
        "date": "Mar 2026 - Present",
        "loc": "New York, NY",
        "tech": "TypeScript, GCP, Stripe, Zeal",
        "bullets": [
            "Enabled Instant Pay for W2 workers, extending earned wage access to all 400K+ workers on the platform",
            "Rebuilt the Clearing House from scratch, improving reliability for ~$400K/week in payment volume",
            "Built unified billing contacts with role-based permissions for 20K+ contacts across thousands of clients",
            "Integrated Zeal and Stripe APIs to streamline payroll disbursement, saving $1M+ annually",
        ],
    },
    {
        "org": "Amazon ( UnifiedAuth )",
        "title": "Software Development Engineer",
        "date": "Nov 2023 - Mar 2026",
        "loc": "New York, NY - San Jose, CA - Remote",
        "tech": "Java, Kotlin, JavaScript, AWS",
        "bullets": [
            "Designed and implemented a telemetry system which assisted 300K+ services migrate legacy dependencies",
            "Created Data Pipeline which ingested, aggregated, and displayed the telemetry data to 15K+ service owners",
            "Made improvements to OAuth-based network authentication protocol which reduced memory usage by 32%",
        ],
    },
    {
        "org": "Amazon ( UnifiedAuth )",
        "title": "Software Development Engineer Intern",
        "date": "Jun 2022 - Sep 2022",
        "loc": "New York, NY - Remote",
        "tech": "Python, Scala, AWS, Spark SQL",
        "bullets": [
            "Built an AWS dashboard that collected, aggregated, and displayed critical business metrics",
            "Generated insights which helped improve Amazon\u2019s security posture across 50K internal services",
            "Saved 10 Developer hours per week spent on collecting metrics and assisted in reprioritizing team goals",
        ],
    },
    {
        "org": "Sage ( Social Media Startup )",
        "title": "Software Developer Intern ( NLP )",
        "date": "Jun 2021 - Sep 2021",
        "loc": "San Jose, CA - Remote",
        "tech": "Python, R, SQL, NLTK",
        "bullets": [
            "Developed an NLP model that matches new questions with field experts, driving 10,000 MAU organically",
            "Evaluated supervised learning methods (Random Forests, K-Nearest-Neighbor) and vectorization methods "
            "(Count, N-Grams, TF-IDF) using scikit-learn, NLTK, numpy, and pandas",
        ],
    },
    {
        "org": "University of California, Santa Cruz",
        "title": "Academic Tutor ( CS & Math )",
        "date": "Apr 2020 - Jun 2021",
        "loc": "Santa Cruz, CA - Remote",
        "tech": "C++, Python, Java",
        "bullets": [
            "Tutored students in data structures, algorithms, and calculus through projects, homework, and labs",
        ],
    },
]

PROJECTS = [
    {
        "name": "SayV - Android Application",
        "tech": "Java, Node.js, Firebase, Android, iOS, Wifi-Direct, Bluetooth",
        "bullets": [
            "Built a P2P community-based panic button alarm and notification network for mobile that works offline",
            "Won Top 20 App and cash prize at Los Altos Hacks, one of the largest Silicon Valley hackathons",
        ],
    },
    {
        "name": "CanvasCal - Status Bar App",
        "tech": "Python, Google Calendar API, Canvas REST API",
        "bullets": [
            "Synced Canvas assignments and schedules to Google Calendar with automated reminders and tracking",
        ],
    },
]

SKILLS = [
    ("Languages:", "Java, Kotlin, Python, C/C++, JavaScript, TypeScript, Scala, SQL, HTML/CSS, Bash"),
    ("Tools:", "AWS (CDK, EC2, ECS Fargate, Lambda, S3, IAM, CloudWatch), GCP, Git, Linux, Docker, Kubernetes, "
               "PostgreSQL, Stripe"),
    ("Libraries/Frameworks:", "React, TanStack, Vite, Spring, Node, Express, Auth0, scikit-learn, numpy, pandas"),
]


# --------------------------------------------------------------------------
# Rendering helpers
# --------------------------------------------------------------------------
def ensure_fonts() -> None:
    FONT_DIR.mkdir(exist_ok=True)
    for name, url in FONTS.items():
        path = FONT_DIR / f"{name}.ttf"
        if not path.exists():
            print(f"downloading {name} ...", file=sys.stderr)
            urllib.request.urlretrieve(url, path)
        pdfmetrics.registerFont(TTFont(name, str(path)))


def width(text: str, font: str, size: float = BODY) -> float:
    return pdfmetrics.stringWidth(text, font, size)


def wrap(text: str, font: str, max_w: float, size: float = BODY) -> list[str]:
    """Greedy word wrap; never splits inside a word (so no 'Full-' / 'Stack' breaks)."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if width(trial, font, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Doc:
    def __init__(self, c: canvas.Canvas):
        self.c = c
        self.y = PAGE_H - 30.9  # baseline of the name

    def text(self, x: float, s: str, font: str = "Poppins", size: float = BODY, color=black) -> float:
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawString(x, self.y, s)
        return x + width(s, font, size)

    def right_text(self, s: str, font: str = "Poppins-Bold") -> None:
        self.c.setFont(font, BODY)
        self.c.setFillColor(black)
        self.c.drawRightString(PAGE_W - MARGIN_R, self.y, s)

    def down(self, dy: float) -> None:
        self.y -= dy

    def section(self, title: str) -> None:
        self.down(SECTION_GAP)
        self.text(MARGIN_L, title, "Poppins-Bold", SECTION, BLUE)
        self.down(17.6)

    def labeled(self, label: str, body: str, label_font: str = "Poppins-Bold") -> None:
        x = self.text(MARGIN_L, label, label_font) + 3.6
        # First line shares the row with the label; continuation lines use the full width.
        first_line, *rest = wrap(body, "Poppins", PAGE_W - MARGIN_R - x)
        self.text(x, first_line)
        self.down(LINE)
        for line in wrap(" ".join(rest), "Poppins", TEXT_W) if rest else []:
            self.text(MARGIN_L, line)
            self.down(LINE)

    def bullets(self, items: list[str]) -> None:
        max_w = PAGE_W - MARGIN_R - BULLET_TEXT_X
        for item in items:
            self.text(BULLET_X, "-")
            over = width(item, "Poppins") - max_w
            if 0 < over <= SQUEEZE_PT:
                # Tighten inter-word spacing slightly instead of orphaning one word on a new line.
                self.c.setFont("Poppins", BODY)
                self.c.setFillColor(black)
                self.c.drawString(BULLET_TEXT_X, self.y, item, wordSpace=-over / item.count(" "))
                self.down(BULLET_LINE)
                continue
            lines = wrap(item, "Poppins", max_w)
            for i, line in enumerate(lines):
                self.text(BULLET_TEXT_X, line)
                self.down(BULLET_LINE if i == len(lines) - 1 else LINE)

    def entry_header(self, left_bold: str, right_bold: str | None, title: str | None = None) -> None:
        x = self.text(MARGIN_L, left_bold, "Poppins-Bold")
        if title:
            self.text(x + 10.0, title, "Poppins-Bold")
        if right_bold:
            self.right_text(right_bold)
        self.down(LINE)

    def meta_line(self, date: str, loc: str | None, tech: str | None, right_regular: str | None = None) -> None:
        x = self.text(MARGIN_L, date)
        if loc:
            self.text(x + 19.9, loc)
        if tech:
            self.right_text(tech)
        if right_regular:
            self.right_text(right_regular, "Poppins")
        self.down(LINE)


def draw_contact(d: Doc) -> None:
    """Icon + text pairs separated by 12pt; wraps to a second line if needed."""
    gap, icon_gap = 12.0, 3.1
    x = MARGIN_L
    first = True
    for icon_font, icon, label in CONTACT:
        parts_w = (width(icon, icon_font) + icon_gap if icon else 0) + width(label, "Poppins-Bold")
        sep = "  \u00b7  " if icon is None else ""
        sep_w = width(sep, "Poppins-Bold")
        if not first and x + sep_w + parts_w > PAGE_W - MARGIN_R:
            d.down(LINE)
            x, first = MARGIN_L, True
        if not first:
            x = d.text(x, sep, "Poppins-Bold") if sep else x + gap
        if icon:
            d.c.setFont(icon_font, BODY)
            d.c.setFillColor(black)
            d.c.drawString(x, d.y - 1.7, icon)
            x += width(icon, icon_font) + icon_gap
        x = d.text(x, label, "Poppins-Bold")
        first = False
    d.down(LINE)


def build() -> None:
    ensure_fonts()
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Santosh Lakshman - Resume")
    c.setAuthor("Santosh Lakshman")
    d = Doc(c)

    d.text(MARGIN_L, "Santosh Lakshman", "Poppins-Bold", NAME, BLUE)
    d.down(35.6)
    draw_contact(d)

    d.section("Education")
    d.entry_header(EDUCATION["school"], None, EDUCATION["degree"])
    d.meta_line(EDUCATION["date"], None, None, right_regular=EDUCATION["right"])
    for label, body in EDUCATION["lines"]:
        d.labeled(label, body)

    d.section("Experience")
    for i, job in enumerate(EXPERIENCE):
        if i:
            d.down(2.4)
        d.entry_header(job["org"], None, job["title"])
        d.meta_line(job["date"], job["loc"], job["tech"])
        d.bullets(job["bullets"])

    d.section("Projects")
    for i, p in enumerate(PROJECTS):
        if i:
            d.down(2.4)
        d.entry_header(p["name"], p["tech"])
        d.bullets(p["bullets"])

    d.section("Skills")
    for label, body in SKILLS:
        d.labeled(label, body, label_font="Poppins")
        d.down(1.0)

    if d.y < 20:
        raise SystemExit(f"content overflowed the page by {20 - d.y:.1f}pt")
    c.showPage()
    c.save()
    print(f"wrote {OUT.relative_to(ROOT)} (bottom margin {d.y:.1f}pt)")


if __name__ == "__main__":
    os.chdir(ROOT)
    build()
