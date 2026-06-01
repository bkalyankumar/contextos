# Verification Notes

The starter scaffold has been smoke-tested in the creation environment and during the DX audit.

Commands run successfully with available local packages:

```bash
python -m pip install -e '.[dev]'
checkpoint --help
checkpoint status
checkpoint continue
pytest
```

Current `pytest` result:

```text
15 passed
```

Note: a normal `pip install -e '.[dev]'` may need internet access to resolve build dependencies in a fresh environment. In an offline environment with dependencies already installed, use:

```bash
python -m pip install --no-build-isolation -e '.[dev]'
```
