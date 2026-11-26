# Writing a codelab

A codelab (`kind: codelab`, with `steps`) is a hands-on tutorial in numbered steps, in the style of Google Codelabs. The learner sees one step at a time with the list of steps beside it, and marks the lesson done on the last step. Use it for anything the learner does, and for reading lessons too (there is no text lesson kind): there each step is one section of the explanation, titled by what it explains. A codelab with a single step shows as a plain page, with no step list.

## Steps

- One step is one task the learner finishes before moving on. If a step needs two different results, split it.
- The title is short and imperative: "Siapkan project", "Minta agent membuat endpoint login", "Uji dengan data kosong".
- `minutes` is an honest estimate of the time a learner at the course's level needs, including waiting for an agent or a build. Do not round everything to 5.
- A codelab holds at most 60 steps. Most fit in 5 to 15.
- The first step says what the learner will have at the end and what they need ready. The last step sums up what they built and what comes next in the course.

## Inside a step

Write it as prose that moves through these beats, without turning them into sub-headings:

1. Why this step exists and what it should achieve.
2. What to do: the prompt in a ```prompt fence, or the command in a fenced code block with its language.
3. What should happen: the result in an ```output fence, and a screenshot when the result is visual.
4. What that result means: walk through the output, explain the terms in it, and point at what to check.
5. What to do when the result differs: the common failures and how to recover.

Give a step enough substance that a learner never has to guess. A step that is only a prompt and a screenshot is too thin.

## Prompts for a coding agent

- A prompt states the goal, the constraints and the decisions the learner made. It does not dictate code line by line, since the learner is learning to direct an agent.
- After the agent's result, review what it produced: what is good, what to watch, what the learner should check or ask it to change.
- When a prompt line carries a decision ("use SQLite, not a JSON file"), explain the decision.
- Keep technical names in English (file names, identifiers, commands, error messages). The explanation around them is Indonesian.

## Commands and code

- Put commands the learner types in a ```bash fence, one command per line, without a `$` prompt so the copy button gives a working command.
- Show only the code the step is about. Link or download the rest.
- Never present output you did not see. If the exact output depends on the learner's machine, show a representative output and say which parts differ.

## Visuals

- A screenshot after each visible result helps more than a paragraph describing it.
- A ```mermaid flowchart for any flow with three or more parts (request to response, build pipeline, agent loop).
- One illustration (`generate_lesson_image`) per concept that is hard to picture, not one per step.
