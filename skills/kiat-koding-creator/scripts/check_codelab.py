#!/usr/bin/env python3
"""Check codelab steps against the Kiat Koding gate before sending them with add_lesson or update_lesson.

Usage: python3 check_codelab.py steps.json
steps.json holds the `steps` array (or an object with a `steps` field). Exit code 0 means the gate would accept it.
This mirrors the server's gate (crates/server/src/mcp/gate.rs). The server stays the judge: if they disagree, it wins.
"""

import json
import sys

STEP_WORDS = 1000
LESSON_WORDS = 3000
PARAGRAPH_WORDS = 70
WORDS_PER_LINE = 20
VISUAL_WORDS = 200
BLOCK_LINES = 10


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
            elif tag in ("mermaid", "video"):
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
                f"A line of code or output carries {WORDS_PER_LINE} words, a diagram, chart, video or image {VISUAL_WORDS}. "
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
