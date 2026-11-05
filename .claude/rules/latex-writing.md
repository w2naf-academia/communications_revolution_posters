---
paths:
  - "**/*.tex"
  - "**/*.bib"
  - "**/*.cls"
  - "**/*.sty"
---

# LaTeX Writing Rules
*Delete this file if your project does not include LaTeX writing.*

Applies to all LaTeX source files in the project (typically under a `manuscript/`, `paper/`, `report/`, or `overleaf/` directory).

## Document Format
- Identify the document type up front (paper, annual report, proposal, dissertation, etc.) and note any template or style guide it follows
- Set the main document filename and bibliography path explicitly in the project's `CLAUDE.md`
- Place figures in a `figs/` subdirectory beside the main `.tex` file (or wherever the chosen template requires)

## Content Rules
- **Never fabricate or hallucinate citations** — only cite references that have been verified against an authoritative source
- Describe actual accomplishments, not aspirational ones
- Credit students, collaborators, and volunteers accurately by name and role
- Acknowledge funders explicitly per the funder's expectations

## LaTeX Workflow
- Commit document changes in the appropriate submodule first (if applicable), then update the pointer in the main repo
- If using Overleaf, pull before editing to avoid conflicts
- Do not commit LaTeX build artifacts (`.aux`, `.log`, `.bbl`, `.bcf`, `.blg`, `.out`, `.toc`, `.fls`, `.fdb_latexmk`, etc.) — these are in `.gitignore`
- **The compiled PDF is not a build artifact.** Commit it with its source, rebuilt from that source in
  the same commit, so the repository always holds a readable copy of the current document
- Preserve existing LaTeX formatting patterns from the template where applicable
- Verify a clean rebuild (zero undefined references, zero overfull boxes) before committing significant prose or layout changes
