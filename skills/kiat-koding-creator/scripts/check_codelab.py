#!/usr/bin/env python3
"""Check codelab steps against the Kiat Koding gate before sending them with add_lesson or update_lesson.

Usage: python3 check_codelab.py steps.json
steps.json holds the `steps` array (or an object with a `steps` field). Exit code 0 means the gate would accept it.
This mirrors the server's codelab gate and interactive checks (crates/server/src/mcp/gate.rs and interactive.rs),
including the ```interactive fence, which the server still reads under its old name ```demo. The server stays the
judge: if they disagree, it wins. Change this file together with those two.
"""

import ast
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

STEP_WORDS = 1000
LESSON_WORDS = 3000
PARAGRAPH_WORDS = 70
WORDS_PER_LINE = 20
VISUAL_WORDS = 200
BLOCK_LINES = 10
# Code fence labels that name no language: code under them was never run, so an ```output after it is made up.
UNTAGGED = ("", "text", "txt", "plain", "plaintext", "pseudo", "pseudocode")

PYTHON = ("python", "py", "python3")
JAVASCRIPT = ("javascript", "js", "jsx", "mjs", "cjs", "node")
NOT_CHECKED_LOCALLY = set()


def syntax_error(tag, code):
    """The first syntax error in code an ```output follows, as (line, text), or None.

    The server parses python, javascript and typescript with tree-sitter. Here Python's own parser checks Python and
    `node --check` checks JavaScript when Node is installed; TypeScript is left to the server.
    """
    lines = code.split("\n")
    if tag in PYTHON:
        try:
            ast.parse(code)
        except SyntaxError as e:
            at = e.lineno or 1
            return at, (lines[at - 1].strip() if at <= len(lines) else "")
        return None
    if tag in JAVASCRIPT:
        node = shutil.which("node")
        if not node:
            NOT_CHECKED_LOCALLY.add("javascript (Node is not installed)")
            return None
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
            f.write(code)
        try:
            run = subprocess.run([node, "--check", f.name], capture_output=True, text=True, timeout=20)
        finally:
            os.unlink(f.name)
        if run.returncode == 0:
            return None
        found = re.search(r":(\d+)\n", run.stderr)
        at = int(found.group(1)) if found else 1
        return at, (lines[at - 1].strip() if at <= len(lines) else "")
    if tag in ("typescript", "ts", "tsx"):
        NOT_CHECKED_LOCALLY.add("typescript")
    return None


FENCES = ("interactive", "demo")
MAX_CHARS = 30000
PER_STEP = 1
PER_LESSON = 2
CDN = "https://cdnjs.cloudflare.com/"
TEACHES_WORDS = 25
TASK_WORDS = 30
MAX_BUTTONS = 4
BUTTON_CHARS = 36
# The frame's content width on a 320px phone, and the smallest text that stays readable there.
PHONE_WIDTH = 288.0
MIN_TEXT_PX = 11.0
MOTION_MS = (150.0, 1000.0)
# Fences whose lines are not the step's code or output.
NOT_CODE = ("prompt", "mermaid", "video", "interactive", "demo")
# Boxes and arrows are an interactive flow; Mermaid keeps charts.
BANNED_MERMAID = ("flowchart", "graph", "sequenceDiagram", "stateDiagram")
SHOWS = ("sequence", "change", "movement", "structure")
KEYS = ("mode", "shows", "teaches", "task", "answer", "mirrors")
STEPPER_WORDS = ("berikutnya", "selanjutnya", "sebelumnya", "lanjut", "mundur", "maju", "next", "previous", "prev", "back", "reset")
KIT_LABELS = ("Sebelumnya", "Berikutnya", "Ulangi")
STATUS_WORDS = ("ok", "success", "pass", "valid", "benar", "berhasil", "lolos", "error", "err", "fail", "invalid", "wrong", "salah", "gagal", "warn", "bad", "miss", "danger")

NAMES = (
    r"black|white|red|green|blue|yellow|orange|purple|pink|brown|gr[ae]y|cyan|magenta|navy|teal|maroon|olive|"
    r"lime|silver|gold|crimson|coral|tomato|salmon|violet|indigo|aqua|fuchsia|beige|khaki|(?:light|dark)(?:gr[ae]y|blue|red|green)|"
    r"steelblue|skyblue|royalblue|orangered|slategr[ae]y|whitesmoke|gainsboro"
)
HEX_VALUE = r"(#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4}))\b"
I = re.I
S = re.S

