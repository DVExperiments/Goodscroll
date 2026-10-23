# Goodscroll V1.6 — Research Trails & Intelligence

Mobile-first research discovery on GitHub Pages. This release builds on V1.5 and retains all four research sources.

## New in V1.6
- Distinctive title + source metadata classification; avoids recycling unrelated legacy categories.
- Clearly flagged `Unclassified` papers when classification is uncertain.
- Extractive author-abstract explanations, with revised result-method cues and explicit uncertainty.
- Research network SVG: click or keyboard-select paper nodes, solid lines for direct identifier references, dashed for overlapping terms.
- Balanced editorial ordering reduces long same-discipline streaks.
- Existing catalogue re-enriched and included for immediate nonempty start.

## Integrity and caveats
- Extracted snippets originate only in indexed abstracts. They are not full-paper review, generated interpretation or validation.
- Relationships: explicit citations only if relevant identifiers match; remaining lines reflect lexical similarity. No claim of support/contradiction.
- Source topic coverage and indexing vary. Low-confidence work is displayed as Unclassified rather than labelled incorrectly.
- Automated checks are offline; API integration needs confirmation after deployment.

## QA
`python -m py_compile collector/research.py`, `node --check app/app.js`, and ZIP integrity.
