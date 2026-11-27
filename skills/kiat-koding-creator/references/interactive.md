# Writing an interactive

An ```interactive fence shows what a still picture cannot: a process playing out in order, a value changing as the learner acts, things moving between places. The lesson page runs it in an isolated frame at the column's width. The frame grows to fit what you draw, and the frame gives you Kiat Koding's design system and a small kit. It counts as one visual for the gate. A step holds at most one interactive, and a lesson at most two.

Use one when moving or touching the idea teaches more than looking at it. Every diagram of boxes and arrows is an interactive flow: a process in order plays its stages, and a structure shows its parts one group at a time. Mermaid is for charts only (`pie`, `xychart-beta`): its flowcharts (`flowchart`, `graph`), sequence and state diagrams are refused.

The server checks every interactive an agent saves and refuses it with the reasons. Run `scripts/check_codelab.py` on the steps first, since it makes the same checks.

## The header

Every interactive starts with a header comment. The server holds the interactive to it, and the frame reads its mode and task.

```html
<!--
mode: interactive
shows: sequence, change
teaches: Di setiap putaran, price berganti ke item berikutnya dan total bertambah sebanyak price.
task: Berapa isi total setelah putaran kedua?
answer: 35000
mirrors:
for price in prices:
    total = total + price
-->
```

- `mode`: `interactive` when the learner acts, `auto` when it plays once by itself as it scrolls into view.
- `shows`: what happens in it, one or more of `sequence` (things in order), `change` (a value changes), `movement` (things move between places), `structure` (nothing changes). The server compares it with what the interactive does.
- `teaches`: one sentence, at most 25 words, on what it makes visible.
- `task`: interactive mode only, at most 30 words. The frame shows it at the top. It is either a question the learner guesses before acting (ending with ?) or a goal to reach, shown as written without a label. Auto mode has no task.
- `answer`: required when the task is a question. A numeric answer must not be readable before the learner acts.
- `mirrors`: required when the step has code or output blocks. List lines copied exactly from them that the interactive shows. A code line must appear in the interactive as written, with the same names and values. An output line may be computed by the interactive, but its names and numbers must be there.

## The kit

Use the kit instead of building your own. The server refuses hand-made next, back and reset buttons.

### Flow diagrams

A flow is data, not drawing. The kit draws it in the house style: boxes top to bottom, arrows drawn as each stage reveals them, and every label on its own arrow with room made for it. Arrows between neighbouring rows run in the gap between them, both ways, a reply beside its request. Arrows that skip a row or go further back up run in lanes at the right. You never place anything yourself. Auto mode plays it once when it is visible. Interactive mode steps through it with Sebelumnya and Berikutnya.

```html
<script type="application/json" data-kk="flow">
{"rows": [[{"id": "browser", "label": "Browser", "note": "GET /api/me"}],
          [{"id": "server", "label": "Server", "note": "cek sesi"}]],
 "edges": [{"from": "browser", "to": "server", "label": "request"},
           {"from": "server", "to": "browser", "label": "response JSON"}],
 "stages": [{"caption": "Browser mengirim request.", "show": ["browser"]},
            {"caption": "Server menerima dan membalas.", "show": ["server", "browser>server", "server>browser"]}]}