# A hex colour as a value: after a quote, colon, equals sign, bracket or comma, or later in a CSS declaration.
# A number in text ("komentar #123") is neither.
HEX = [re.compile(r"[:=(,\x22'`]\s*" + HEX_VALUE, I), re.compile(r":[^;{}<>\x22'\n]*\s" + HEX_VALUE, I)]
# A preceding dot is a library's colour helper fed from kk.color, not a literal. No space before the bracket.
FUNCTION = re.compile(r"(?:^|[^.\w-])((?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\()", I)
NAMED = [
    re.compile(
        r"(?:^|[;{\s\x22'])(?:color|background(?:-color)?|border(?:-(?:top|right|bottom|left))?(?:-color)?|outline(?:-color)?|fill|stroke|stop-color|flood-color|caret-color|accent-color|text-decoration-color|box-shadow|text-shadow)\s*:[^;}\x22'<>]*?\b("
        + NAMES
        + r")\b",
        I,
    ),
    re.compile(r"\b(?:fill|stroke|stop-color|flood-color|color|bgcolor)\s*=\s*[\x22']\s*(" + NAMES + r")\s*[\x22']", I),
    re.compile(
        r"\b(?:fillStyle|strokeStyle|shadowColor|color|background|backgroundColor|fill|stroke)\s*[:=]\s*[\x22'`]\s*(" + NAMES + r")\s*[\x22'`]",
        I,
    ),
    re.compile(
        r"\.(?:attr|style)\(\s*[\x22'](?:fill|stroke|color|background(?:-color)?|stop-color)[\x22']\s*,\s*[\x22']\s*(" + NAMES + r")\s*[\x22']",
        I,
    ),
]
FONT = re.compile(r"""(?:font-family|fontFamily)\s*[:=]\s*["'`]?\s*([^;}"'`\n]*)""", I)
SCRIPT_SRC = re.compile(r"""<script\b[^>]*\bsrc\s*=\s*["']?\s*([^"'\s>]+)""", I)
OUTSIDE = re.compile(r"""(?:\b(?:src|href|xlink:href)\s*=\s*["']?|url\(\s*["']?)\s*((?:https?:)?//[^"'\s)>]*)""", I)
DOC_TAG = re.compile(r"<\s*(!doctype|html|head|body|iframe|object|embed|link|base|meta)\b", I)
NETWORK = re.compile(r"\b(fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts)")
STORAGE = re.compile(r"\b(localStorage|sessionStorage|indexedDB|document\.cookie)\b")
DIALOG = re.compile(r"(?:^|[^.\w])((?:alert|confirm|prompt)\s*\()|\bwindow\.(?:alert|confirm|prompt)\b")

SCRIPT_BLOCK = re.compile(r"<script\b([^>]*)>(.*?)</script>", I | S)
STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", I | S)
STYLE_ATTR = re.compile(r"""\bstyle\s*=\s*(?:"([^"]*)"|'([^']*)')""", I)
COMMENT = re.compile(r"<!--.*?-->", S)
ANY_TAG = re.compile(r"<[^>]*>")
STRING_LIT = re.compile(r"""'((?:[^'\\\n]|\\.)*)'|"((?:[^"\\\n]|\\.)*)"|`((?:[^`\\]|\\.)*)`""")
BUTTON = re.compile(r"<button\b[^>]*>(.*?)</button>", I | S)
FIELD = re.compile(r"<(?:input|select|textarea)\b([^>]*)>", I)
LABEL_TAG = re.compile(r"<label\b([^>]*)>", I)
ID_ATTR = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""", I)
FOR_ATTR = re.compile(r"""\bfor\s*=\s*["']([^"']+)["']""", I)
CLASS_ATTR = re.compile(r"""\bclass\s*=\s*["']([^"']*)["']""", I)
SVG_BLOCK = re.compile(r"<svg\b([^>]*)>(.*?)</svg>", I | S)
VIEWBOX = re.compile(r"""viewBox\s*=\s*["']\s*-?[\d.]+[\s,]+-?[\d.]+[\s,]+([\d.]+)""", I)
TEXT_TAG = re.compile(r"<text\b([^>]*)>", I | S)
FONT_SIZE = re.compile(r"""font-size\s*[=:]\s*["']?\s*([\d.]+)\s*(px|rem|em)?""", I)
CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", S)
MOTION_ANY = re.compile(r"\b(?:transition|animation)(?:-[a-z]+)?\s*[:=]|@keyframes|\.animate\(", I)
MOTION_DECL = re.compile(r"""\b(?:transition|animation)(?:-duration)?\s*[:=]\s*["'`]?([^;}"'`\n]+)""", I)
DURATION = re.compile(r"(\d*\.?\d+)\s*(ms|s)\b", I)
MOVEMENT = re.compile(r"""translate\(|\.style\.(?:left|top|transform)\b|setAttribute\(\s*["'](?:x|y|cx|cy|x1|x2|y1|y2|transform|points|d)["']""", I)
RAF = re.compile(r"requestAnimationFrame\(\s*([A-Za-z_$][\w$]*)")
FLOW = re.compile(r"""<script\b([^>]*\bdata-kk\s*=\s*["']flow["'][^>]*)>(.*?)</script>""", I | S)
# \p{L}\p{N} is [^\W_]; Python's \w is Unicode-aware like Rust's.
BANG = re.compile(r"""(?:[^\W_]|[)}\]])!(?:\s|\Z|["'`])""")
WORD = re.compile(r"\w+")
NODE_ID = re.compile(r"[a-z0-9_-]{1,24}")


def rust_lines(s):
    """Rust's str::lines: split on \\n, drop one trailing empty piece and a \\r before each \\n."""
    parts = s.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return [p[:-1] if p.endswith("\r") else p for p in parts]


