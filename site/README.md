# ContextOS Marketing Site

This directory contains the first static marketing/docs site for
`contextos.quantumleapit.in`.

It is intentionally dependency-free:

- `index.html` is the complete page.
- `CNAME` declares the intended custom domain for GitHub Pages artifacts.
- No build step is required.
- Any static host can serve this directory.

Preview locally:

```bash
python -m http.server 8080 --directory site
```

Then open `http://localhost:8080`.

Before public announcement, make sure the GitHub repository is public so the
GitHub, release, roadmap, contribution, and security links are visible to
visitors.