</script>
```

- 1 to 8 rows, each with 1 to 4 nodes.
- Node ids use lowercase letters, digits, `-` or `_`, up to 24 characters. Labels are up to 32 characters, notes up to 60.
- Edge labels are up to 24 characters.
- 2 to 10 stages. Each stage shows something new, with a caption of up to 140 characters.
- An edge is shown as `"from>to"`, and no earlier than both its nodes.
- By the last stage every node and edge is shown, so the diagram ends complete.

### Steppers and sequences

For your own drawing, describe the stages and let the kit run them. Each stage has a `caption` and a `show()` that draws that stage's whole state, so stepping back works.

- `kk.stepper([{caption, show() {...}}, ...])` is for interactive mode. It adds Sebelumnya, Berikutnya and the position ("3/9") under the interactive, or inside an element marked `data-kk="controls"`.
- `kk.sequence([{caption, show() {...}}, ...])` is for auto mode. It plays once when visible, takes at most 12 seconds in all and ends on the last stage. Under reduced motion it jumps straight to the end.

### Code, states and ready classes

- Show code as `<pre class="kk-code">` with one `<span>` per line. Put class `is-current` on the running line.
- Mark the current part of your own drawing with `is-current`, parts already passed with `is-done`, and parts out of play with `is-off`.
- Buttons, inputs, selects and range sliders already wear the site's style. Use class `primary` for the main button.
- Ready classes: `.row` lays controls in a wrapping row, `.box` is a 2px ink frame, `.label` a small mono capital label, `.mono` mono figures, `.muted` muted text.

## The design system

An interactive must look like the rest of Kiat Koding, a 1980s computer manual. Take every colour, font and spacing from the design system the frame provides.

| For | CSS | Script |
|---|---|---|
| The frame's white ground | `var(--color-paper-3)` | `kk.color.paper3` |
| Panels | `var(--color-paper)`, `var(--color-paper-2)` | `kk.color.paper`, `kk.color.paper2` |
| Headings, key lines | `var(--color-ink-strong)` | `kk.color.inkStrong` |
| Text, outlines | `var(--color-ink)` | `kk.color.ink` |
| Muted labels | `var(--color-ink-2)` | `kk.color.ink2` |
| Grid lines | `var(--color-rule)`, `var(--color-rule-strong)` | `kk.color.rule`, `kk.color.ruleStrong` |
| The one thing to look at | `var(--color-accent)` | `kk.color.accent` |
| Success and failure only | `var(--color-ok)`, `var(--color-warn)`, `var(--color-ok-bg)`, `var(--color-warn-bg)` | `kk.color.ok`, `kk.color.warn`, `kk.color.okBg`, `kk.color.warnBg` |
| Data series, in this order | `var(--color-series-1)` to `var(--color-series-4)` | `kk.series[0]` to `kk.series[3]` |
| Fonts | `var(--font-body)`, `var(--font-display)` for headings, `var(--font-mono)` for numbers and labels | `kk.font.body`, `kk.font.display`, `kk.font.mono` |
| Spacing, borders | `var(--space-2xs)` to `var(--space-xl)`, `var(--rule-ink)` (2px ink border), `var(--shadow-hard)` | |

- The script values are hex, for a canvas and for chart libraries that cannot read the site's colour format.
- Use square corners, 2px ink outlines, hard offset shadows and flat fills. No rounded cards, gradients, glows or soft shadows.
- `--color-ok` and `--color-warn` mark success and failure only, in classes named for them (ok, error, salah and the like). A highlight is `is-current`, never green.

## What the server refuses

### Motion

Motion is required when `shows` names sequence, change or movement.
- What changes moves with a CSS transition or animation of 150 to 1000 ms using `var(--ease-out)`. The kit animates its own parts.
- Nothing runs `infinite`.
- Animation driven by a script (`setInterval`, a `requestAnimationFrame` loop, `animate()`) checks `kk.reducedMotion` and shows the end state when it is true.

### Reading

- Words go in HTML, not in `<svg>`. SVG text that would render under 11px on a 320px phone is refused. For example, a viewBox 640 wide needs a font-size of at least 25.
- Every `<svg>` has `role="img"` and an `aria-label`. Every input has a `<label>`.

### Controls

- At most 4 buttons, with at most 36 characters of labels in all. Beyond that, use a select or a slider.
- Labels are written in sentence case.
- The step's prose does not explain how to operate the interactive, and does not repeat its button labels.

### Writing

- No exclamation marks.
- No `->` in visible text, unless it is part of a mirrored code line.
- No em dashes or en dashes used as separators.
- Labels in Indonesian.

### The frame

- No colour values (hex, `rgb()`, `hsl()`, `oklch()`, or names such as `red`) and no font names.
- Scripts load only from `https://cdnjs.cloudflare.com`. Images come only from `/uploads/` paths.
- No `<html>`, `<head>`, `<body>`, `<meta>`, `<link>` or frames.
- No network, storage, `alert`, `confirm` or `prompt`.
- At most 30,000 characters.

## Example: a flow that plays once

