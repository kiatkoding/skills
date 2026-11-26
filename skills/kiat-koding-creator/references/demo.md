# Writing a demo

A ```demo fence is an interactive demo inside a lesson: motion or interaction that a still picture cannot show. Examples are a flow that animates step by step, a slider that changes a result while the learner watches, or an algorithm stepping through its data. The lesson page runs it in an isolated frame at the column's width, and the frame grows to fit what you draw. It counts as one visual for the gate, like a Mermaid diagram.

Use a demo when moving or touching the idea teaches more than looking at it. A flow that reads fine as boxes and arrows stays a ```mermaid diagram, and numbers that only need comparing stay a chart.

## What to write

Write an HTML fragment with inline `<svg>` or `<canvas>`, `<style>` and `<script>`. Leave out `<html>`, `<head>` and `<body>`: the frame supplies them, with Kiat Koding's fonts and design system already loaded.

- Design for 320px up to the column's width. Give every `<svg>` a `viewBox` so it scales.
- Text inside an `<svg>` scales with its `viewBox`. Put labels and numbers in HTML around the drawing, or size the `viewBox` near the width it shows at (about 640).
- Don't use `vh` heights. The frame takes its height from your content, so a height based on the frame never settles.
- Under reduced motion (`kk.reducedMotion`), show the end state, or move one step per click instead of looping.
- Labels are Indonesian, like the rest of the lesson.

## The design system

A demo must look like the rest of Kiat Koding, a 1980s computer manual. Take every colour, font and spacing from the design system the frame provides.

| For | CSS | Script |
|---|---|---|
| The frame's white ground | `var(--color-paper-3)` | `kk.color.paper3` |
| Panels | `var(--color-paper)`, `var(--color-paper-2)` | `kk.color.paper`, `kk.color.paper2` |
| Headings, key lines | `var(--color-ink-strong)` | `kk.color.inkStrong` |
| Text, outlines | `var(--color-ink)` | `kk.color.ink` |
| Muted labels | `var(--color-ink-2)` | `kk.color.ink2` |
| Grid lines | `var(--color-rule)`, `var(--color-rule-strong)` | `kk.color.rule`, `kk.color.ruleStrong` |
| The one thing to look at | `var(--color-accent)` | `kk.color.accent` |
| States | `var(--color-ok)`, `var(--color-warn)`, `var(--color-ok-bg)`, `var(--color-warn-bg)` | `kk.color.ok`, `kk.color.warn`, `kk.color.okBg`, `kk.color.warnBg` |
| Data series, in this order | `var(--color-series-1)` to `var(--color-series-4)` | `kk.series[0]` to `kk.series[3]` |
| Fonts | `var(--font-body)`, `var(--font-display)` for headings, `var(--font-mono)` for numbers and labels | `kk.font.body`, `kk.font.display`, `kk.font.mono` |
| Spacing, borders | `var(--space-2xs)` to `var(--space-xl)`, `var(--rule-ink)` (2px ink border), `var(--shadow-hard)` | |

The script values are hex, for a canvas and for chart libraries that cannot read the site's colour format: `ctx.fillStyle = kk.color.accent`, ``ctx.font = `14px ${kk.font.mono}` ``, `d3.rgb(kk.color.ink)`.

Plain controls already wear the site's style: `<button>` (add `class="primary"` for the main one), `<input>`, `<select>`, range sliders and tick boxes. These classes are also ready to use:

- `.row` lays controls out in a wrapping row.
- `.box` is a 2px ink frame on paper.
- `.label` is a small mono capital label.
- `.mono` sets mono figures.
- `.muted` sets muted text.

Use square corners, 2px ink outlines, hard offset shadows and flat fills. No rounded cards, gradients, glows or soft shadows. The accent marks one thing at a time.

## What the server refuses

The server checks every demo an agent saves, in any Markdown field, and refuses it with the reason:

- A colour value: hex (`#b2422c`), `rgb()`, `hsl()`, `oklch()` and the like, or a colour name such as `red` in a style, an attribute or a script. Use the variables or `kk.color` instead.
- A font name. Use `var(--font-...)`, `.mono` or `kk.font`.
- A script from anywhere but `https://cdnjs.cloudflare.com`, or any other outside address. Images come from `/uploads/` paths (`generate_lesson_image`, `create_image_upload`).
- `<html>`, `<head>`, `<body>`, `<meta>`, `<link>`, `<iframe>`, `<object>` or `<embed>`.
- The network (`fetch`, `XMLHttpRequest`, `WebSocket`), storage (`localStorage`, `document.cookie`) and `alert`, `confirm` or `prompt`. The frame has none of them, so write the data into the script and show messages inside the demo.
- More than 30,000 characters.

The skill's `scripts/check_codelab.py` runs the same checks on a codelab's steps.

## Example

````markdown
```demo
<div class="row">
  <label class="label" for="ambang">Ambang confidence</label>
  <input id="ambang" type="range" min="0" max="100" value="60">
  <output id="nilai" class="mono">0.60</output>
</div>
<svg viewBox="0 0 640 220" role="img" aria-label="Komentar yang lolos dan yang ditahan">
  <line x1="0" y1="200" x2="640" y2="200" stroke="var(--color-ink)" stroke-width="2"/>
  <rect id="lolos" x="80" width="160" fill="var(--color-series-1)"/>
  <rect id="ditahan" x="400" width="160" fill="var(--color-series-2)"/>
</svg>
<p class="muted">Kiri: komentar yang lolos. Kanan: komentar yang ditahan untuk dicek manusia.</p>
<script>
const ambang = document.getElementById('ambang');
const gambar = () => {
  const v = ambang.value / 100;
  document.getElementById('nilai').textContent = v.toFixed(2);
  for (const [id, tinggi] of [['lolos', 180 * (1 - v)], ['ditahan', 180 * v]]) {
    const bar = document.getElementById(id);
    bar.setAttribute('height', tinggi);
    bar.setAttribute('y', 200 - tinggi);
  }
};
ambang.addEventListener('input', gambar);
gambar();
</script>
```
````

The learner sees the demo under a DEMO strip with Kode, which shows its source, and Ulangi, which restarts it.