def alower(s):
    return "".join(c.lower() if c.isascii() else c for c in s)


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
    m = {
        "prose": 0, "code": 0, "output": 0, "prompt": False, "images": 0, "diagrams": 0, "interactives": 0,
        "untagged": 0, "syntax": [], "dashes": 0, "long": [], "blocks": [], "joined": [],
    }
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
    # The last fence's tag and text when it was code, to see what an ```output follows.
    last_code = None
    for raw in rust_lines(body):
        line = raw.strip()
        if fence:
            c, n, kind = fence
            if line and all(x == c for x in line) and len(line) >= n:
                fence = None
                if kind == "code":
                    m["blocks"].append(block)
                    s["unexplained"] = True
                continue
            if kind == "code" and last_code is not None:
                last_code[1].append(raw)
            if line:
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
            tag = alower((info.split() or [""])[0])
            if tag == "prompt":
                m["prompt"] = True
                kind = "prompt"
            elif tag == "output":
                s["unexplained"] = False
                if last_code is not None and last_code[0] in UNTAGGED:
                    m["untagged"] += 1
                elif last_code is not None:
                    bad = syntax_error(last_code[0], "\n".join(last_code[1]) + "\n")
                    if bad:
                        m["syntax"].append((last_code[0],) + bad)
                kind = "output"
            elif tag in ("mermaid", "video", "interactive", "demo"):
                m["diagrams"] += 1
                if tag in FENCES:
                    m["interactives"] += 1
                kind = "other"
            else:
                if s["unexplained"]:
                    m["joined"].append(len(m["blocks"]) + 1)
                block = 0
                kind = "code"
            last_code = (tag, []) if kind == "code" else None
            fence = (c, n, kind)
            continue
        if "—" in line or " – " in line:
            m["dashes"] += 1
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
            # A heading counts toward the step's prose but is no paragraph.
            end()
            add(text.lstrip("#"))
            s["open"] = 0
        else:
            if is_list_item(text):
                end()
            add(text)
    end()
    return m


# ---------------------------------------------------------------- interactive.rs


def scan(text):
    """Fences of a Markdown text as (tag, content), and the prose outside them."""
    fences, prose = [], []
    open_ = None  # [char, count, tag, body lines]
    for raw in rust_lines(text):
        line = raw.strip()
        if open_ is not None:
            c, n, tag, body = open_
            if line and all(x == c for x in line) and len(line) >= n:
                fences.append((tag, "".join(b + "\n" for b in body)))
                open_ = None
            else:
                body.append(raw)
            continue
        opened = fence_open(line)
        if opened:
            c, n, info = opened
            open_ = [c, n, alower((info.split() or [""])[0]), []]
        else:
            prose.append(raw + "\n")
    # An unclosed fence runs to the end, as Markdown renders it.
    if open_ is not None:
        fences.append((open_[2], "".join(b + "\n" for b in open_[3])))
    return fences, "".join(prose)


def banned_mermaid(text):
    """Mermaid diagram types refused in a Markdown text, one entry per fence."""
    out = []
    for tag, body in scan(text)[0]:
        if tag != "mermaid":
            continue
        first_line = next((l.strip() for l in rust_lines(body) if l.strip()), None)
        if first_line is None:
            continue
        kind = next((k for k in BANNED_MERMAID if first_line.startswith(k)), None)
        if kind:
            out.append(kind)
    return out


def header(src):
    """The header comment as a dict and the fragment after it, when the source starts with one."""
    s = src.lstrip()
    if not s.startswith("<!--"):
        return None
    body = s[4:]
    end = body.find("-->")
    if end == -1:
        return None
    h = {"mode": "", "shows": [], "teaches": "", "task": "", "answer": "", "mirrors": [], "unknown": []}
    in_mirrors = False
    for line in rust_lines(body[:end]):
        t = line.strip()
        if not t:
            continue
        if ":" in t:
            k, v = t.split(":", 1)
            key = alower(k.strip())
            if key in KEYS:
                v = v.strip()
                in_mirrors = key == "mirrors"
                if key == "mode":
                    h["mode"] = alower(v)
                elif key == "shows":
                    h["shows"] = [alower(x) for x in re.split(r"[,\s]", v) if x]
                elif key in ("teaches", "task", "answer"):
                    h[key] = v
                elif v:
                    h["mirrors"].append(v)
                continue
        if in_mirrors:
            h["mirrors"].append(t)
        else:
            h["unknown"].append(t)
    return h, body[end + 3 :]


def decode(s):
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'").replace("&apos;", "'").replace("&nbsp;", " ").replace("&amp;", "&")


def squash(s):
    return " ".join(s.split())


def static_text(fragment):
    """What the learner reads before touching anything: markup text without scripts, styles and comments."""
    without = SCRIPT_BLOCK.sub(" ", fragment)
    without = STYLE_BLOCK.sub(" ", without)
    without = COMMENT.sub(" ", without)
    return decode(ANY_TAG.sub(" ", without))


