---
name: kiat-koding-creator
description: Build and edit courses on Kiat Koding (kiatkoding.com) through its kiat-koding-creator MCP server. Covers planning a course, writing codelab and video lessons, designing graded Submissions on the learner's computer or in the Coding Lab, covers and screenshots, and Kiat Koding's Indonesian writing style. Use when asked to create, outline, write, extend, fix or review a Kiat Koding course or lesson.
---

# Kiat Koding course creator

Kiat Koding is an Indonesian course platform for programmers. Instructors build their courses there, and you build them through the `kiat-koding-creator` MCP server. The instructor reviews the draft and publishes it in the Kiat Koding admin. This skill is how to build a course that is worth publishing.

## Before you start

- The MCP tools (`list_courses`, `get_course`, `create_course`, `add_section`, `add_lesson`, `update_lesson` and the rest) must be available. If they are not, tell the user to connect you from Kiat Koding at Koneksi > Agen AI > Hubungkan agen AI, then stop.
- Everything you write is a draft. You cannot publish, schedule live sessions, choose the payment method or upload a starter template zip. Those happen in the admin. Say so when the user asks for them.
- A change aimed at a live course goes into its draft version, made on the first change. The tool answer's `draft_version` names that draft's `course_id`. From then on use the draft's id and its own chapter and lesson ids from `get_course`.
- Talk to the user in Indonesian with "kamu", unless they write to you in another language.

## Workflow

1. Ask, in one message, only for what you cannot infer: the topic and the result learners should reach, who the learners are and what they already know, the level, and whether a graded project (Submission) belongs in the course. Skip the questions the user already answered.
2. Look before you write. Call `list_categories`, and `get_course` on one of the instructor's existing courses to match their tone and structure.
3. Propose the outline: the chapters, and for each lesson its kind and one line on what it covers. Wait for the user's go-ahead once. After that, build the whole draft without stopping for review at each lesson, since the instructor reviews it in the admin.
4. Build in order: `create_course` with the course info, `add_section` per chapter, then `add_lesson` per lesson.
5. Once the title and summary are settled, call `generate_course_covers` with the course's `course_id`. The instructor picks one of the options in the admin.
6. Hand over: give the `admin_url`, list what is left for the instructor (cover, price if they did not give one, payment method, live sessions, template zip, publishing), and name anything you skipped or were unsure about.

## Course info

- `title`: the skill or result the learner gets, in plain words. No hype.
- `summary`: one or two sentences on what the learner builds or can do afterwards. It shows in search results and link previews.
- `description` ("Tentang kelas"): Markdown. Who it is for, what they build, how the course is taught, what they need.
- `benefits` ("Yang kamu pelajari"): 4 to 8 concrete outcomes, each starting with a verb. They also print on the certificate's second page, so keep each one under about 120 characters.
- `requirements` ("Siapkan dulu"), `audience` ("Cocok buat"), `materials` ("Isi paket"): short lists.
- `level`: beginner, intermediate, expert or all_levels. It also sets the default Submission weights.
- `price_idr`: only when the user gave a price. Never guess one.

## Choosing a lesson kind

- `codelab`: anything the learner does or reads, such as building, configuring, practising, or concepts, background and comparisons. There is no text lesson kind: a reading lesson is a codelab with one step per section, and a short one may be a single step. See [references/codelab.md](references/codelab.md).
- `video`: when the instructor has a recording. Link it as a YouTube link or ID, an MP4 or WebM link, or an HLS `.m3u8` link. Never invent a video link.
- `submission`: a graded project, usually at the end of a chapter or of the course. See [references/submission.md](references/submission.md).
- Live sessions are added by the instructor in the admin.

Lessons open in order, and a Submission must pass before the lessons after it open. Place Submissions where that makes sense. With the instructor's agreement, mark the first lesson or two `is_preview` so visitors can try them before buying.

## Content principles

- Concepts before hands-on. Explain every technical term in plain words where it first appears.
- Many Kiat Koding courses teach building with a coding agent. In those, give the learner prompts, not code to type: put prompts in ```prompt fences and the result they should see in ```output fences. Explain why the important lines of a prompt are written the way they are, and review what the agent produced.
- Narrate, do not template. Do not repeat the same sub-headings ("Tujuan", "Langkah", "Penjelasan") in every step. Write prose that moves from goal to action to result to explanation.
- Show real things: screenshots from a real run, real output, real numbers. Never fabricate output, screenshots, versions or measurements. If you have not run something, say what to expect in general terms and mark it for the instructor to verify.
- Use ```mermaid diagrams for flows and architecture, and `generate_lesson_image` for concept illustrations in the Kiat Koding look.
- There are no quizzes on the platform. Use a codelab exercise or a Submission instead.
- Files learners need (starter code as a .zip, datasets, request collections, slides) go up with `create_file_upload`, up to 50 MB each. Put the returned link on its own line in the step that uses the file, where it shows as a download card. Without a shell, list the files for the instructor to add in the editor with Unggah file.

## Writing

Lesson content is in Indonesian. Follow [references/writing.md](references/writing.md). In short: address the learner as "kamu", no semicolons, no em dashes, no hype or slogans, "Submission" and never "tugas", "project" and never "proyek", and technical terms stay in English with Indonesian affixes ("di-commit", "nge-parse", "me-return").

## Markdown in lessons

Lesson bodies, codelab steps and Submission briefs are Markdown with GitHub tables. No raw HTML.

- Code fences get a language label and a copy button.
- ```prompt is a prompt to paste into an AI assistant. ```output is the result the learner should see.
- A ```video fence holding one YouTube, MP4, WebM or `.m3u8` link becomes the course player.
- ```mermaid draws a diagram. Use `flowchart TD` and short labels so it fits a phone.
- `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]` and `> [!CAUTION]` become labelled callouts.
- An image line followed by a line all in italics becomes a captioned figure. Write the caption as a plain sentence about what the image shows, never in a "Label: text" pattern.

## Images

- `generate_lesson_image` draws one illustration in the Kiat Koding look and returns its Markdown. Generated images, covers included, are capped at 20 per person per day.
- `create_image_upload` gives a curl command with a one-hour token to upload a screenshot from this machine (JPG, PNG or WebP up to 10 MB). It returns the Markdown to put in the lesson.
- Crop screenshots to what matters. Never show secrets such as tokens, keys or passwords, or other people's private data.

## Before handing over

- Every lesson has content, and every codelab step has an honest minute estimate.
- Every term is explained where it first appears, and nothing claims a result you did not see.
- Prompts are in ```prompt fences and expected results in ```output fences.
- Submissions have a brief and milestones written as described in the Submission reference.
- The writing follows the style reference.
- You gave the `admin_url` and the list of what is left for the instructor.
