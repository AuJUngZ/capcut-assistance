from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / ".vendor"))

    try:
        import pytest  # noqa: PLC0415
    except Exception:
        from _pytest.config import main as pytest_main  # noqa: PLC0415
        return pytest_main(sys.argv[1:])

    if hasattr(pytest, "main"):
        return pytest.main(sys.argv[1:])
    if hasattr(pytest, "console_main"):
        return pytest.console_main()

    from _pytest.config import main as pytest_main  # noqa: PLC0415
    return pytest_main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
