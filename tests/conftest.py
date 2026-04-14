"""Module `tests/conftest.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

