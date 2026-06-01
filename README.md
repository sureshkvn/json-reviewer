# json-reviewer

A lightweight CLI tool that validates JSON files for syntax errors, duplicate keys, and schema compliance. Built as a [Claude Code](https://claude.ai/code) skill.

## Features

- **Syntax validation** — detects malformed JSON with line and column pointers
- **Duplicate key detection** — catches silently overwritten keys that standard parsers ignore
- **Schema validation** — checks required fields and value types against a simple schema format (optional)

## Requirements

- Python 3.10+
- No external dependencies — uses only the standard library

## Usage

```bash
# Basic syntax + duplicate-key check
python scripts/check_json.py path/to/file.json

# With schema validation
python scripts/check_json.py path/to/file.json --schema path/to/schema.json
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All checks passed |
| `1`  | One or more issues found |
| `2`  | Usage error or file not found |

## Schema format

The `--schema` flag accepts a plain JSON file (not the JSON Schema spec). Supported types: `string`, `number`, `integer`, `boolean`, `array`, `object`, `null`. Nested objects are validated recursively.

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

## Limitations

- Schema format is intentionally simple — not the full JSON Schema (draft-07) spec.
- Array item validation is not supported (only checks that the field is an array type).
- For very large files (>50 MB), the check may be slow.
