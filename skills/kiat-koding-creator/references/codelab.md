# Writing a codelab

A codelab (`kind: codelab`, with `steps`) is a hands-on tutorial in numbered steps, in the style of Google Codelabs. The learner sees one step at a time with the list of steps beside it, and marks the lesson done on the last step. Use it for anything the learner does, and for reading lessons too (there is no text lesson kind): there each step is one section of the explanation, titled by what it explains. A codelab with a single step shows as a plain page, with no step list.

Code and real output carry a codelab. Prose frames them. A learner who skims only the code blocks and the output should still be able to follow the lesson.

## The gate

The server checks every codelab an agent saves with `add_lesson` or `update_lesson`, and refuses it with the full list of problems when it reads long or shows little code. Prose is everything outside fences, tables and image lines.

- At most 1,000 words of prose per step, and 3,000 per lesson.
- Paragraphs of at most 70 words. Each list item counts as its own paragraph.
- A step with a ```prompt fence also shows the code the agent wrote, a diff, or the command it ran.
- A code block holds at most 10 lines, and two code blocks never follow each other without prose between them. An ```output block may follow its command directly. Output blocks have no line limit.
- Prose is carried by what the step shows: every 20 words need a line of code or output, or every 200 words a visual (a Mermaid chart or diagram, an interactive, a video, an image). Prompt, Mermaid, interactive and video lines do not count as code lines. Text alone is refused.
- An ```interactive follows its own rules (a header, the step's real code or data, motion, the design system), at most one per step and two per lesson. See [interactive.md](interactive.md). Mermaid `sequenceDiagram` and `stateDiagram` are refused.
- A code block followed by an ```output names its language (python, javascript, bash...), never `text` or nothing.
- No em dashes or en dashes as separators.
- A lesson with code shows a real result: an ```output fence or a screenshot.

Fix every point in the refusal and send the lesson again. Changing a lesson's steps checks the whole lesson, so an older long lesson has to be rewritten before any of its steps can change. The limits are ceilings, not targets: most pages carry 400 to 800 words.

## Passing the gate the first time

What the gate counts:

- Prose is every word outside fences, tables and image lines. Captions, callouts, list items, headings and inline code all count. A link counts its text, not its address.
- Code and output lines are the non-empty lines inside code fences and ```output fences. Lines in ```prompt, ```mermaid, ```interactive and ```video fences are not code, and an interactive has no line limit.
- A step's prose allowance is 20 words per line of code and output plus 200 words per visual, never more than 1,000. One command with two lines of output allows 60 words. Add a diagram and it allows 260.
- A concept part needs a visual for every 200 words of its reasons. A page that mixes concept and code adds both allowances together.

Before sending a lesson, write its `steps` array to a JSON file and run the checker that ships with this skill. It mirrors the server's rules, prints each step's words, lines and allowance, and lists every problem the server would report:

```bash
python3 <this skill's folder>/scripts/check_codelab.py steps.json
```

The refusals that come up most, and what fixes them:

