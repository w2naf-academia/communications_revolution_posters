# AI Usage Log — {{PROJECT_NAME}}

This log records all substantive AI-assisted sessions for the project
"{{PROJECT_TITLE}}".

Required per University of Scranton AI Policy, HamSCI Generative AI Use Agreement, NASA AI guidance, NSF AI guidance, and {{FUNDER}} expectations.

---

<!-- Append new entries below this line, newest at the bottom. Use the format produced by the /commit command. -->

## [2026-04-25 13:26 EDT]
- **Tool**: Claude (Anthropic), claude-opus-4-7
- **Session Purpose**: Fix invalid `$schema` URL in `.claude/settings.json` so Claude Code stops rejecting the file (caught while using a downstream project scaffolded from this template).
- **Sections/Files Affected**: `.claude/settings.json`
- **Nature of Contribution**: Bug fix
- **Human Review Status**: Reviewed and verified
- **Git Hash**: 839ee05

## [2026-04-25 13:31 EDT]
- **Tool**: Claude (Anthropic), claude-opus-4-7
- **Session Purpose**: Align template with the `.claude/` folder anatomy described in https://blog.dailydoseofds.com/p/anatomy-of-the-claude-folder — gitignore the personal-override file and scope language-specific rules to relevant file types so they don't load when not applicable.
- **Sections/Files Affected**: `.gitignore` (added `CLAUDE.local.md`), `.claude/rules/latex-writing.md` (added `paths:` frontmatter scoping to `.tex`/`.bib`/`.cls`/`.sty`), `.claude/rules/python-code.md` (added `paths:` frontmatter scoping to `.py`/`pyproject.toml`/`requirements*.txt`)
- **Nature of Contribution**: Configuration / scaffolding refinement
- **Human Review Status**: Reviewed and verified
- **Git Hash**: e229ba5

## [2026-10-01 16:26 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5
- **Session Purpose**: Update the template so that every commit goes on a feature branch and
  through a pull request that a human reviews and merges, replacing the earlier
  "commit to main, ask before pushing" workflow.
- **Sections/Files Affected**: `.claude/commands/commit.md` (steps 6 to 9 rewritten for branch, PR, pointer bump, push order; see the follow-up entry below), `CLAUDE.md` (new Git Workflow section; Submodules steps), `.claude/rules/python-code.md`, `.claude/rules/ai-governance.md`, `README.md`
- **Nature of Contribution**: Edit
- **Human Review Status**: Pending review
- **Git Hash**: c525fe3 (branch pr-workflow, PR w2naf-academia/ai_project_template#1), merged as 28aaa71

## [2026-10-01 16:50 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5
- **Session Purpose**: Follow-up on the same PR, at N. A. Frissell's direction: keep this
  template self-contained. The first commit had replaced `/commit` with a copy of a private
  workflow file that cited rule IDs and a repository readers of this template cannot see; this
  commit replaces it with a self-contained branch/PR workflow and removes those references.
- **Sections/Files Affected**: `.claude/commands/commit.md`, `README.md`, `ai/ai_usage_log.md`
  (Sections field of the 16:26 entry corrected to describe the final change)
- **Nature of Contribution**: Edit
- **Human Review Status**: Pending review
- **Git Hash**: d9af543 (branch pr-workflow, PR w2naf-academia/ai_project_template#1), merged as 28aaa71

## [2026-10-01 17:46 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5
- **Session Purpose**: Stop the AI usage log from forcing a second pull request per change. The
  Git Hash field is now filled in once, on the change's own branch; a merge commit keeps that
  SHA valid, so no post-merge "merged SHA" update is needed.
- **Sections/Files Affected**: `.claude/commands/commit.md` (Git Hash and submodule pointer-bump steps)
- **Nature of Contribution**: Edit
- **Human Review Status**: Pending review
- **Git Hash**: 9043d6e (PR w2naf-academia/ai_project_template#3)

## [2026-10-10 12:08 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5 (1M context)
- **Session Purpose**: Make committing rendered output standing guidance, at NAF's direction
  (2026-10-10): memo and report PDFs and final figures capture the results of the code in
  human-readable form and must be committed, or past work is hard to look back on.
- **Sections/Files Affected**: `CLAUDE.md` (new "Rendered Output" section), `.claude/rules/latex-writing.md` (compiled PDF is not a build artifact), `.claude/rules/python-code.md`, `.claude/commands/commit.md` (step 2b), `.gitignore`.
- **Nature of Contribution**: Edit (workflow guidance).
- **Human Review Status**: Pending review.
- **Git Hash**: 7fbd6b1, branch `commit-rendered-output`

## [2026-10-10 12:35 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5 (1M context)
- **Session Purpose**: Narrow the committed-output rule to curated documents, at NAF's direction
  (2026-10-10): "I'm looking more to capture PDFs that are memos, notes, or some more curated
  level of analysis", not large generated outputs such as figure batches.
- **Sections/Files Affected**: `CLAUDE.md` ("Curated Documents"), `.claude/commands/commit.md` (step 2b), `.claude/rules/python-code.md`.
- **Nature of Contribution**: Edit (workflow guidance).
- **Human Review Status**: Pending review.
- **Git Hash**: afe77db, branch `curated-documents-only`

## [2026-10-10 15:01 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5 (1M context)
- **Session Purpose**: Make projects check their upstream ai_project_template for workflow and
  rule changes, at NAF's direction (2026-10-10), so repositories stop drifting from their
  template unnoticed.
- **Sections/Files Affected**: `.claude/template.json` (new: this template's record and the
  sibling templates it watches); `.claude/hooks/template_check.sh` (new: session-start check,
  read-only, once a day, silent on failure); `.claude/settings.json` (registers the hook);
  `.claude/commands/template-sync.md` (new: applies template changes as changes, through a PR);
  `CLAUDE.md` ("Template Updates"); `README.md` (instantiation step for the record).
- **Nature of Contribution**: Code generation, drafting.
- **Human Review Status**: Pending review.
- **Notes**: The check script was tested on scratch repositories (behind, current, freshly
  instantiated, unreachable upstream) and on this template. Hook format checked against the
  Claude Code hooks documentation. Project hooks run without a trust prompt; this one only reads
  `.claude/template.json` and makes one public HTTPS request to GitHub.
- **Git Hash**: 96a854a, branch `template-sync-tooling`

## [2026-10-10 15:14 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5 (1M context)
- **Session Purpose**: Fix a flaw in the template check found before rolling it out: comparing
  commit SHAs alone made templates flag each other indefinitely (marking a sibling reviewed is
  itself a commit the siblings see) and flagged projects for template changes with nothing to
  adopt.
- **Sections/Files Affected**: `.claude/hooks/template_check.sh` (asks GitHub's compare API which
  files changed and ignores `.claude/template.json`, `ai/ai_usage_log.md` and, in a project, its
  `not_adopted` files; falls back to flagging if the file list is unavailable; names the changed
  files in its notice); `.claude/commands/template-sync.md` (record and log are never taken from
  the template; companion changes only need marking reviewed); `.claude/template.json` (sibling
  template-sync tooling, the companion of this template's own, marked reviewed).
- **Nature of Contribution**: Code generation, edit.
- **Human Review Status**: Pending review.
- **Notes**: Tested on scratch repositories (behind: flagged with file list; only ignorable
  changes: silent) and on the live w2naf-academia template (flags both siblings' tooling PRs).
- **Git Hash**: 518a252, branch `template-check-filter`
