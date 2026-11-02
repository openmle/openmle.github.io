# omle-convert Support References

One page per source framework, each answering the same question at class level:
what converts, what it becomes in the OMLE graph, and what is explicitly not
supported. The repository README's
[Supported frameworks](https://github.com/openmle/omle-convert/blob/main/README.md#supported-frameworks) table carries the
counts and the entry points; these pages carry the detail behind them.

"Not supported" sections are deliberate. A converter that silently dropped an
unsupported stage would produce a model that loads and scores differently from
the original, so each page states the boundary rather than leaving it to be
discovered.

## Model frameworks

- [`sklearn.md`](sklearn.md) — the largest surface, and the one the others reach
  through: estimators, meta-estimators, preprocessing and feature selection
  inside `Pipeline` and `ColumnTransformer`, per-column DataFrame inputs, graph
  shape, and output type annotations.
- [`xgboost.md`](xgboost.md) — sklearn wrappers, `xgb.Booster` and `.json`,
  feature dtypes, use inside a `ColumnTransformer`, and the auxiliary data
  (verification, warmup, sample inputs) written into converted models.
- [`lightgbm.md`](lightgbm.md) — the same ground for sklearn wrappers,
  `lgb.Booster` and `.txt`.
- [`catboost.md`](catboost.md) — supported inputs and how oblivious trees are
  represented.
- [`spark.md`](spark.md) — conversion modes, supported stages, and the subset of
  SQL that `SQLTransformer` compiles to `Derive` nodes.

## Encoders

- [`category_encoders.md`](category_encoders.md) — the target-statistic and
  lookup encoders, why most collapse to a single operator with an explicit value
  table, the emitted node attributes, and the name collision with sklearn's own
  `TargetEncoder`.

## Status and roadmap

Everything listed above is implemented and covered by the test suite. The one
entry that is not yet is recorded here so the gap is visible rather than
inferred from its absence:

| Framework | Status | Notes |
|---|---|---|
| scikit-learn | Available | Pipeline walker, including meta-estimators and `category_encoders` |
| Spark ML | Available | Live (PySpark) and no-Spark (saved-format reader) paths; XGBoost4J and SynapseML LightGBM |
| XGBoost | Available | sklearn wrappers, native `Booster`, `.json` |
| LightGBM | Available | sklearn wrappers, native `Booster`, `.txt` |
| CatBoost | Available | sklearn wrappers, `.cbm` / `.json` |
| PMML | Planned | Round-trip fidelity for the compliance audience |

Per-framework counts and entry points are in the repository README's
[Supported frameworks](https://github.com/openmle/omle-convert/blob/main/README.md#supported-frameworks) table; the pages above
carry the class-level detail.

## Elsewhere

- Operator and function semantics — the [OMLE registry
  reference](https://github.com/openmle/omle/blob/main/docs/reference/README.md),
  which defines what the nodes these converters emit actually mean.
- Contributing a converter — [`CONTRIBUTING.md`](https://github.com/openmle/omle-convert/blob/main/CONTRIBUTING.md).
