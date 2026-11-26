#!/usr/bin/env python3
"""Check codelab steps against the Kiat Koding gate before sending them with add_lesson or update_lesson.

Usage: python3 check_codelab.py steps.json
steps.json holds the `steps` array (or an object with a `steps` field). Exit code 0 means the gate would accept it.
This mirrors the server's gate and demo checks (crates/server/src/mcp/gate.rs and demo.rs). The server stays the judge:
if they disagree, it wins.
"""

import json
import re
import sys

STEP_WORDS = 1000
LESSON_WORDS = 3000
PARAGRAPH_WORDS = 70
WORDS_PER_LINE = 20
VISUAL_WORDS = 200
BLOCK_LINES = 10
DEMO_CHARS = 30000
CDN = "https://cdnjs.cloudflare.com/"

NAMES = (
    r"black|white|red|green|blue|yellow|orange|purple|pink|brown|gr[ae]y|cyan|magenta|navy|teal|maroon|olive|"
    r"lime|silver|gold|crimson|coral|tomato|salmon|violet|indigo|aqua|fuchsia|beige|khaki|(?:light|dark)(?:gr[ae]y|blue|red|green)|"
    r"steelblue|skyblue|royalblue|orangered|slategr[ae]y|whitesmoke|gainsboro"
)
HEX_VALUE = r"(#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4}))\b"
# A hex colour as a value, not a number in text ("komentar #123").
HEX = [re.compile(r"[:=(,\"'`]\s*" + HEX_VALUE, re.I), re.compile(r":[^;{}<>\"'\n]*\s" + HEX_VALUE, re.I)]
# A preceding dot is a library helper fed from kk.color, such as d3.rgb(kk.color.ink).
FUNCTION = re.compile(r"(?:^|[^.\w-])((?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\()", re.I)
NAMED = [
    re.compile(
        r"(?:^|[;{\s\"'])(?:color|background(?:-color)?|border(?:-(?:top|right|bottom|left))?(?:-color)?|outline(?:-color)?|fill|stroke|stop-color|flood-color|caret-color|accent-color|text-decoration-color|box-shadow|text-shadow)\s*:[^;}\"'<>]*?\b("
        + NAMES
        + r")\b",
        re.I,
    ),
    re.compile(r"\b(?:fill|stroke|stop-color|flood-color|color|bgcolor)\s*=\s*[\"']\s*(" + NAMES + r")\s*[\"']", re.I),
    re.compile(
        r"\b(?:fillStyle|strokeStyle|shadowColor|color|background|backgroundColor|fill|stroke)\s*[:=]\s*[\"'`]\s*(" + NAMES + r")\s*[\"'`]",
        re.I,
    ),
    re.compile(
        r"\.(?:attr|style)\(\s*[\"'](?:fill|stroke|color|background(?:-color)?|stop-color)[\"']\s*,\s*[\"']\s*(" + NAMES + r")\s*[\"']",
        re.I,
    ),
]
FONT = re.compile(r"(?:font-family|fontFamily)\s*[:=]\s*[\"'`]?\s*([^;}\"'`\n]*)", re.I)
SCRIPT_SRC = re.compile(r"<script\b[^>]*\bsrc\s*=\s*[\"']?\s*([^\"'\s>]+)", re.I)
OUTSIDE = re.compile(r"(?:\b(?:src|href|xlink:href)\s*=\s*[\"']?|url\(\s*[\"']?)\s*((?:https?:)?//[^\"'\s)>]*)", re.I)
TAG = re.compile(r"<\s*(!doctype|html|head|body|iframe|object|embed|link|base|meta)\b", re.I)
NETWORK = re.compile(r"\b(fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts)")
STORAGE = re.compile(r"\b(localStorage|sessionStorage|indexedDB|document\.cookie)\b")
DIALOG = re.compile(r"(?:^|[^.\w])((?:alert|confirm|prompt)\s*\()|\bwindow\.(?:alert|confirm|prompt)\b")


def fence_open(line):
    if not line or line[0] not in "`~":
        return None
    c = line[0]
    n = len(line) - len(line.lstrip(c))
    info = line[n:].strip()
    if n >= 3 and not (c == "`" and "`" in info):
        return c, n, info
    return None


def words(line):
    # A link counts its text, not its address.
    parts, rest = [], line
    while "](" in rest:
        at = rest.index("](")
        parts.append(rest[:at])
        end = rest.find(")", at + 2)
        rest = "" if end == -1 else rest[end + 1 :]
    parts.append(rest)
    return sum(1 for w in "".join(parts).split() if any(ch.isalnum() for ch in w))


