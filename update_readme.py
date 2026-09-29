import os, json, urllib.request
from datetime import date, timedelta
from itertools import zip_longest

USER = "KartikHalkunde"
DOB = date(2005, 9, 26)
W = 52  # width of the info column

ART = [
    r"     .--.     ",
    r"    |o_o |    ",
    r"    |:_/ |    ",
    r"   //   \ \   ",
    r"  (|     | )  ",
    r" /'\_   _/`\  ",
    r" \___)=(___/  ",
]  # replace with your own ASCII art


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
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}"},
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


def row(label, value):
    dots = max(W - 5 - len(label) - len(value), 3)
    return f". {label}: {'.' * dots} {value}"


def head(title):
    return f"- {title} " + "-" * (W - len(title) - 3)


def build():
    repos, stars, followers, commits = stats()
    info = [
        head(f"{USER}@github")[: W],
        row("OS", "Windows 11, Fedora Linux"),
        row("Uptime", uptime(date.today())),
        row("Host", "Your Company"),
        row("IDE", "VSCode, IntelliJ"),
        ".",
        row("Languages.Programming", "Java, Python, JS, C"),
        row("Languages.Computer", "HTML, CSS, JSON, LaTeX, YAML"),
        row("Languages.Real", "English, Hindi, Marathi"),
        ".",
        row("Hobbies.Software", "Minecraft Modding, iOS Jailbreaking"),
        row("Hobbies.Hardware", "Painting, Music"),
        "",
        head("Contact"),
        row("Email.Personal", "kartikhalkunde26@gmail.com"),
        row("Email.Work", "kartikhalkunde@proton.me"),
        row("LinkedIn", "https://www.linkedin.com/in/kartikhalkunde/"),
        row("LeetCode", "https://leetcode.com/u/KartikHalkunde/"),
        "",
        head("GitHub Stats"),
        row("Repos", str(repos)),
        row("Stars", str(stars)),
        row("Followers", str(followers)),
        row("Commits", f"{commits:,}"),
    ]
    art_w = max(len(a) for a in ART)
    lines = []
    for a, i in zip_longest(ART, info, fillvalue=""):
        lines.append(f"{a.ljust(art_w)}   {i}".rstrip())
    return "\n".join(lines)


if __name__ == "__main__":
    with open("README.md", encoding="utf-8") as f:
        text = f.read()
    start, end = "<!--FETCH_START-->", "<!--FETCH_END-->"
    a, b = text.index(start) + len(start), text.index(end)
    new = text[:a] + "\n" + build() + "\n" + text[b:]
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new)
