# Designing a Submission

A Submission (`kind: submission`) is a graded project. The learner builds it milestone by milestone, Kiat Koding's AI reviews the final code against the milestones and scores how the learner worked, the learner answers defense questions about their own code, and the instructor gives the final grade. A Submission is done only when it passes, and the lessons after it stay locked until then.

## Where the learner works: `workspace`

- `agent` (default): on the learner's own computer, with the coding agent of their choice (Claude Code, Codex CLI, opencode, Cursor and others). A local recorder logs each request to the agent and every code change. Use it for projects that are naturally built with an agent: web apps, APIs, scripts.
- `lab`: in the Coding Lab, an editor and a real Linux terminal in the browser, with nothing to install. The learner types the work themselves, without an agent. Each learner gets 2 hours of lab per day. Use it when the skill is the tool itself, which an agent would do for them: Git, the command line, first steps in Python, debugging.

The workspace cannot change once a learner has started.

## Brief

`brief` is the only part the learner sees before starting. Say what they build, for whom or why, the stack, and what "done" looks like overall. Keep the milestones out of it.

## Milestones

Each milestone has a `title`, a `task`, optional `hints` and an optional `change`. The learner gets one milestone at a time.

- In `agent` Submissions, write the task as an outcome that can be seen in the code, since the AI review reads the final code and the changes up to each milestone against it. "Item bisa ditandai sudah dibeli dan tetap tersimpan setelah halaman dimuat ulang" can be judged. "Rapikan kodenya" cannot.
- In `lab` Submissions, the learner reads the task beside the lab, so write it as a plain instruction in Indonesian with "kamu".
- 3 to 6 milestones suit most projects. Each one builds on the previous.
- `hints` are served one at a time on request, from gentle to specific, and each one used is recorded. Two or three per milestone is enough. The last may name the concept or the command, but never the full answer.
- `change` is a requirement change served when the milestone is done, like a client changing their mind. Use it once or twice per Submission to see how the learner adapts.

## Grading

- `pass_score`: default 70.
- `defense_questions`: default 4. The questions are generated from the learner's own code after hand-in.
- The final score combines the result, the process and the defense. The default weights follow the course level (beginner 35, 25 and 40, intermediate 40, 30 and 30, expert 40, 35 and 25), and the instructor can change them per course in the admin.
- The process score judges who set the direction: requests that carry the learner's own decisions score higher than accepting the agent's plans. Its aspects are decomposition, context, verification, iteration and decisions. Design milestones that leave real decisions to the learner.

## Coding Lab settings (`workspace: lab`)

- `setup`: a bash script run once in `~/project`, as the learner, when an attempt's lab is first made. Build the starting point with it: a git repository with commits and branches, a conflict waiting to happen, files to fix. Keep it idempotent and quiet. Example: `git init -q -b main && git config user.name Kiat && git config user.email kiat@localhost && printf 'halo\n' > catatan.txt && git add . && git commit -qm awal`.
- `packages`: tools beyond the base image (Debian with git, Python 3 and curl). Debian package names (`nodejs`, `sqlite3`), `pip:<name>` and `npm:<name>`. Prefer this over installing in `setup`.
- `internet`: off by default. Turn it on only when the lesson needs it, and list the domains in `hosts`, for example `github.com` and `githubusercontent.com` for GitHub, or `pypi.org` and `pythonhosted.org` for pip.
- `checks` per milestone: bash commands run in the learner's lab when they say the milestone is done. Each passes when it exits 0 within 30 seconds, and every one must pass. Check the state, not the way it was reached. Each check has a `fail` message in Indonesian with "kamu" that says what is still missing without giving the command away.

Check examples:

| run | fail |
|---|---|
| `git rev-parse -q --verify HEAD >/dev/null` | Belum ada commit. |
| `git rev-parse --verify -q fitur` | Branch fitur belum ada. |
| `git merge-base --is-ancestor fitur main` | Perubahan dari branch fitur belum masuk ke main. |
| `! grep -rq '<<<<<<<' .` | Masih ada konflik yang belum diselesaikan. |
| `test "$(git log --oneline \| wc -l)" -ge 3` | Riwayat commit-nya belum sampai tiga. |
| `python3 hitung.py \| grep -qx 5` | Hasil hitung.py belum 5. |
| `python3 -m unittest -q` | Masih ada test yang gagal. |

When a lab Submission is handed in, the learner's own Git history is recorded too, and the defense questions may ask about it. That makes Git lessons gradable from their history, not only from their files.

## What happens in the admin

The instructor can upload a starter template zip, sees every attempt with the AI evaluation, the defense answers and a timeline of how the learner worked, and saves the grade from a form the AI has already filled in. Mention the template zip in your hand-over when the project needs starting code.