def is_list_item(line):
    if line.startswith(("- ", "* ", "+ ")):
        return True
    digits = len(line) - len(line.lstrip("0123456789"))
    return digits > 0 and line[digits:].startswith((". ", ") "))


def measure(body):
    m = {"prose": 0, "code": 0, "output": 0, "prompt": False, "images": 0, "diagrams": 0, "long": [], "blocks": [], "joined": []}
    s = {"open": 0, "paragraphs": 0, "unexplained": False}

    def end():
        if s["open"] > 0:
            s["paragraphs"] += 1
            if s["open"] > PARAGRAPH_WORDS:
                m["long"].append((s["paragraphs"], s["open"]))
            s["open"] = 0

    def add(text):
        w = words(text)
        m["prose"] += w
        s["open"] += w
        s["unexplained"] = s["unexplained"] and w == 0

    fence, block = None, 0
    for raw in body.split("\n"):
        line = raw.strip()
        if fence:
            c, n, kind = fence
            if line and all(x == c for x in line) and len(line) >= n:
                fence = None
                if kind == "code":
                    m["blocks"].append(block)
                    s["unexplained"] = True
            elif line:
                if kind == "code":
                    m["code"] += 1
                    block += 1
                elif kind == "output":
                    m["output"] += 1
            continue
        opened = fence_open(line)
        if opened:
            end()
            c, n, info = opened
            tag = (info.split() or [""])[0].lower()
            if tag == "prompt":
                m["prompt"] = True
                kind = "prompt"
            elif tag == "output":
                s["unexplained"] = False
                kind = "output"
            elif tag in ("mermaid", "video", "demo"):
                m["diagrams"] += 1
                kind = "other"
            else:
                if s["unexplained"]:
                    m["joined"].append(len(m["blocks"]) + 1)
                block = 0
                kind = "code"
            fence = (c, n, kind)
            continue
        i = 0
        while i < len(line) and (line[i] == ">" or line[i].isspace()):
            i += 1
        quoted = line[i:]
        if line.startswith(">") and quoted.startswith("[!"):
            text = quoted.split("]", 1)[1] if "]" in quoted else ""
        else:
            text = quoted
        if not text.strip() or text.startswith("|") or all(ch in "-*_ " for ch in text):
            end()
        elif text.startswith("!["):
            end()
            m["images"] += 1
        elif text.startswith("#"):
            end()
            add(text.lstrip("#"))
            s["open"] = 0
        else:
            if is_list_item(text):
                end()
            add(text)
    end()
    return m


def demo_sources(body):
    found, fence = [], None
    for raw in body.split("\n"):
        line = raw.strip()
        if fence:
            c, n, src = fence
            if line and all(x == c for x in line) and len(line) >= n:
                if src is not None:
                    found.append("\n".join(src))
                fence = None
            elif src is not None:
                src.append(raw)
            continue
        opened = fence_open(line)
        if opened:
            c, n, info = opened
            fence = (c, n, [] if (info.split() or [""])[0].lower() == "demo" else None)
    if fence and fence[2] is not None:
        found.append("\n".join(fence[2]))
    return found


def first(pattern, src):
    m = pattern.search(src)
    return m.group(1).strip() if m and m.group(1) else None


