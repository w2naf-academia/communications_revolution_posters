# AI Project Template

A starter scaffold for AI-assisted writing or coding projects in Dr. Nathaniel A. Frissell's (W2NAF) academic and HamSCI portfolio. The template enforces compliance with University of Scranton, HamSCI, NASA, and NSF policies on generative AI use, and provides a `/commit` workflow that logs every substantive AI session before committing.

The same scaffold supports:
- **Writing projects** (papers, proposals, annual reports, theses) — typically with an `overleaf/` submodule
- **Coding projects** (research software, dashboards, analysis pipelines) — flat or with one or more code submodules
- **Mixed projects** — both, in any combination

## Use as a GitHub Template

```bash
gh repo create my-new-project --template w2naf-academia/ai_project_template --private --clone
```

or click **Use this template** on the GitHub repository page.

## After Instantiation

1. **Replace placeholders.** Search the repo for `{{` and replace every `{{PLACEHOLDER}}` in `CLAUDE.md`, `.claude/rules/ai-governance.md`, and `ai/ai_usage_log.md`. Common placeholders:
   - `{{PROJECT_NAME}}`, `{{PROJECT_TITLE}}`, `{{PROJECT_GOAL}}`, `{{PROJECT_PERIOD}}`
   - `{{PI_NAME_AND_AFFILIATION}}`, `{{COLLABORATORS}}`, `{{FUNDER}}`, `{{FUNDING_AMOUNT_OPTIONAL}}`
   - `{{REPO_NAME}}`
2. **Prune optional rule files.** Delete the rule files that don't apply:
   - `rm .claude/rules/latex-writing.md` if no LaTeX
   - `rm .claude/rules/python-code.md` if no Python code
3. **Add project-specific top-level folders** (e.g., `manuscript/`, `src/`, `posters/`, `proposal/`, `media/`).
4. **Add submodules if needed.**
   - Overleaf manuscript: `git submodule add https://git.overleaf.com/<id> overleaf`
   - External code repo: `git submodule add git@github.com:org/repo.git <path>`
5. **Customize `.claude/rules/ai-governance.md`** — fill in the `{{FUNDER}}`-specific expectations section, or delete it if the project is unfunded.
6. **Commit and push** the instantiated project to its own GitHub repo. This initial push seeds `main`; every change after it goes through a feature branch and pull request (see `CLAUDE.md` § Git Workflow).

### Record which template commit you started from

`.claude/template.json` arrives describing this template. Turn it into a project record: set
`"role": "project"`, `"upstream": "w2naf-academia/ai_project_template"`, `"upstream_branch": "main"`, `"synced_commit"` to the
template commit you instantiated from (the tip of `main` that day), and `"synced_on"`; list in
`"customized"` the files whose placeholders you filled in, and in `"not_adopted"` any template
files you deleted; remove `repo` and `siblings`. From then on, a session-start check reports when
this template changes and `/template-sync` adopts the changes. If you skip this step, the first
Claude session notices and offers to do it.

## What This Template Provides

- **`CLAUDE.md`** — top-level project instructions consumed automatically by Claude Code, with placeholders for project specifics.
- **`.claude/rules/ai-governance.md`** — standing AI-use policies (Scranton, HamSCI, NASA, NSF) plus a funder-specific section.
- **`.claude/commands/commit.md`** — the `/commit` slash command that logs the AI session, then commits each changed repo (submodules first) on a feature branch and opens a pull request for human review and merge. Auto-detects submodules.
- **`ai/ai_usage_log.md`** — append-only log of every substantive AI-assisted session.
- **`.gitignore`** — generic LaTeX + Python build artifacts.
- **Optional rule files** for LaTeX writing and Python code, with "delete if unused" headers.
