# Latihan (exercise lessons)

A Latihan is a lesson of kind `exercise`: practice items that Kiat Koding draws and scores itself. You write the items as data. You write no HTML and no styling.

## How learners work it

- An attempt shows one item at a time. Nothing says whether an answer is right while the learner works.
- At the end of an attempt the learner sees only the score. Then they pick Ulangi (a new attempt, with options and tiles shuffled again) or Lanjut.
- Lanjut locks the Latihan at the best score of all attempts, marks the lesson done and opens the worked answers: the key, the learner's own answer and each item's `explanation`.
- `min_score` (0 to 100, default 0) holds Lanjut until the best score reaches it. Set it when the Latihan is a chapter checkpoint.
- `draw` asks that many items per attempt, picked at random from `items` and kept in their order. Leave it out to ask every item.
- Every interaction is recorded: items viewed, answers changed, the tab left and come back to.

## Item types

Pick the type that makes the learner do the skill, not one that only recalls a word.

- `arrange`: compose a sentence from word tiles. The tiles of `answer` in order, plus decoys in `extra`. This is how a learner reads code aloud: the code in the prompt, the sentence that reads it as the answer. `accept` lists other right orders built from the same tiles. Keep each tile one word or a short phrase.
- `choice`: `options` with `answer` as the indices of the right ones, from 0. More than one right index makes it a pick-all item. Good for telling apart: what a line prints, which version has the bug.
- `match`: `pairs` of `[left, right]`. The right sides are shuffled. Good for terms and meanings, code and its output, errors and their causes.
- `fill`: `text` with each blank as `[[answer]]` or `[[answer|other accepted answer]]`, compared without case and extra spaces. Set `mono` when the text is code. Good for exact syntax.
- `lines` (a Parsons problem): the program's lines in order in `answer`, indented with spaces as the code is, plus decoy lines in `extra` and the `lang`. The learner places the lines and, by default (`indent` true), sets each line's indentation, so a line in the wrong block is wrong. Good for beginners learning structure: loops, conditions, functions. Make each decoy a real mistake (`return a` where `return hasil` belongs, an off-by-one `range`).
- `code`: the learner writes real code in an editor. Give `lang` (`python` or `javascript`), a `starter` that runs (a signature with `pass`, or a program with a bug to fix), a `solution`, 1 to 5 `examples` the learner sees and runs in the browser, and 3 to 20 hidden `tests`. The item scores the share of hidden tests that pass, run in Kiat Koding's grading lab (no internet, 3 seconds a test) when the attempt ends.
  - A test with `call` evaluates one expression after the code and compares its value: Python as `repr()` (`'halo'`, `90000.0`, `[1, 2]`), JavaScript as JSON (`"halo"`, `90000`, `[1,2]`).
  - A test with `stdin` runs the whole program with that input and compares what it prints, trailing spaces and blank lines at the end ignored. Python reads with `input()`, whose prompt text is printed too, so use `input()` without a prompt. JavaScript reads with `require('fs').readFileSync(0, 'utf8')`.
  - Before saving, the server runs your `solution` against every example and test, and your `starter` against the tests, and refuses when the solution fails one or the starter already passes everything. Take each `expect` from running the solution, never from memory.
  - Cover what the prompt promises: the normal case, the edges it names (zero, empty, negative), and one case a shortcut would get wrong.

Option, tile and pair texts are plain, with `code` in backticks. Prompts and explanations are Markdown: put the code an item is about in a fenced block with its language.

## Rules the server holds through the MCP

- 3 to 30 items. Order them from easy to hard.
- Every item has an `explanation` of at most 80 words: why the answer is right, the thing the learner should take away.
- A question's prose is at most 60 words outside code. Let the code carry it.
- Code in a question is fenced with its language and at most 20 lines. Python, JavaScript and TypeScript must parse whole: a learner reads it as real code.
- A choice item has at least 3 options, a match item at least 3 pairs.
- An arrange item has at least 3 answer tiles and at least 2 decoys, and its sentence must not appear in the question.
- A lines item has `lang`, at least 3 answer lines that parse whole in order (Python, JavaScript, TypeScript) and at least one decoy line, and its program must not appear in the question.
- A code item has a `solution` and `starter` that parse, at least one example and at least 3 hidden tests, and passes the run described above.
- No em dashes or en dashes as separators.
- The intro is at most 120 words, and `draw` is at least 3 when set.

## Example

```json
{
  "kind": "exercise",
  "title": "Latihan: membaca loop",
  "intro": "Lima soal tentang membaca loop dan operator pembanding.",
  "min_score": 60,
  "items": [
    {
      "type": "arrange",
      "prompt": "Baca kode ini sebagai kalimat:\n\n```python\nfor angka in daftar:\n    print(angka)\n```",
      "answer": ["untuk", "setiap", "angka", "di", "daftar,", "cetak", "angka"],
      "extra": ["jumlahkan", "sebelum", "semua"],
      "explanation": "`for` mengambil isi `daftar` satu per satu ke `angka`, lalu `print` mencetaknya."
    },
    {
      "type": "choice",
      "prompt": "Apa yang dicetak kode ini?\n\n```python\nx = 3\nx = x + 2\nprint(x)\n```",
      "options": ["3", "5", "x + 2", "32"],
      "answer": [1],
      "explanation": "Baris kedua mengganti isi `x` jadi 3 + 2."
    },
    {
      "type": "match",
      "prompt": "Pasangkan operator dengan artinya.",
      "pairs": [["`==`", "sama dengan"], ["`!=`", "tidak sama dengan"], ["`>=`", "lebih dari atau sama dengan"]],
      "explanation": "Ketiganya operator pembanding, hasilnya `True` atau `False`."
    },
    {
      "type": "fill",
      "prompt": "Lengkapi supaya kode mencetak 1 sampai 3.",
      "text": "for i in [[range]](1, [[4]]):\n    print(i)",
      "mono": true,
      "explanation": "`range(1, 4)` berhenti sebelum 4."
    },
    {
      "type": "lines",
      "lang": "python",
      "prompt": "Susun fungsi yang menjumlahkan isi daftar.",
      "answer": ["def total(angka):", "    hasil = 0", "    for a in angka:", "        hasil += a", "    return hasil"],
      "extra": ["    return a", "        hasil = a"],
      "explanation": "`return` sejajar dengan `for`, jadi baru jalan setelah semua angka dijumlahkan."
    },
    {
      "type": "code",
      "lang": "python",
      "prompt": "Lengkapi `diskon(harga, persen)` supaya mengembalikan harga setelah dipotong `persen` persen.",
      "starter": "def diskon(harga, persen):\n    return harga\n",
      "solution": "def diskon(harga, persen):\n    return harga - harga * persen / 100\n",
      "examples": [{ "call": "diskon(100000, 10)", "expect": "90000.0" }],
      "tests": [
        { "call": "diskon(50000, 20)", "expect": "40000.0" },
        { "call": "diskon(80000, 0)", "expect": "80000.0" },
        { "call": "diskon(1000, 100)", "expect": "0.0" }
      ],
      "explanation": "Potongannya `harga * persen / 100`, lalu harga dikurangi potongan itu."
    }
  ]
}
```

`update_lesson` with `items` replaces the whole list. Writing in the items follows [writing.md](writing.md).