def code_of(fragment):
    """Script and style text, including inline style attributes. Flow data is not script."""
    scripts = "\n".join(m.group(2) for m in SCRIPT_BLOCK.finditer(fragment) if "application/json" not in m.group(1).lower())
    styles = "\n".join(m.group(1) for m in STYLE_BLOCK.finditer(fragment))
    for m in STYLE_ATTR.finditer(fragment):
        styles += "\n_{" + (m.group(1) if m.group(1) is not None else (m.group(2) or "")) + "}"
    return scripts, styles


def sentences(scripts):
    """String literals in scripts that read as words for people, not keys or selectors."""
    out = []
    for m in STRING_LIT.finditer(scripts):
        s = next((g for g in m.groups() if g is not None), None)
        if s is not None and " " in s and any(c.isalpha() for c in s):
            out.append(s)
    return out


def first(pattern, src):
    m = pattern.search(src)
    return m.group(1).strip() if m and m.group(1) is not None else None


def nwords(s):
    return len(s.split())


def css_rules(styles):
    return [(m.group(1).strip(), m.group(2)) for m in CSS_RULE.finditer(styles)]


def px(value, unit):
    try:
        n = float(value)
    except ValueError:
        return None
    return n * 16.0 if (unit or "").lower() in ("rem", "em") else n


def selector_has_class(selector, cls):
    needle = "." + cls
    for m in re.finditer(re.escape(needle), selector):
        rest = selector[m.end() :]
        if not rest or not (rest[0].isalnum() or rest[0] in "-_"):
            return True
    return False


def _min(values):
    values = list(values)
    return min(values) if values else None


def smallest_svg_text(fragment, rules):
    """The smallest SVG text in a fragment as it renders on a phone: (rendered px, viewBox width, font-size)."""

    def size_of(decl):
        m = FONT_SIZE.search(decl)
        return px(m.group(1), m.group(2)) if m else None

    def text_sel(sel):
        return any(p.strip() == "text" or p.strip().endswith(" text") or p.strip().endswith(">text") for p in sel.split(","))

    base = _min(s for s in (size_of(d) for sel, d in rules if text_sel(sel)) if s is not None)
    smallest = None
    for svg in SVG_BLOCK.finditer(fragment):
        vb = VIEWBOX.search(svg.group(1))
        try:
            width = float(vb.group(1)) if vb else None
        except ValueError:
            width = None
        if width is None or not width > 0.0:
            continue
        for text in TEXT_TAG.finditer(svg.group(2)):
            attrs = text.group(1)
            own = size_of(attrs)
            by_class = None
            cm = CLASS_ATTR.search(attrs)
            if cm:
                sizes = []
                for cls in cm.group(1).split():
                    for sel, d in rules:
                        if any(selector_has_class(p, cls) for p in sel.split(",")):
                            sz = size_of(d)
                            if sz is not None:
                                sizes.append(sz)
                by_class = _min(sizes)
            size = own if own is not None else by_class if by_class is not None else base if base is not None else 16.0
            rendered = size * min(PHONE_WIDTH, width) / width
            if smallest is None or rendered < smallest[0]:
                smallest = (rendered, width, size)
    return smallest


def body_of(scripts, name):
    """The body of a named function, found by matching braces, to tell a requestAnimationFrame loop from a single call."""
    n = re.escape(name)
    pattern = re.compile(rf"function\s+{n}\s*\(|\b{n}\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)")
    m = pattern.search(scripts)
    if not m:
        return None
    at = m.end()
    rel = scripts[at:].find("{")
    if rel == -1:
        return None
    start = at + rel
    depth = 0
    for i, c in enumerate(scripts[start:]):
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return scripts[start : start + i]
    return None


def title_case(label):
    ws = label.split()

    def first_alpha_upper(w):
        c = next((c for c in w if c.isalpha()), None)
        return c is None or c.isupper()

    return (
        len(ws) >= 2
        and not any(c in "=._[]{}<>" for c in label)
        and all(first_alpha_upper(w) for w in ws)
        and not all(all(c.isupper() for c in w if c.isalpha()) for w in ws)
    )


def sentence_case(label):
    out = []
    for i, w in enumerate(label.split()):
        alpha = [c for c in w if c.isalpha()]
        acronym = len(alpha) <= 4 and all(c.isupper() for c in alpha)
        out.append(w if i == 0 or acronym else w.lower())
    return " ".join(out)


def _s(v, k):
    x = v.get(k) if isinstance(v, dict) else None
    return x if isinstance(x, str) else ""


def _a(v, k):
    x = v.get(k) if isinstance(v, dict) else None
    return x if isinstance(x, list) else []


def _no_constants(name):
    raise ValueError(f"invalid constant {name}")


