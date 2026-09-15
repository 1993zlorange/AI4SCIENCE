# AI4SCIENCE Template v0.1.0 — Release Manifest

## Release identity

- Package: `ai4science-template-v0.1.0`
- Type: local research-project template release
- Version: `v0.1.0`
- License: MIT
- Release date: 2026-09-13
- External actions: none — no upload, deployment, repository push, submission, signing, or publication was performed.

## Included content

| Path | Purpose | Included |
| --- | --- | --- |
| `AGENTS.md` | Root research governance, evidence gates, and release rules | Yes |
| `README.md` | Template overview and derivation guidance | Yes |
| `LICENSE` | MIT license text | Yes |
| `projectname/project/` | Python AI/research engineering template, tests, configuration, documentation, and project skills | Yes |
| `MANIFEST.sha256` | SHA-256 integrity list for package files | Yes |
| `ROLLBACK.md` | Local rollback procedure | Yes |

## Exclusions

- `projectname/achieve/`: research records, management records, scientific cards, handoffs, and internal delivery material.
- `.venv/`, caches, `__pycache__`, `var/runs/`, logs, secrets, real data, models, checkpoints, experiment outputs, and environment-specific artifacts.
- Empty `CITATION.cff`: a derived research project must complete its authors, title, version, DOI, and repository information before a research-output release.
- Research conclusions, datasets, models, papers, or statements that a scientific gate has passed.

## Verification

1. From `projectname/project`, run `python scripts/f001_governance_validate.py --project-root . --check`.
2. Run `python -m ruff format --check .`, `python -m ruff check .`, `python -m mypy src`, and `python -m pytest` in a prepared local environment.
3. Verify every package file against `MANIFEST.sha256` before reuse.

## Known limitations

This is a reusable scaffold, not a scientific result. It contains no approved research question, data, model, experiment, result, paper, DOI, author list, or public scientific claim.