def demo_problems(src):
    if not src.strip():
        return ["is empty. Fill it with an HTML fragment: <svg> or <canvas>, <style> and <script>."]
    out = []
    if len(src) > DEMO_CHARS:
        out.append(f"has {len(src)} characters, the limit is {DEMO_CHARS}. Simplify it or make two demos.")
    colour = next((v for v in (first(p, src) for p in HEX) if v), None)
    if not colour:
        f = first(FUNCTION, src)
        colour = f.rstrip("(") if f else next((v for v in (first(p, src) for p in NAMED) if v), None)
    if colour:
        out.append(f"writes a colour value (`{colour}`). Take colours from the Kiat Koding design system: var(--color-...) in CSS, kk.color and kk.series in a script.")
    for m in FONT.finditer(src):
        v = m.group(1).strip()
        low = v.lower()
        if not (low.startswith(("var(", "${", "kk.font")) or low in ("inherit", "initial", "unset", "revert")):
            out.append(f"sets its own font (`{v}`). Use var(--font-body), var(--font-display) or var(--font-mono), class .mono, or kk.font on a canvas.")
            break
    script = next((m.group(1) for m in SCRIPT_SRC.finditer(src) if not m.group(1).startswith(CDN)), None)
    if script:
        out.append(f"loads a script from `{script}`. Outside scripts come only from {CDN}.")
    outside = next((m.group(1) for m in OUTSIDE.finditer(src) if not m.group(1).startswith(CDN)), None)
    if outside:
        out.append(f"links an outside address (`{outside}`). Images come from /uploads/ paths, and a demo cannot open other sites.")
    tag = first(TAG, src)
    if tag:
        out.append(f"uses <{tag.lower()}>. Write only the demo's content, without <html>, <head>, <body>, <meta> or <link>.")
    net = first(NETWORK, src)
    if net:
        out.append(f"uses `{net}`. A demo has no network: write the data into the script.")
    store = first(STORAGE, src)
    if store:
        out.append(f"uses `{store}`. A demo has no storage: keep its state in variables.")
    if DIALOG.search(src):
        out.append("uses alert, confirm or prompt, which the frame blocks. Show the message inside the demo.")
    return out


def check(steps):
    problems, rows = [], []
    total, hands_on, result = 0, False, False
    for n, step in enumerate(steps, 1):
        m = measure(step.get("body") or "")
        shown = m["code"] + m["output"]
        total += m["prose"]
        hands_on |= m["code"] > 0 or m["prompt"]
        result |= m["output"] > 0 or m["images"] > 0
        visuals = m["images"] + m["diagrams"]
        carried = shown * WORDS_PER_LINE + visuals * VISUAL_WORDS
        budget = min(STEP_WORDS, carried)
        rows.append(f"step {n:2}: {m['prose']:4} words, {shown:3} code+output lines, {visuals} visuals, prose allowed {budget:4}  {step.get('title', '')}")
        if m["prose"] > STEP_WORDS:
            problems.append(f"step {n}: {m['prose']} words of prose, the limit is {STEP_WORDS}. Start a new step where the context changes.")
        demos = demo_sources(step.get("body") or "")
        for k, src in enumerate(demos, 1):
            name = f"demo {k}" if len(demos) > 1 else "the demo"
            problems.extend(f"step {n}: {name} {p}" for p in demo_problems(src))
        for p, w in m["long"]:
            problems.append(f"step {n}: paragraph {p} has {w} words, the limit is {PARAGRAPH_WORDS}. Split it.")
        for k, lines in enumerate(m["blocks"], 1):
            if lines > BLOCK_LINES:
                problems.append(f"step {n}: code block {k} has {lines} lines, the limit is {BLOCK_LINES}. Split it and explain each part under it.")
        for k in m["joined"]:
            problems.append(f"step {n}: code block {k} follows the previous code block with no prose between them. Explain the first one before the next.")
        if not m["prompt"] and m["code"] + m["output"] + m["images"] + m["diagrams"] == 0:
            problems.append(f"step {n} is text only. A concept step needs a ```mermaid diagram or chart or an image, a hands-on step its code and output. A table is not a visual.")
        if m["prompt"] and m["code"] == 0:
            problems.append(f"step {n} has a prompt but no code. Show the code the agent wrote, a diff, or the command it ran.")
        elif shown + visuals > 0 and carried < m["prose"]:
            problems.append(
                f"step {n}: {m['prose']} words of prose, but its {shown} lines of code and output and {visuals} visuals carry only {carried}. "
                f"A line of code or output carries {WORDS_PER_LINE} words, a diagram, chart, demo, video or image {VISUAL_WORDS}. "
                "Show more real code, output or visuals, or cut the prose."
            )
    if total > LESSON_WORDS:
        problems.append(f"the lesson has {total} words of prose, the limit is {LESSON_WORDS}. Cut it or make two lessons.")
    if hands_on and not result:
        problems.append("the lesson shows code but no result. Add real output in an ```output fence or a screenshot.")
    return rows, total, problems


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    steps = data["steps"] if isinstance(data, dict) else data
    rows, total, problems = check(steps)
    print("\n".join(rows))
    print(f"lesson: {total} words of prose (limit {LESSON_WORDS})")
    if problems:
        print("\nThe gate would refuse this:")
        print("\n".join(f"- {p}" for p in problems))
        sys.exit(1)
    print("\nThe gate would accept this.")


if __name__ == "__main__":
    main()