def check_flow(attrs, js):
    """A flow's problems, and its words for the writing checks."""
    out, texts = [], []
    if "application/json" not in attrs.lower():
        out.append('has a flow without type="application/json", so the browser runs it as a script.')
    try:
        spec = json.loads(js, parse_constant=_no_constants)
    except ValueError as e:
        out.append(f"has a flow that is not valid JSON ({e}).")
        return out, texts
    rows = _a(spec, "rows")
    if not rows or len(rows) > 8:
        out.append(f"has a flow with {len(rows)} rows. Use 1 to 8 rows of nodes.")
    ids = set()
    for row in rows:
        nodes = row if isinstance(row, list) else []
        if not nodes or len(nodes) > 4:
            out.append(f"has a flow row with {len(nodes)} nodes. A row holds 1 to 4 nodes.")
        for node in nodes:
            nid = _s(node, "id")
            if not NODE_ID.fullmatch(nid):
                out.append(f"has a flow node with id `{nid}`. An id uses lowercase letters, digits, - or _, at most 24 characters.")
            elif nid in ids:
                out.append(f"uses node id `{nid}` twice.")
            else:
                ids.add(nid)
            label = _s(node, "label")
            if not label.strip() or len(label) > 32:
                out.append(f"has node `{nid}` with a label of {len(label)} characters. A label is required, at most 32.")
            note = _s(node, "note")
            if len(note) > 60:
                out.append(f"has node `{nid}` with a note of {len(note)} characters, at most 60.")
            texts.extend([label, note])
    edges = set()
    for edge in _a(spec, "edges"):
        frm, to = _s(edge, "from"), _s(edge, "to")
        if frm not in ids or to not in ids or frm == to:
            out.append(f"has an arrow `{frm}>{to}` that does not connect two different existing nodes.")
        elif f"{frm}>{to}" in edges:
            out.append(f"has arrow `{frm}>{to}` twice.")
        else:
            edges.add(f"{frm}>{to}")
        label = _s(edge, "label")
        if len(label) > 24:
            out.append(f"has arrow label `{frm}>{to}` of {len(label)} characters, at most 24.")
        texts.append(label)
    stages = _a(spec, "stages")
    if len(stages) < 2 or len(stages) > 10:
        out.append(f"has a flow with {len(stages)} stages. Use 2 to 10 stages.")
    shown = set()
    for i, stage in enumerate(stages):
        caption = _s(stage, "caption")
        if not caption.strip() or len(caption) > 140:
            out.append(f"has flow stage {i + 1} with a caption of {len(caption)} characters. A caption is required, at most 140.")
        texts.append(caption)
        new = 0
        items = [x for x in _a(stage, "show") if isinstance(x, str)]
        for item in items:
            if ">" in item:
                frm, to = item.split(">", 1)
                if item not in edges:
                    out.append(f"shows arrow `{item}` in stage {i + 1} but that arrow is not in edges.")
                elif frm not in shown or to not in shown:
                    both = set(items)
                    if not (frm in shown or frm in both) or not (to in shown or to in both):
                        out.append(f"shows arrow `{item}` in stage {i + 1} before both its nodes are shown.")
            elif item not in ids:
                out.append(f"shows node `{item}` in stage {i + 1} but that node does not exist.")
            if item not in shown:
                shown.add(item)
                new += 1
        if new == 0:
            out.append(f"has flow stage {i + 1} that shows nothing new.")
    missing = sorted(x for x in list(ids) + list(edges) if x not in shown)
    if missing:
        out.append(f"does not show {', '.join(missing)} by the last stage. The last stage must show the whole diagram.")
    return out, texts


