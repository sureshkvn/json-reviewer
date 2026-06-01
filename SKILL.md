---
name: json-reviewer
description: >
  Review JSON files for syntax errors, duplicate keys, and schema validation.
  Use this skill whenever the user wants to validate, lint, audit, or check a
  JSON file — even if they phrase it as "is my JSON correct?", "check this
  config file", "validate my API payload", or "does this JSON look right?".
  Also trigger when the user pastes raw JSON and asks for feedback, or when
  they mention broken/invalid/malformed JSON. Always prefer this skill over
  ad-hoc JSON inspection.
---

# JSON Syntax Reviewer

Validates a JSON file and produces a human-readable report covering:

1. **Syntax errors** — detects malformed JSON with line/column pointers
2. **Duplicate keys** — catches silently overwritten keys
3. **Schema validation** — checks required fields and value types (optional)

---

## When to use

- User provides a `.json` file path and wants it checked
- User pastes raw JSON and asks if it's valid
- User mentions "broken", "invalid", or "malformed" JSON
- User wants to verify an API payload, config file, or data file

---

## Quickstart

```bash
# Basic syntax + duplicate-key check
python scripts/check_json.py path/to/file.json

# With schema validation
python scripts/check_json.py path/to/file.json --schema path/to/schema.json
```

Exit codes: `0` = clean, `1` = issues found, `2` = usage/file error.

---

## Schema file format

The `--schema` flag accepts a plain JSON file (not JSON Schema spec).

```json
{
  "required": ["id", "name", "price"],
  "properties": {
    "id":    { "type": "integer" },
    "name":  { "type": "string"  },
    "price": { "type": "number"  },
    "meta": {
      "type": "object",
      "required": ["created_at"],
      "properties": {
        "created_at": { "type": "string" }
      }
    }
  }
}
```

Supported types: `string`, `number`, `integer`, `boolean`, `array`, `object`, `null`.

Nested objects are validated recursively.

---

## Sample output

**Clean file:**
```
📄 Reviewing: data.json

✅ Passed checks:
   • Syntax — valid JSON
   • Duplicate keys — none found
   • Schema validation — all fields present and correctly typed

🎉 Result: All checks passed — JSON looks good!
```

**File with issues:**
```
📄 Reviewing: broken.json

✅ Passed checks:
   • Syntax — valid JSON

❌ Issues found:
   • Duplicate keys found: ['id']
   • Schema validation failed:
   • [root] Missing required field: 'price'
   • [root.meta] Expected type 'string', got 'int'

🔍 Result: 3 issue(s) detected — review required.
```

---

## Workflow for Claude

1. If the user provides a file path, run the script directly.
2. If the user pastes raw JSON in chat, save it to a temp file first:
   ```bash
   cat > /tmp/review_target.json << 'EOF'
   { ...pasted JSON... }
   EOF
   python scripts/check_json.py /tmp/review_target.json
   ```
3. Show the full script output to the user.
4. If issues are found, explain each one clearly and suggest fixes.
5. If a schema is mentioned or implied, prompt the user for it and re-run with `--schema`.

---

## Limitations

- Schema format is intentionally simple — not full JSON Schema (draft-07) spec.
- Array item validation is not supported (only checks that the field is an array).
- For very large files (>50 MB), inform the user the check may be slow.
