# Publishing To PyPI

Checkpoint publishes the `checkpoint-cli` package to PyPI so users can install
the CLI without cloning the repository.

## Install Commands

After the first PyPI release is published:

```bash
pip install checkpoint-cli
checkpoint --help
```

With uv:

```bash
uv tool install checkpoint-cli
checkpoint --help
```

For project-local use:

```bash
uv add --dev checkpoint-cli
uv run checkpoint --help
```

## One-Time PyPI Setup

Use PyPI Trusted Publishing instead of storing an API token in GitHub.

Create a pending publisher on PyPI with:

- PyPI project name: `checkpoint-cli`
- Owner: `bkalyankumar`
- Repository name: `contextos`
- Workflow name: `publish-pypi.yml`
- Environment name: `pypi`

In GitHub, create an environment named `pypi`. Add a required reviewer before
public launch if you want an approval gate for uploads.

## Release Flow

The `.github/workflows/publish-pypi.yml` workflow publishes when a GitHub
release is published. It can also be run manually with an existing tag, for
example `v0.1.0`, which is useful when the GitHub release already exists before
the workflow is added.

PyPI versions are immutable. If a version has already been uploaded, fix forward
with a new version instead of trying to overwrite the existing artifact.
