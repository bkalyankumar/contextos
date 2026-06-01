# Verification Notes

The starter scaffold was smoke-tested in the creation environment.

Commands run successfully with available local packages:

```bash
python -m pip install --no-build-isolation -e '.[dev]'
checkpoint --help
checkpoint status
checkpoint resume --for codex --task TASK-001
pytest -q
```

`pytest -q` result:

```text
1 passed
```

Note: a normal `pip install -e '.[dev]'` may need internet access to resolve build dependencies in a fresh environment. In an offline environment with dependencies already installed, use:

```bash
python -m pip install --no-build-isolation -e '.[dev]'
```
