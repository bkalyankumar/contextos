# Launch Plan

This is the operational launch plan for ContextOS / Checkpoint.

## Launch Homes

- Open-source home: `https://github.com/bkalyankumar/contextos`
- Initial marketing and docs home: `https://contextos.quantumleapit.in`
- Publisher: QuantumLeapIT

The product does not need a standalone product domain for the first public
launch. Use `contextos.quantumleapit.in` as the canonical marketing/docs site
and keep GitHub as the canonical source, issue, and release home.

## Public Positioning

Use this concise description everywhere a short product description is needed:

```text
ContextOS is repo-native continuity infrastructure for AI-assisted software engineering.
Checkpoint is the local-first CLI that lets developers resume work across AI coding tools.
```

Use this tagline for announcements and the marketing-site hero:

```text
Plan in Claude. Code in Codex. Debug in Claude Code. Delegate to Antigravity. Resume anywhere.
```

## Repository Launch Steps

1. Verify the launch branch is `main`.
2. Verify the local checks pass:

   ```bash
   mypy src
   ruff check .
   pytest
   vulture src tests
   uv build
   ```

3. Confirm the secret scan has no real findings. Test fixtures that contain fake
   redaction examples are acceptable.
4. Set GitHub repository metadata:

   ```bash
   gh repo edit bkalyankumar/contextos \
     --description "Repo-native continuity infrastructure for AI-assisted software engineering" \
     --homepage "https://contextos.quantumleapit.in"
   ```

5. Create a `v0.1.0` GitHub release from the verified build artifacts:

   ```bash
   gh release create v0.1.0 dist/checkpoint_cli-0.1.0-py3-none-any.whl dist/checkpoint_cli-0.1.0.tar.gz \
     --repo bkalyankumar/contextos \
     --title "Checkpoint 0.1.0" \
     --notes-file docs/release-notes/v0.1.0.md
   ```

6. Make the repository public:

   ```bash
   gh repo edit bkalyankumar/contextos --visibility public
   ```

7. Announce the project with the source install path clearly marked as the
   supported early-tester path.

## Package Policy

Do not block the first launch on PyPI. Source install is the supported
early-tester path for `0.1.0`.

Publish a package later when the project has enough external feedback to lock
down the distribution name and package support expectations.

## Marketing Site

The first marketing site should be small:

- one homepage
- install-from-source commands
- the agent-switching promise
- privacy and local-first trust notes
- links to GitHub, roadmap, security policy, and contribution guide

Avoid hosted sync, dashboard, IDE extension, vector database, and enterprise
claims until those features exist.

The first static site lives in `site/` and can be hosted without a build step.
GitHub Pages deployment is wired through `.github/workflows/pages.yml`, which
uploads `site/` as the Pages artifact.

GitHub Pages is configured for `contextos.quantumleapit.in`. Add this DNS record
at the domain provider:

```text
Type: CNAME
Name: contextos
Value: bkalyankumar.github.io
```

After DNS resolves, re-enable HTTPS enforcement in GitHub Pages settings if it
is not already enabled.
