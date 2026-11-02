---
hide:
  - navigation
---

<div class="omle-hero" markdown>

# Open Machine Learning Exchange

An open, schema-aware interchange format for **classical** machine learning
inference. A compact protobuf representation of trained models together with
their preprocessing and postprocessing pipelines — portable across ecosystems,
inspectable, and verifiable.

<div class="omle-cta" markdown>
[Try the playground](playground/index.md){ .md-button .md-button--primary }
[Read the spec](spec/README.md){ .md-button }
[Browse the registry](reference/README.md){ .md-button }
</div>

</div>

---

## Why another format?

Classical ML has an interoperability gap. Deep learning settled on ONNX; the
tabular half of the field never settled on anything that captures what it
actually needs.

- **PMML** is semantically rich but XML-based, verbose, and has seen no
  meaningful update in years.
- **ONNX-ML** handles tensors well and classical ML semantics poorly. It has no
  notion of feature binding, missing/invalid/outlier handling, measure levels,
  or value domains.
- **Framework-native formats** — pickle, joblib, XGBoost JSON, LightGBM text —
  are not portable and carry real security risk.

OMLE combines PMML's semantic richness with ONNX's operational pragmatism, under
a permissive licence.

<div class="omle-compare" markdown>

| Capability | PMML | ONNX-ML | OMLE |
|---|---|---|---|
| Feature schema with measure levels | ✓ | ✗ | ✓ |
| Missing / invalid / outlier handling | ✓ | ✗ | ✓ |
| Structured ML models (trees, ensembles, linear, SVM, MLP, naive Bayes, clustering, anomaly detection) | ✓ | partial | ✓ |
| Generic ML models (KNN) | ✗ | ✗ | ✓ |
| Generic operator graph | ✗ | ✓ | ✓ |
| Embedded verification, warm-up and sample inputs | partial | ✗ | ✓ |
| Binary format | ✗ | ✓ | ✓ |
| Versioned operator registry | ✗ | ✓ | ✓ |
| Permissive licence | ✓ | ✓ | ✓ |

</div>

---

## Start here

=== "Convert a model"

    ```bash
    pip install "omle[convert]"
    ```

    ```python
    from omle import export_omle

    # scikit-learn, XGBoost, LightGBM, CatBoost — pass the fitted estimator.
    # X supplies the verification and sample rows embedded in the file.
    export_omle(sklearn_pipeline, "model.omle", X=X_test)
    ```

=== "Score a model"

    ```bash
    pip install "omle[runtime]"
    ```

    ```python
    import omle

    model = omle.load("model.omle")
    y_pred = model.predict(X_test)         # (n_samples,)
    proba  = model.predict_proba(X_test)   # (n_samples, n_classes)
    ```

=== "Inspect a model"

    ```bash
    pip install "omle[viewer]"
    omle view model.omle        # or omle-viewer model.omle
    ```

    Opens the interactive DAG viewer in your browser. No server, nothing
    uploaded — or use the [playground](playground/index.md) without installing
    anything.

=== "Run in the browser"

    ```bash
    npm install @openmle/omle
    ```

    ```js
    import { fromProtoBinary, Engine } from '@openmle/omle';

    const model  = fromProtoBinary(bytes);
    const output = new Engine(model).run({ x: [[1, 2, 3]] });
    ```

---

## What the format carries

OMLE uses a hybrid representation rather than forcing everything through one
abstraction.

**Logical schema** — named features and targets with types, measure levels,
value domains, and the policies that decide what happens to a missing, invalid
or outlying value. This is the layer ONNX-ML lacks, and the reason a converted
pipeline scores the same as the estimator it came from.

**Graph nodes** — a DAG of named operators spanning preprocessing, model
scoring, and postprocessing. [`CompositeNode`](spec/composite-scoping.md)
introduces local namespaces, so a `ColumnTransformer` round-trips without name
collisions.

**Structured model bodies** — dedicated proto messages for the classical
families, so a gradient-boosted ensemble stays a tree ensemble rather than
being lowered to matrix multiplies.

**Embedded verification** — a model file carries sample inputs and their
expected outputs, so a runtime can prove on load that it reproduces the
framework that produced the file. Every runtime in the ecosystem checks them.

---

## Reference

- **[Specification](spec/README.md)** — proto schema, registries, versioning,
  composite scoping, validation rules
- **[Registry reference](reference/README.md)** — every operator and expression
  primitive, generated from the registries: **79 operators** across four
  domains and **61 expression functions**
- **[Ecosystem](ecosystem.md)** — the packages, what each one is for, and how
  they fit together
