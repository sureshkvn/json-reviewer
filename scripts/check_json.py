#!/usr/bin/env python3
"""
check_json.py - JSON Syntax Reviewer
Checks a JSON file for:
  - Syntax errors (malformed JSON)
  - Duplicate keys
  - Schema validation (required fields and types) if a schema file is provided

Usage:
  python check_json.py <file.json> [--schema <schema.json>]
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


# ── Duplicate-key detection ────────────────────────────────────────────────────

def _object_pairs_hook(pairs: list[tuple]) -> dict:
    """
    Called by json.loads for every JSON object.
    Raises ValueError on the first duplicate key found.
    """
    counter = Counter(k for k, _ in pairs)
    duplicates = [k for k, count in counter.items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate keys found: {duplicates}")
    return dict(pairs)


# ── Schema validation ──────────────────────────────────────────────────────────

SUPPORTED_TYPES = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def _validate_schema(data: dict, schema: dict, path: str = "root") -> list[str]:
    """
    Recursively validate data against a simple schema.
    Schema format:
      {
        "required": ["field1", "field2"],
        "properties": {
          "field1": { "type": "string" },
          "field2": { "type": "number" },
          "nested": {
            "type": "object",
            "required": ["id"],
            "properties": { "id": { "type": "integer" } }
          }
        }
      }
    Returns a list of human-readable error strings.
    """
    errors = []

    if not isinstance(data, dict):
        errors.append(f"  [{path}] Expected an object, got {type(data).__name__}")
        return errors

    # Check required fields
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"  [{path}] Missing required field: '{field}'")

    # Check property types and recurse
    for field, rules in schema.get("properties", {}).items():
        if field not in data:
            continue  # Already caught above if required

        value = data[field]
        field_path = f"{path}.{field}"
        expected_type_name = rules.get("type")

        if expected_type_name:
            expected_type = SUPPORTED_TYPES.get(expected_type_name)
            if expected_type is None:
                errors.append(f"  [{field_path}] Unknown schema type: '{expected_type_name}'")
            elif not isinstance(value, expected_type):
                actual = type(value).__name__
                errors.append(
                    f"  [{field_path}] Expected type '{expected_type_name}', got '{actual}'"
                )

        # Recurse into nested objects
        if rules.get("type") == "object" and isinstance(value, dict):
            errors.extend(_validate_schema(value, rules, path=field_path))

    return errors


# ── Main review logic ──────────────────────────────────────────────────────────

def review(json_path: Path, schema_path: Path | None = None) -> int:
    """
    Run all checks. Returns 0 if clean, 1 if issues found, 2 on usage error.
    """
    issues: list[str] = []
    passed: list[str] = []
    data = None

    print(f"\n📄 Reviewing: {json_path}\n")

    # ── 1. Syntax check ────────────────────────────────────────────────────────
    try:
        raw = json_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"❌ File not found: {json_path}")
        return 2
    except OSError as e:
        print(f"❌ Could not read file: {e}")
        return 2

    try:
        # First pass: plain parse to get the data object
        data = json.loads(raw)
        passed.append("Syntax — valid JSON")
    except json.JSONDecodeError as e:
        issues.append(f"Syntax error — {e.msg} (line {e.lineno}, col {e.colno})")

    # ── 2. Duplicate key check (only if syntax passed) ─────────────────────────
    if data is not None:
        try:
            json.loads(raw, object_pairs_hook=_object_pairs_hook)
            passed.append("Duplicate keys — none found")
        except ValueError as e:
            issues.append(str(e))

    # ── 3. Schema validation ───────────────────────────────────────────────────
    if schema_path is not None:
        try:
            schema_raw = schema_path.read_text(encoding="utf-8")
            schema = json.loads(schema_raw)
        except FileNotFoundError:
            print(f"❌ Schema file not found: {schema_path}")
            return 2
        except json.JSONDecodeError as e:
            print(f"❌ Schema file is not valid JSON: {e}")
            return 2

        if data is not None:
            schema_errors = _validate_schema(data, schema)
            if schema_errors:
                issues.append("Schema validation failed:")
                issues.extend(schema_errors)
            else:
                passed.append("Schema validation — all fields present and correctly typed")
        else:
            issues.append("Schema validation — skipped (file has syntax errors)")

    # ── Report ─────────────────────────────────────────────────────────────────
    if passed:
        print("✅ Passed checks:")
        for p in passed:
            print(f"   • {p}")

    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   • {issue}")
        print(f"\n🔍 Result: {len(issues)} issue(s) detected — review required.\n")
        return 1

    print(f"\n🎉 Result: All checks passed — JSON looks good!\n")
    return 0


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Review a JSON file for syntax errors, duplicate keys, and schema compliance."
    )
    parser.add_argument("file", type=Path, help="Path to the JSON file to review")
    parser.add_argument(
        "--schema",
        type=Path,
        default=None,
        metavar="SCHEMA_FILE",
        help="Optional path to a JSON schema file for field/type validation",
    )
    args = parser.parse_args()

    sys.exit(review(args.file, schema_path=args.schema))


if __name__ == "__main__":
    main()