````markdown
```interactive
<!--
mode: auto
shows: sequence, movement
teaches: Satu request berjalan dari browser ke server dan database, lalu jawabannya kembali lewat jalur yang sama.
-->
<script type="application/json" data-kk="flow">
{"rows": [[{"id": "browser", "label": "Browser", "note": "GET /api/me"}],
          [{"id": "server", "label": "Server", "note": "cek sesi"}],
          [{"id": "db", "label": "Database", "note": "tabel users"}]],
 "edges": [{"from": "browser", "to": "server", "label": "request"},
           {"from": "server", "to": "db", "label": "query"},
           {"from": "db", "to": "server", "label": "baris user"},
           {"from": "server", "to": "browser", "label": "response JSON"}],
 "stages": [{"caption": "Browser mengirim request ke alamat /api/me.", "show": ["browser"]},
            {"caption": "Server menerima request dan memeriksa sesinya.", "show": ["server", "browser>server"]},
            {"caption": "Server menanyakan data user ke database.", "show": ["db", "server>db"]},
            {"caption": "Database mengembalikan satu baris user.", "show": ["db>server"]},
            {"caption": "Server membungkus data itu jadi JSON dan mengirimnya ke browser.", "show": ["server>browser"]}]}
</script>
```
````

## Example: tracing code line by line

The step shows the code and its real output in its own blocks, then this:

````markdown
```interactive
<!--
mode: interactive
shows: sequence, change
teaches: Di setiap putaran, price berganti ke item berikutnya dan total bertambah sebanyak price.
task: Berapa isi total setelah putaran kedua?
answer: 35000
mirrors:
prices = [10000, 25000, 15000]
total = 0
for price in prices:
    total = total + price
print(total)
-->
<pre class="kk-code"><span>prices = [10000, 25000, 15000]</span>
<span>total = 0</span>
<span>for price in prices:</span>
<span>    total = total + price</span>
<span>print(total)</span></pre>
<table class="vars">
  <tr><th class="label">prices</th><td id="v-prices" class="mono"></td></tr>
  <tr><th class="label">price</th><td id="v-price" class="mono"></td></tr>
  <tr><th class="label">total</th><td id="v-total" class="mono"></td></tr>
  <tr><th class="label">output</th><td id="v-out" class="mono"></td></tr>
</table>
<style>
  .vars { border-collapse: collapse; width: 100%; }
  .vars th { width: 6rem; padding: var(--space-2xs) var(--space-xs); text-align: left; border-bottom: 1px solid var(--color-rule); }
  .vars td { padding: var(--space-2xs) var(--space-xs); border-bottom: 1px solid var(--color-rule); transition: background-color 300ms var(--ease-out); }
  .vars td.is-current { background: var(--color-paper-2); box-shadow: inset 4px 0 0 var(--color-accent); }
</style>
<script>
const lines = [...document.querySelectorAll('.kk-code > span')];
const plan = [
  [0, { prices: '[10000, 25000, 15000]' }, 'Baris 1 membuat list prices berisi tiga harga.'],
  [1, { total: '0' }, 'Baris 2 menyiapkan total dengan nilai awal 0.'],
  [2, { price: '10000' }, 'Putaran 1: price berisi item pertama.'],
  [3, { total: '10000' }, 'total ditambah price.'],
  [2, { price: '25000' }, 'Putaran 2: price berganti ke item kedua.'],
  [3, { total: '35000' }, 'total ditambah price lagi.'],
  [2, { price: '15000' }, 'Putaran 3: price berisi item terakhir.'],
  [3, { total: '50000' }, 'total ditambah price untuk ketiga kalinya.'],
  [4, { out: '50000' }, 'List habis, loop selesai, dan print menampilkan total.'],
];
let vars = {};
const states = plan.map(([line, change, caption]) => {
  vars = { ...vars, ...change };
  return { line, vars, changed: Object.keys(change), caption };
});
kk.stepper(states.map((s) => ({
  caption: s.caption,
  show() {
    lines.forEach((el, i) => el.classList.toggle('is-current', i === s.line));
    for (const name of ['prices', 'price', 'total', 'out']) {
      const cell = document.getElementById('v-' + name);
      cell.textContent = s.vars[name] ?? '';
      cell.classList.toggle('is-current', s.changed.includes(name));
    }
  },
})));
</script>
```
````

The learner reads the real code, guesses first, then steps through it and sees each value change where it changes.
