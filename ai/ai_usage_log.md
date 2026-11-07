# AI Usage Log — communications_revolution_posters

This log records all substantive AI-assisted sessions for the project
"The Communications Revolution, 1775–2020: HamSCI posters from the AC2ZU tri-fold exhibit".

Required per University of Scranton AI Policy, HamSCI Generative AI Use Agreement, NASA AI guidance, and NSF AI guidance.

---

<!-- Append new entries below this line, newest at the bottom. Use the format produced by the /commit command. -->

## [2026-11-05 17:16 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5
- **Session Purpose**: Start the project from `ai_project_template` and transcribe Charlie Cebula (AC2ZU)'s three tri-fold boards, *The Communications Revolution, 1775–2020*, from N. A. Frissell's photos, so they can be rebuilt as HamSCI-style posters.
- **Sections/Files Affected**: `CLAUDE.md`, `README.md`, `.claude/rules/ai-governance.md`, `.claude/template.json`, `ai/ai_usage_log.md` (placeholders filled in, project content rules added, `python-code.md` removed); `source_photos/IMG_5578.heic`, `IMG_5579.heic`, `IMG_5580.heic` (original photos, unchanged); `transcription/board_1_1775-1848.md`, `board_2_1850-1940.md`, `board_3_1940-2020.md` (new)
- **Nature of Contribution**: Transcription (AI reading of cropped, zoomed photos, word for word, errors kept); suggested corrections listed in each file's transcriber notes (AI-generated, not yet checked against sources); project setup
- **Human Review Status**: Pending review (transcriptions need proofreading against the photos; suggested corrections need fact-checking)
- **Git Hash**: af38ab6 (branch instantiate-and-transcribe, PR w2naf-academia/communications_revolution_posters#1)

## [2026-11-07 15:15 UTC]
- **Tool**: Claude (Anthropic), claude-opus-5-5
- **Session Purpose**: Typeset the three Communications Revolution posters on the HamSCI 48 × 36 in poster template, using the verbatim transcription text with no corrections. At N. A. Frissell's direction, all footer logos except HamSCI were removed.
- **Sections/Files Affected**:
  - `posters/build_posters.py`: new; generates the posters from `transcription/`.
  - `posters/check_text.py`: new; checks that every transcribed line is on its poster.
  - `posters/requirements.txt`, `posters/README.md`: new.
  - `posters/poster_{1_1775-1848,2_1850-1940,3_1940-2020}.pptx`, with `.pdf` and `preview_*.png` versions: generated.
  - `README.md`, `CLAUDE.md`: layout description, status list, and a rule that posters are generated, never hand-edited.
- **Nature of Contribution**: Code generation (layout and text-fitting script, text check); layout design
- **Human Review Status**: Pending review. The posters were checked only in LibreOffice renders, not yet in PowerPoint. The text is the unproofread verbatim transcription.
- **Git Hash**: [fill in after committing]