| Refusal | Fix |
|---|---|
| A short command with a long explanation | Put the why next to a diagram that shows it, show the real output, or cut the prose. Never pad code or output to raise the allowance. |
| A code block over 10 lines | Split it where the idea changes (a request's state and its questions, the loop and the error branch) and explain each part right under it. |
| Two code blocks in a row | Put a sentence between them: what the next block does, or how to run the one before. |
| A step that is text only, such as a checklist, a table or a summary | A table is not a visual. Add an ```interactive, a Mermaid chart, or an image from `generate_lesson_image`. |
| An interactive without a header, task or mirrors | Start it with the header comment, and copy the lines it shows from the step's code or output. See [interactive.md](interactive.md). |
| An interactive that writes a colour or a font | Take it from the design system: `var(--color-...)` and `var(--font-...)` in CSS, `kk.color`, `kk.series` and `kk.font` in a script. |
| An interactive that does not move | Give what changes a transition of 150 to 1000 ms with `var(--ease-out)`, or use a flow. |
| SVG text too small on a phone | Write the words in HTML around the drawing. |
| A code block with `text` before an output | Name its language and show the output of actually running it. |
| A paragraph over 70 words | Split it where the second idea starts. |
| A prompt without code | Show the code the agent wrote, a diff, or the command it ran. |

Plan the pages before writing: one page per context, usually 5 to 7 per lesson. Learners click Next to move to a new context, not to read the next paragraph of the same one, so a lesson of 15 short pages is worse than 6 long ones.

## Steps

- One step is one page about one context: a concept with its examples, or a task with its prompt, code, command and output. It may scroll as long as it stays on that context. Start a new step only where the context or the runnable goal changes. Most lessons have 5 to 7 steps, rarely more than 8.
- A long page is split into parts with `###` subheadings, one per sub-task or idea, so the learner can scan it. Each part follows the beats below.
- The title is short and imperative: "Siapkan project", "Minta agent membuat endpoint login", "Uji dengan data kosong".
- `minutes` is an honest estimate of the time a learner at the course's level needs, including waiting for an agent or a build. Do not round everything to 5.
- A typical page carries 400 to 800 words of prose, at most 1,000, and runs two to five screens. A lesson that needs more than 3,000 words of prose is two lessons.
- The first step says what the learner will have at the end, ideally by showing it (the final output or a screenshot), and what they need ready. The last step sums up what they built and what comes next.

## Inside a step

Write the beats in this order, as short paragraphs and code blocks, without turning them into sub-headings:

1. The goal, in one or two sentences: what this step produces and why it is needed now.
2. The action: the prompt in a ```prompt fence when an agent does the work, or the code the learner writes.
3. The code, block by block. When an agent did the work, show the code it wrote: the part that matters (the function, the request, the config), not the whole file. Split it into small blocks, one idea each (the loop, the error branch, the retry), and explain each block right under it in a sentence or two before the next block starts. The code already shows what it does, so the explanation says why it is written that way or what to check. The first block carries the file path as a comment line. A ```diff fence fits a change to existing code.
4. The command that runs it, in a ```bash fence.
5. The real output in an ```output fence, or a screenshot when the result is visual.

When a result often differs (versions, an API's wording, an agent's own choices), add one line on what to check, or a `> [!TIP]`. Background the step does not need belongs in a concept step or a separate reading lesson.

## An example step

````markdown
Klien ini satu-satunya bagian pipeline yang nge-call API. Kirim prompt ini ke opencode:

```prompt
Buat src/decision_lab/jev.py dengan fungsi ask(state, questions) yang nge-call Jev, timeout 30 detik,
retry dengan backoff kalau dapat HTTP 429 atau 529, lalu me-return answers dan usage.
Belum perlu dijalankan ke API, cukup pastikan tidak ada error.
```

Baris yang menentukan hasilnya: status retry ditulis jelas, 429 dan 529. Tanpa itu, agent bisa ikut mengulang 400, yang pasti gagal lagi.

Agent menulis `ask()` dengan loop retry. Bagian pertama mengirim request:

```python
# src/decision_lab/jev.py
for attempt in range(4):
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
```

Loop ini mencoba paling banyak empat kali, dan setiap percobaan menunggu response paling lama 30 detik.

```python
    except HTTPError as exc:
        status = exc.code
        exc.close()
        if status in {429, 529} and attempt < 3:
            time.sleep(2**attempt)
            continue
```

Hanya 429 dan 529 yang dicoba lagi. `2**attempt` memberi jeda 1, 2, lalu 4 detik.

```python
        raise JevError(f"Jev request failed with HTTP {status}.") from None
```

Status lain langsung gagal. `from None` membuang detail error aslinya, jadi log cuma berisi status HTTP.

Cek tanpa nge-call API:

```bash
uv run python -m unittest tests.test_jev
```

```output
.......
----------------------------------------------------------------------
Ran 7 tests in 0.002s

OK
```
````

About 100 words of prose around 17 lines of code and output, each code block explained before the next one starts.

## What to cut

- Describing an image or a screenshot again in prose. Its caption says what it shows, in one line.
- Explaining a prompt line by line. Explain only the line that changes the result.
- Restating what the code or the output already shows.
- Walking through every field of a JSON block in paragraphs. Point at the two or three fields that matter.
- History, alternatives and caveats the step does not need to succeed.

## Prompts for a coding agent

- A prompt states the goal, the constraints and the decisions the learner made. It does not dictate code line by line, since the learner is learning to direct an agent.
- Show what the agent wrote, then review it in a few notes: what is right, what to watch, what to ask the agent to change. The learner learns to read the code, not only to ask for it.
- When a prompt line carries a decision ("use SQLite, not a JSON file"), explain the decision in one sentence.
- Keep technical names in English (file names, identifiers, commands, error messages). The explanation around them is Indonesian.

## Commands and code

- Put commands the learner types in a ```bash fence, one command per line, without a `$` prompt so the copy button gives a working command.
- Show the code the step is about, under its file name. Put the full project up as a download (`create_file_upload`), one zip per chapter once the code grows, so the learner can compare their files with yours.
- Never present output you did not see. If the exact output depends on the learner's machine, show a representative output and say which parts differ.

## Concept steps

A step that explains an idea instead of building something needs no code, but it carries a visual where a hands-on step carries code:

- An ```interactive flow for anything that happens in order (a request and its response, a build pipeline, an agent loop). In auto mode it plays once as it scrolls into view, ending on the whole diagram. See [interactive.md](interactive.md).
- An ```interactive for code traced line by line, a value that changes as the learner acts, or an algorithm walking through its data, with a task the learner guesses or reaches first.
- A Mermaid diagram (`flowchart TD`) only for a structure where nothing happens in order.
- A chart for numbers, drawn by Mermaid so every number is exact: `pie` for shares, `xychart-beta` for bars or lines (time, cost, accuracy). For dates in order, use a `flowchart TD` with one box per date: Mermaid's `timeline` draws its text too small to read.
- An illustration from `generate_lesson_image` for an idea that is hard to picture.
- A light meme-style panel from `generate_lesson_image` when a joke makes the point stick, such as the moment a learner recognises from their own work. Draw an original joke in the Kiat Koding look. Never copy a known meme template or show a real person.

Keep the step to what the next hands-on step needs, with a small example when one exists (a request, a snippet). The learner should run something in the course's first or second lesson, not after a chapter of theory.

## Visuals

- A screenshot after each visible result, with a one-line caption.
- An ```interactive flow for any flow with three or more parts (request to response, build pipeline, agent loop).
- One illustration (`generate_lesson_image`) per concept that is hard to picture, not one per step.

## What makes it premium

Not length. Real numbers you measured, screenshots from a real run, a finished project the learner can download chapter by chapter, and an honest line when a result can differ.