def check_interactive(src, ctx):
    """What is wrong with one interactive, each as a sentence that says how to fix it."""
    out = []
    if not src.strip():
        return ["is empty. Fill it with a header and then an HTML fragment."]
    chars = len(src)
    if chars > MAX_CHARS:
        out.append(f"has {chars} characters, the limit is {MAX_CHARS}. Simplify it or split it in two.")
    parsed = header(src)
    # Without a header the rest is still checked, so everything gets fixed in one round.
    headless = parsed is None
    if headless:
        out.append(
            "has no header yet. Start with an <!-- --> comment holding mode, shows, teaches, and task, answer and mirrors where needed, as in the guide."
        )
        h = {"mode": "interactive", "shows": [], "teaches": "", "task": "", "answer": "", "mirrors": [], "unknown": []}
        fragment = src
    else:
        h, fragment = parsed
    scripts, styles = code_of(fragment)
    visible = static_text(fragment)
    lines = sentences(scripts)
    flow = FLOW.search(fragment)
    flow_texts = []
    if flow:
        problems, flow_texts = check_flow(flow.group(1), flow.group(2))
        out.extend(problems)
    auto = h["mode"] == "auto"

    # The header.
    for line in h["unknown"]:
        out.append(f"has an unknown header line (`{line}`). Keys in use: mode, shows, teaches, task, answer, mirrors.")
    if h["mode"] != "interactive" and not auto:
        out.append(f"uses mode `{h['mode']}`. Choose interactive (the learner acts) or auto (it plays by itself once when visible).")
    if not headless and not h["shows"]:
        out.append("needs `shows` with sequence, change, movement or structure.")
    for s in h["shows"]:
        if s not in SHOWS:
            out.append(f"writes `shows: {s}`. Choose from sequence, change, movement and structure.")
    if not headless and (not h["teaches"] or nwords(h["teaches"]) > TEACHES_WORDS):
        out.append(f"needs `teaches`: one sentence, at most {TEACHES_WORDS} words, on what it makes visible.")
    if auto and h["task"]:
        out.append("uses `task` in auto mode. Auto mode plays by itself, so remove the task or use interactive mode.")
    if not headless and not auto and (not h["task"] or nwords(h["task"]) > TASK_WORDS):
        out.append(
            f"needs `task` (at most {TASK_WORDS} words): a question to guess first, ending with a question mark, or a goal for the learner to reach."
        )
    if not auto and h["task"].rstrip().endswith("?") and not h["answer"]:
        out.append("needs `answer` because its task is a question.")
    if any(c in "0123456789" for c in h["answer"]) and h["answer"].strip() in squash(visible):
        out.append(f"already shows the answer `{h['answer'].strip()}` before the learner does anything. Reveal the answer through interaction.")
    if not headless and not (not ctx["code"] and not ctx["output"]) and not h["mirrors"]:
        out.append("needs `mirrors`: lines copied exactly from this step's code or output blocks and shown in the interactive too.")
    whole = decode(fragment)
    whole_squashed = squash(whole)
    tokens = set(WORD.findall(whole))
    for m in h["mirrors"]:
        line = m.strip()
        shown = squash(line) in whole_squashed
        if line in ctx["code"]:
            # Code is shown as written: a renamed variable or a made-up label teaches the wrong code.
            if not shown:
                out.append(f"does not show the code line `{line}` exactly as in its step. Write the same line, with the same names and values.")
        elif line in ctx["output"]:
            # Output may be computed by the interactive, so only its names and numbers must be there.
            missing = [w for w in WORD.findall(line) if w not in tokens]
            if not shown and missing:
                out.append(f"does not show the output `{line}`: {', '.join(missing)} is not in it. Use the same names and values as the step.")
        else:
            out.append(f"has a mirrors line `{line}` that is not in this step's code or output blocks. Copy it exactly, names and numbers included.")

    # Design system and the frame's limits.
    colour = next((v for v in (first(p, fragment) for p in HEX) if v is not None), None)
    if colour is None:
        f = first(FUNCTION, fragment)
        colour = f.rstrip("(") if f is not None else next((v for v in (first(p, fragment) for p in NAMED) if v is not None), None)
    if colour is not None:
        out.append(
            f"writes a colour value directly (`{colour}`). Take every colour from the Kiat Koding design system: var(--color-ink), var(--color-accent), var(--color-series-1) to -4 and the other tokens in CSS, or kk.color and kk.series in a script."
        )
    for m in FONT.finditer(fragment):
        v = m.group(1).strip()
        low = alower(v)
        if not (low.startswith(("var(", "${", "kk.font")) or low in ("inherit", "initial", "unset", "revert")):
            out.append(f"sets its own font (`{v}`). Use var(--font-body), var(--font-display) or var(--font-mono), class .mono, or kk.font on a canvas.")
            break
    script = next((m.group(1) for m in SCRIPT_SRC.finditer(fragment) if not m.group(1).startswith(CDN)), None)
    if script is not None:
        out.append(f"loads a script from `{script}`. Outside scripts come only from {CDN}.")
    outside = next((m.group(1) for m in OUTSIDE.finditer(fragment) if not m.group(1).startswith(CDN)), None)
    if outside is not None:
        out.append(
            f"links an outside address (`{outside}`). Images come from /uploads/ paths (generate_lesson_image or create_image_upload), and an interactive cannot open other sites."
        )
    tag = first(DOC_TAG, fragment)
    if tag is not None:
        out.append(
            f"uses the <{alower(tag)}> tag. Write only its content, without <html>, <head>, <body>, <meta>, <link> or frames: Kiat Koding's fonts and styles are already provided."
        )
    net = first(NETWORK, scripts)
    if net is not None:
        out.append(f"uses `{net}`. An interactive has no network access: write its data directly in the script.")
    store = first(STORAGE, scripts)
    if store is not None:
        out.append(f"uses `{store}`. An interactive has no storage: keep its state in variables.")
    if DIALOG.search(scripts):
        out.append("uses alert, confirm or prompt, which are blocked. Show the message inside the interactive.")

    # Controls.
    labels = [l for l in (squash(decode(ANY_TAG.sub(" ", m.group(1)))) for m in BUTTON.finditer(fragment)) if l]
    fields = [a for a in (m.group(1) for m in FIELD.finditer(fragment)) if 'type="hidden"' not in a.lower()]
    stepper = "kk.stepper(" in scripts
    sequence = "kk.sequence(" in scripts
    controls = bool(labels) or bool(fields) or stepper or (flow is not None and not auto)
    if not auto and not controls:
        out.append("has interactive mode but no controls. Add buttons, a slider or inputs in HTML, kk.stepper, or a flow.")
    for l in labels:
        if any(w in STEPPER_WORDS for w in WORD.findall(l.lower())):
            out.append(f"builds its own step button (`{l}`). Use kk.stepper, which provides Sebelumnya, Berikutnya and the step position.")
            break
    if len(labels) > MAX_BUTTONS:
        out.append(f"has {len(labels)} buttons, at most {MAX_BUTTONS}. Use a select or a slider.")
    label_chars = sum(len(l) for l in labels)
    if label_chars > BUTTON_CHARS:
        out.append(f"has button labels of {label_chars} characters, at most {BUTTON_CHARS} in all. Shorten them, or use a select or a slider.")
    for l in labels:
        if title_case(l):
            out.append(f"uses Title Case in the label `{l}`. Write it like an ordinary sentence: `{sentence_case(l)}`.")
            break
    prose = ctx["prose"].lower()
    for l in list(labels) + list(KIT_LABELS):
        if len(l) < 4:
            continue
        low = l.lower()
        if f"**{low}**" in prose or f'"{low}"' in prose or f"tombol {low}" in prose:
            out.append(f"has its use explained in the narration (`{l}`). The task and the controls inside it are enough, so remove that sentence from the narration.")
            break

    # Seeing it.
    rules = css_rules(styles)
    small = smallest_svg_text(fragment, rules)
    if small is not None and small[0] < MIN_TEXT_PX:
        rendered, width, size = small
        need = math.ceil(MIN_TEXT_PX * width / min(PHONE_WIDTH, width))
        out.append(
            f"has SVG text that renders at only {rendered:.0f}px on a phone (viewBox {width:.0f} wide, font-size {size:.0f}). Move the text to HTML, or raise the font-size to {float(need):.0f} or more."
        )
    for selector, decl in rules:
        if ("--color-ok" in decl or "--color-warn" in decl) and not any(w in selector.lower() for w in STATUS_WORDS):
            out.append(
                f"uses a status colour in `{squash(selector)}`. --color-ok and --color-warn are only for success and failure, in classes named that way. For highlights use is-current, is-done and is-off."
            )
            break
    for c in SVG_BLOCK.finditer(fragment):
        a = c.group(1).lower()
        if 'aria-hidden="true"' not in a and not ('role="img"' in a and ("aria-label" in a or "<title" in c.group(2))):
            out.append('has an <svg> without role="img" and aria-label.')
            break
    label_for = {v for v in (first(FOR_ATTR, m.group(1)) for m in LABEL_TAG.finditer(fragment)) if v is not None}
    bare_labels = sum(1 for m in LABEL_TAG.finditer(fragment) if first(FOR_ATTR, m.group(1)) is None)
    ids = [first(ID_ATTR, a) for a in fields]
    unlabelled_ids = sum(1 for i in ids if i is not None and i not in label_for)
    without_id = sum(1 for i in ids if i is None)
    if unlabelled_ids + without_id > bare_labels:
        out.append("has an input without a <label>.")

    # Motion.
    detected = []
    if controls:
        detected.append("changes when the learner acts")
    if stepper or sequence or flow is not None or "marker-end" in fragment:
        detected.append("has a sequence of steps")
    if MOVEMENT.search(scripts):
        detected.append("moves positions")
    declared = any(s != "structure" and s in SHOWS for s in h["shows"])
    if h["shows"] and not declared and detected:
        out.append(f"declares `shows: structure` but its content {' and '.join(detected)}. Set shows to sequence, change or movement.")
    moves = bool(MOTION_ANY.search(styles) or MOTION_ANY.search(scripts))
    if (declared or detected) and flow is None and not moves:
        out.append("does not move yet. Add a transition or animation to what changes (150 to 1000 ms, var(--ease-out)), or use a flow.")
    for m in MOTION_DECL.finditer(f"{styles}\n{scripts}"):
        decl = m.group(1)
        if "infinite" in decl.lower():
            out.append("uses an infinite animation. Motion runs once for each change.")
        for part in decl.split(","):
            d = DURATION.search(part)
            if not d:
                continue
            try:
                n = float(d.group(1))
            except ValueError:
                continue
            ms = n * 1000.0 if d.group(2).lower() == "s" else n
            if ms > 0.0 and not (MOTION_MS[0] <= ms <= MOTION_MS[1]):
                out.append(f"uses a motion duration of {ms:.0f} ms. Use {MOTION_MS[0]:.0f} to {MOTION_MS[1]:.0f} ms.")
            elif ms > 0.0 and "var(--ease" not in part:
                out.append(f"moves without var(--ease-out) (`{part.strip()}`).")
    raf_loop = False
    for c in RAF.finditer(scripts):
        b = body_of(scripts, c.group(1))
        if b is not None and f"requestAnimationFrame({c.group(1)}" in b:
            raf_loop = True
            break
    if (raf_loop or "setInterval(" in scripts or ".animate(" in scripts) and "kk.reducedMotion" not in scripts:
        out.append("animates through script without checking kk.reducedMotion. Show the end state at once when kk.reducedMotion is true.")
    if auto and not sequence and flow is None:
        out.append("auto mode needs kk.sequence or a flow, so the kit plays it once when visible.")
    if not auto and sequence:
        out.append("uses kk.sequence in interactive mode. kk.sequence is for auto mode only, use kk.stepper for learner-driven steps.")

    # Words people read.
    readable = [visible] + lines + flow_texts
    if any("—" in t or " – " in t for t in readable):
        out.append("uses an em dash or en dash as a separator. Use a comma or a period.")
    mirrored = [squash(m) for m in h["mirrors"]]
    if any(
        "->" in l and not any(m in squash(l) or squash(l) in m for m in mirrored)
        for t in readable
        for l in rust_lines(t)
    ):
        out.append("writes `->` in visible text. Write it in words.")
    for t in readable:
        b = BANG.search(t)
        if b:
            at = b.start()
            start = at - 21 if at >= 21 else 0
            out.append(f"uses an exclamation mark (`{squash(t[start : at + 2])}`). Write it flat.")
            break
    return out


