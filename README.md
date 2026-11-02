# openmle.github.io

Source for <https://openmle.github.io> — the OMLE project site: landing page,
format specification, registry reference, and an in-browser playground.

## Content is synced, not copied

The spec and the registry reference live in
[`openmle/omle`](https://github.com/openmle/omle) and are *generated* from the
operator and function registries. The playground is the viewer bundle from
[`openmle/omle-viewer`](https://github.com/openmle/omle-viewer). None of it is
committed here — `scripts/sync_content.py` fetches it at build time, so the site
cannot drift from the repos it documents.

## Local development

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt

# Pull spec, reference and playground. Uses sibling checkouts when present
# (../omle, ../omle-viewer), otherwise clones and downloads from PyPI.
.venv/bin/python scripts/sync_content.py

.venv/bin/mkdocs serve
```

## Deployment

`.github/workflows/deploy.yml` runs the sync, builds, and publishes to GitHub
Pages. It runs on three triggers:

| trigger | fired by |
|---|---|
| `push` to `main` | a change to the site itself |
| `repository_dispatch` (`content-updated`) | `omle` when regenerated docs land, `omle-viewer` after a release |
| `workflow_dispatch` | the Run workflow button |

The dispatch trigger matters because the site's content is *fetched* rather
than committed: a new operator in `omle` or a new `omle-viewer` release changes
nothing here, so without something asking for a rebuild the site keeps serving
the previous version indefinitely.

### Setting up the dispatch token

Both source repos need a `SITE_DISPATCH_TOKEN` secret — a fine-grained PAT with
**`contents: write`** on `openmle/openmle.github.io`. A workflow's default
`GITHUB_TOKEN` is scoped to its own repository and cannot dispatch to another.

1. Create the PAT: GitHub → Settings → Developer settings → Fine-grained tokens,
   repository access `openmle/openmle.github.io`, permission
   *Contents: Read and write*.
2. Add it as an Actions secret named `SITE_DISPATCH_TOKEN` in **both**
   `openmle/omle` and `openmle/omle-viewer`.

Until it is set, both senders log a warning and skip rather than failing the
release that triggered them — a missing site rebuild should not turn a green
publish red.
