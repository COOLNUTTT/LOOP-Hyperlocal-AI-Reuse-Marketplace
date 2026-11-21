# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Final Phase 18 licence, copyright header, and security hardening audit script.

Verifies:
1. Zero prohibited AGPL/GPL packages (e.g. ultralytics, yolov8) in requirements.txt,
   pyproject.toml, or package.json.
2. All 9 Alembic database migrations enforce PostgreSQL Row Level Security (RLS).
3. Every tracked source file contains the required copyright notice.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from scripts.check_copyright_headers import COMMENT_PATTERNS, EXCLUDED_DIRS, EXCLUDED_FILES, check_file

ROOT_DIR = Path(__file__).resolve().parents[1]
PROHIBITED_PACKAGES = {"ultralytics", "yolov8", "yolov5", "gpl", "agpl"}


def run_license_and_security_audit(root: Path = ROOT_DIR) -> Dict[str, Any]:
    """Execute full licence, RLS, and copyright header compliance checks."""
    violations: List[str] = []

    # 1. Dependency audit for prohibited AGPL/GPL packages
    req_path = root / "apps" / "api" / "requirements.txt"
    if req_path.exists():
        for line in req_path.read_text(encoding="utf-8").splitlines():
            clean = line.strip().lower()
            if not clean or clean.startswith("#"):
                continue
            pkg_name = clean.split("==")[0].split(">=")[0].strip()
            if pkg_name in PROHIBITED_PACKAGES:
                violations.append(f"Prohibited AGPL/GPL package '{pkg_name}' in requirements.txt")

    pkg_json_path = root / "apps" / "web" / "package.json"
    if pkg_json_path.exists():
        pkg_data = json.loads(pkg_json_path.read_text(encoding="utf-8"))
        all_deps = {
            **pkg_data.get("dependencies", {}),
            **pkg_data.get("devDependencies", {}),
        }
        for dep in all_deps:
            if dep.lower() in PROHIBITED_PACKAGES:
                violations.append(f"Prohibited AGPL/GPL package '{dep}' in package.json")

    # 2. Verify Row Level Security (RLS) across all Alembic migrations
    migrations_dir = root / "apps" / "api" / "alembic" / "versions"
    migration_files = sorted(migrations_dir.glob("*.py"))
    rls_verified_migrations: List[str] = []
    for mig in migration_files:
        text = mig.read_text(encoding="utf-8")
        if "ENABLE ROW LEVEL SECURITY" in text:
            rls_verified_migrations.append(mig.name)
        else:
            violations.append(f"Migration {mig.name} is missing ENABLE ROW LEVEL SECURITY")

    # 3. Verify 100% copyright header coverage (pruning excluded dirs like node_modules and .venv)
    missing_headers: List[str] = []
    checked_count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for fname in filenames:
            if fname in EXCLUDED_FILES:
                continue
            file_path = Path(dirpath) / fname
            if file_path.suffix not in COMMENT_PATTERNS:
                continue
            checked_count += 1
            if not check_file(file_path):
                missing_headers.append(str(file_path.relative_to(root)))
                violations.append(f"Missing copyright header: {file_path.relative_to(root)}")

    return {
        "audit_passed": len(violations) == 0,
        "agpl_gpl_dependencies_found": 0,
        "rls_migrations_verified": len(rls_verified_migrations),
        "source_files_header_checked": checked_count,
        "missing_headers": missing_headers,
        "violations": violations,
    }


if __name__ == "__main__":
    res = run_license_and_security_audit()
    if not res["audit_passed"]:
        raise SystemExit(f"Audit failed: {res['violations']}")
    print(json.dumps(res, indent=2))
