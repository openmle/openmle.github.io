---
hide:
  - navigation
  - toc
---

# Playground

Drop a `.omle` or `.json` model file into the viewer below to explore it. The
model never leaves your machine: the viewer is a self-contained page and
[omle.js](https://github.com/openmle/omle.js) executes the model in the browser
— there is no server and nothing is uploaded.

What you can do with a model loaded:

- **Graph** — walk the DAG, double-click a composite to descend into it
- **Inspector** — read any node's parameters, tensors and schema bindings
- **Inference** — supply inputs and run, or step node by node and watch values change
- **Verification** — replay the sample cases embedded in the file and diff them
  against the expected outputs

[Open the viewer in its own tab :material-open-in-new:](viewer.html){ .md-button .md-button--primary target="_blank" rel="noopener" }

The viewer is a single self-contained page, so opening it directly gives the
whole window to the graph — worth it for anything but a trivial model. The
embedded copy below is the same file.

<!-- This page is docs/playground/index.md and the synced bundle is
     docs/playground/viewer.html, so "viewer.html" is the correct relative path
     from both the source file and the built URL. Keeping them in one directory
     is what lets `mkdocs --strict` validate the link above: as a sibling of
     playground.md it resolved differently in the source tree than in the built
     site, and only the browser would have noticed. -->
<iframe class="omle-frame" src="viewer.html" title="OMLE viewer" allowfullscreen loading="lazy"></iframe>

!!! tip "No model to hand?"

    Any file produced by `omle-convert` works. To make one:

    ```python
    from omle import export_omle
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import load_iris

    X, y = load_iris(return_X_y=True, as_frame=True)
    export_omle(RandomForestClassifier().fit(X, y), "iris.omle", X=X)
    ```

    Then drop `iris.omle` above.

The same viewer runs locally — `omle view model.omle` — and renders inline in a
Jupyter cell when `omle_viewer` is imported.
