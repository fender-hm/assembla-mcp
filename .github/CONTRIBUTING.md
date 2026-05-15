# Contributing

## Add a tool in 5 steps

1. **Pick the module** — find the right file in `assembla_mcp/tools/` (or create a new one for a new resource).

2. **Write a failing test** in the corresponding `tests/tools/test_*.py` file. Mock `get_client()` using `unittest.mock.patch`. Run `pytest tests/tools/test_yourfile.py -v` and confirm it fails.

3. **Implement the function** following the pattern in existing tools:
   - Resolve the space ID with `_resolve_space(space_id)`
   - Call `get_client().get/post/put/delete()`
   - Check for `"error"` key in result and return it as a string
   - Return `json.dumps(result, indent=2)` on success

4. **Register the tool** — add it to the module's `register(mcp)` function.

5. **Run all tests** with `pytest -v` and confirm everything passes. Then open a PR.

## Running tests

```bash
pip install -e ".[dev]"
pytest -v
```