# Kiat Koding skills

Agent skills for building courses on [Kiat Koding](https://kiatkoding.com), an Indonesian course platform for programmers.

| Skill | What it does |
|---|---|
| [kiat-koding-creator](skills/kiat-koding-creator/SKILL.md) | Plans and writes Kiat Koding courses through the `kiat-koding-creator` MCP server: codelab, text and video lessons, graded Submissions on the learner's computer or in the Coding Lab, covers and screenshots, in Kiat Koding's Indonesian writing style. |

## Install

```bash
npx skills add kiatkoding/skills
```

The [skills CLI](https://github.com/vercel-labs/skills) installs the skill into the coding agents on your machine (Claude Code, Codex, Cursor, opencode and others). Add `-g -y` to install it for your user without prompts. Update it later with `npx skills update`.

The skill works together with the Kiat Koding MCP server, which gives your agent the tools to create and edit courses. Connect it from Kiat Koding at Koneksi > Agen AI > Hubungkan agen AI, and paste the prompt shown there into your agent.

## License

[MIT](LICENSE).

## Untuk instruktur

Skill ini membantu agent AI-mu menyusun kelas di Kiat Koding dengan gaya dan aturan yang sama dengan kelas lainnya. Pasang dengan `npx skills add kiatkoding/skills`, lalu hubungkan agent-mu ke Kiat Koding lewat menu Koneksi > Agen AI. Semua yang dibuat agent tersimpan sebagai draf, dan kamu yang memeriksa dan menerbitkannya.