def interactive_problems(text):
    """Every problem of every interactive in a Markdown text, checked against that text."""
    fences, prose = scan(text)

    def lines_of(output):
        got = set()
        for tag, body in fences:
            if (tag == "output") if output else (tag != "output" and tag not in NOT_CODE):
                got.update(l.strip() for l in rust_lines(body) if l.strip())
        return got

    ctx = {"code": lines_of(False), "output": lines_of(True), "prose": prose}
    allf = [body for tag, body in fences if tag in FENCES]
    out = []
    for i, src in enumerate(allf):
        name = f"interactive {i + 1}" if len(allf) > 1 else "the interactive"
        out.extend(f"{name} {p}" for p in check_interactive(src, ctx))
    return out


def mermaid_problem(kind):
    return f"the Mermaid diagram `{kind}` is refused. Write the flow as an ```interactive with a flow, so shape and motion stay uniform."


# ---------------------------------------------------------------- gate.rs


def check(steps):
    problems, rows = [], []
    total, hands_on, result, interactives = 0, False, False, 0
    for n, step in enumerate(steps, 1):
        body = step.get("body") or ""
        m = measure(body)
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
        if m["long"]:
            lst = ", ".join(f"{p} ({w} words)" for p, w in m["long"])
            problems.append(f"step {n}: paragraph {lst} has more than {PARAGRAPH_WORDS} words. One paragraph covers one thing.")
        long_blocks = [f"{k} ({l} lines)" for k, l in enumerate(m["blocks"], 1) if l > BLOCK_LINES]
        if long_blocks:
            problems.append(
                f"step {n}: code block {', '.join(long_blocks)} has more than {BLOCK_LINES} lines. Split it into small blocks and explain each right under it."
            )
        if m["joined"]:
            lst = ", ".join(str(k) for k in m["joined"])
            problems.append(
                f"step {n}: code block {lst} follows the previous code block with no explanation between them. Explain the previous block first, then go on to the next."
            )
        if not m["prompt"] and m["code"] + m["output"] + m["images"] + m["diagrams"] == 0:
            problems.append(
                f"step {n} is text only. A concept step needs a visual: a ```mermaid chart, an ```interactive (a moving flow, a slider, step by step), or an illustration from generate_lesson_image (a meme-style panel in the Kiat Koding style is fine). A practice step needs its code and output."
            )
        problems.extend(f"step {n}: {p}" for p in interactive_problems(body))
        problems.extend(f"step {n}: {mermaid_problem(k)}" for k in banned_mermaid(body))
        interactives += m["interactives"]
        if m["interactives"] > PER_STEP:
            problems.append(f"step {n} has {m['interactives']} interactives, at most {PER_STEP} per step.")
        if m["untagged"] > 0:
            problems.append(
                f"step {n}: {m['untagged']} code blocks followed by output do not name their language (`text` or empty). Name it, for example python or javascript, and show output from code that really ran."
            )
        for tag, at, bad in m["syntax"]:
            problems.append(
                f"step {n}: the {tag} block followed by output is not valid at line {at} (`{bad}`). Code with output must be whole code that really ran, in one language, not a fragment or a mix."
            )
        if m["dashes"] > 0:
            problems.append(f"step {n}: the prose uses an em dash or en dash as a separator. Use a comma or a period.")
        if m["prompt"] and m["code"] == 0:
            problems.append(f"step {n} has a prompt but no code. Show the code the agent wrote (the part that matters, with its file name), its diff, or the command it ran.")
        elif shown + visuals > 0 and carried < m["prose"]:
            problems.append(
                f"step {n}: {m['prose']} words of prose, but its {shown} lines of code and output and {visuals} visuals carry only {carried}. "
                f"A line of code or output carries {WORDS_PER_LINE} words, a visual (diagram, chart, interactive, video or image) {VISUAL_WORDS}. "
                "Show more real code, output or visuals, or cut the prose."
            )
    if total > LESSON_WORDS:
        problems.append(f"the lesson has {total} words of prose, the limit is {LESSON_WORDS}. Cut it or make two lessons.")
    if interactives > PER_LESSON:
        problems.append(f"the lesson has {interactives} interactives, at most {PER_LESSON} per lesson.")
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
    if NOT_CHECKED_LOCALLY:
        print(f"syntax not checked here: {', '.join(sorted(NOT_CHECKED_LOCALLY))}. The server checks it.")
    if problems:
        print("\nThe gate would refuse this:")
        print("\n".join(f"- {p}" for p in problems))
        sys.exit(1)
    print("\nThe gate would accept this.")


if __name__ == "__main__":
    main()
