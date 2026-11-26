# Writing a codelab

A codelab (`kind: codelab`, with `steps`) is a hands-on tutorial in numbered steps, in the style of Google Codelabs. The learner sees one step at a time with the list of steps beside it, and marks the lesson done on the last step. Use it for anything the learner does, and for reading lessons too (there is no text lesson kind): there each step is one section of the explanation, titled by what it explains. A codelab with a single step shows as a plain page, with no step list.

Code and real output carry a codelab. Prose frames them. A learner who skims only the code blocks and the output should still be able to follow the lesson.

## The gate

The server checks every codelab an agent saves with `add_lesson` or `update_lesson`, and refuses it with the full list of problems when it reads long or shows little code. Prose is everything outside fences, tables and image lines.

- At most 250 words of prose per step, and 1,500 per lesson.
- Paragraphs of at most 70 words. Each list item counts as its own paragraph.
- A step with a ```prompt fence also shows the code the agent wrote, a diff, or the command it ran.
- A code block holds at most 10 lines, and two code blocks never follow each other without prose between them. An ```output block may follow its command directly. Output blocks have no line limit.
- A step with code or a prompt carries a line of code or output for every 20 words of its prose. Prompt, Mermaid and video lines do not count as code.
- A lesson with code shows a real result: an ```output fence or a screenshot.

Fix every point in the refusal and send the lesson again. Changing a lesson's steps checks the whole lesson, so an older long lesson has to be rewritten before any of its steps can change. The limits are ceilings, not targets: most steps need 80 to 200 words.

## Steps

- One step is one task the learner finishes before moving on, and it ends in a result they can see. If a step needs two different results, split it.
- The title is short and imperative: "Siapkan project", "Minta agent membuat endpoint login", "Uji dengan data kosong".
- `minutes` is an honest estimate of the time a learner at the course's level needs, including waiting for an agent or a build. Do not round everything to 5.
- Most codelabs fit in 4 to 8 steps and 15 to 25 minutes. A codelab holds at most 60 steps, but a lesson that needs more than 1,500 words of prose is two lessons.
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

A step that explains an idea instead of building something has no code, so only the length limits apply. Keep it to what the next hands-on step needs: a short explanation, a diagram or an illustration, and a small example when one exists (a request, a snippet). The learner should run something in the course's first or second lesson, not after a chapter of theory.

## Visuals

- A screenshot after each visible result, with a one-line caption.
- A ```mermaid flowchart for any flow with three or more parts (request to response, build pipeline, agent loop).
- One illustration (`generate_lesson_image`) per concept that is hard to picture, not one per step.

## What makes it premium

Not length. Real numbers you measured, screenshots from a real run, a finished project the learner can download chapter by chapter, and an honest line when a result can differ.
