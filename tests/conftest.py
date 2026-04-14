"""Detailed module documentation for `tests/conftest.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `conftest.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

