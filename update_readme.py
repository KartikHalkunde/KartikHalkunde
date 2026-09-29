"""Generates a colored, fastfetch-style profile card as SVG (dark + light).

Output: assets/fastfetch-dark.svg and assets/fastfetch-light.svg
Optional: put your own ASCII art in a file called ascii.txt next to this script.
"""
import os, json, urllib.request
from datetime import date, datetime, timedelta
from itertools import zip_longest
from pathlib import Path
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

USER = "KartikHalkunde"
DOB = date(2005, 9, 26)
W = 62      # width (in characters) of the info column
GAP = 3     # spaces between ASCII art and info column

# ---- SVG look ----
FONT_SIZE = 14
LINE_H = 20
CHAR_W = 8.6            # slightly wider than real glyphs so text never clips
PAD_X, PAD_Y = 28, 26
FONT = "'SFMono-Regular','Consolas','Liberation Mono','Menlo','DejaVu Sans Mono',monospace"

THEMES = {
    "dark": dict(bg="#161b22", border="#30363d", fg="#c9d1d9",
                 muted="#6e7681", label="#ffa657", value="#79c0ff"),
    "light": dict(bg="#f6f8fa", border="#d0d7de", fg="#24292f",
                  muted="#8c959f", label="#bc4c00", value="#0550ae"),
}

DEFAULT_ART = [
    r"     .--.     ",
    r"    |o_o |    ",
    r"    |:_/ |    ",
    r"   //   \ \   ",
    r"  (|     | )  ",
    r" /'\_   _/`\  ",
    r" \___)=(___/  ",
]


def load_art():
    p = Path("ascii.txt")
    if p.exists():
        lines = [l.expandtabs(4).rstrip() for l in p.read_text(encoding="utf-8").splitlines()]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if lines:
            return lines
    return DEFAULT_ART


def today_ist():
    # GitHub runners use UTC; use IST so the uptime rolls over at local midnight
    return datetime.now(ZoneInfo("Asia/Kolkata")).date()


def uptime(today):
    y = today.year - DOB.year
    m = today.month - DOB.month
    d = today.day - DOB.day
    if d < 0:
        m -= 1
        d += (today.replace(day=1) - timedelta(days=1)).day
    if m < 0:
        y -= 1
        m += 12
    return f"{y} years, {m} months, {d} days"


def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def stats():
    u = api(f"/users/{USER}")
    stars, page = 0, 1
    while True:
        repos = api(f"/users/{USER}/repos?per_page=100&page={page}")
        if not repos:
            break
        stars += sum(r["stargazers_count"] for r in repos)
        page += 1
    commits = api(f"/search/commits?q=author:{USER}")["total_count"]
    return u["public_repos"], stars, u["followers"], commits


# ---- line builders: each returns a list of (text, color_role) segments ----
def row(label, value):
    dots = max(W - 5 - len(label) - len(value), 3)
    return [(". ", "muted"), (label + ":", "label"),
            (" " + "." * dots + " ", "muted"), (value, "value")]


def head(title):
    return [(f"- {title} " + "-" * max(W - len(title) - 3, 3), "fg")]


def pair(l1, v1, l2, v2):
    wl = (W - 3) // 2
    wr = W - 3 - wl
    d1 = max(wl - 5 - len(l1) - len(v1), 3)
    d2 = max(wr - 3 - len(l2) - len(v2), 3)
    return [(". ", "muted"), (l1 + ":", "label"), (" " + "." * d1 + " ", "muted"),
            (v1, "value"), (" | ", "muted"),
            (l2 + ":", "label"), (" " + "." * d2 + " ", "muted"), (v2, "value")]


def build_info():
    repos, stars, followers, commits = stats()
    return [
        head(f"{USER}@github"),
        row("OS", "Windows 11, Fedora Linux"),
        row("Uptime", uptime(today_ist())),
        row("Host", "Student @ Vidyavardhini College Of Enggineering"), 
        row("IDE", "VSCode, IntelliJ"),
        [(".", "muted")],
        row("Languages.Programming", "Java, Python, JS, C"),
        row("Languages.Computer", "HTML, CSS, JSON, LaTeX, YAML"),
        row("Languages.Real", "English, Hindi, Marathi"),
        [(".", "muted")],
        row("Hobbies.Software", "Minecraft Modding, iOS Jailbreaking"),
        row("Hobbies.Hardware", "Painting, Music"),
        [],
        head("Contact"),
        row("Email.Personal", "kartikhalkunde26@gmail.com"),
        row("Email.Work", "kartikhalkunde@proton.me"),
        row("LinkedIn", "https://www.linkedin.com/in/kartikhalkunde/"),
        row("LeetCode", "https://leetcode.com/u/KartikHalkunde/"),
        [],
        head("GitHub Stats"),
        pair("Repos", str(repos), "Stars", str(stars)),
        pair("Commits", f"{commits:,}", "Followers", str(followers)),
    ]


def nb(text):
    """Escape for XML and use non-breaking spaces so alignment survives every renderer."""
    return escape(text).replace(" ", "\u00a0")


def render(art, info, theme):
    c = THEMES[theme]
    art_w = max(len(a) for a in art)
    # center short art vertically next to the info column
    art = [""] * max(0, (len(info) - len(art)) // 2) + list(art)
    rows = list(zip_longest(art, info, fillvalue=None))
    info_x = PAD_X + (art_w + GAP) * CHAR_W
    width = int(info_x + W * CHAR_W + PAD_X)
    height = len(rows) * LINE_H + 2 * PAD_Y - 6

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="fastfetch profile card">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'<g font-family="{FONT}" font-size="{FONT_SIZE}">',
    ]
    for i, (a, segs) in enumerate(rows):
        y = PAD_Y + i * LINE_H + FONT_SIZE
        if a and a.strip():
            out.append(f'<text x="{PAD_X}" y="{y}" fill="{c["fg"]}">{nb(a)}</text>')
        if segs:
            parts = "".join(
                f'<tspan fill="{c[role]}">{nb(text)}</tspan>' for text, role in segs
            )
            out.append(f'<text x="{info_x:.1f}" y="{y}">{parts}</text>')
    out += ["</g>", "</svg>"]
    return "\n".join(out)


def main():
    art = load_art()
    info = build_info()
    Path("assets").mkdir(exist_ok=True)
    for theme in THEMES:
        Path(f"assets/fastfetch-{theme}.svg").write_text(
            render(art, info, theme), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
