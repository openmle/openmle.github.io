# Ecosystem

OMLE is a format plus the tooling to produce, inspect and execute it. Each piece
ships separately so you install only what you need.

| Package | Language | Purpose |
|---|---|---|
| [`omle`](https://github.com/openmle/omle) | Python | The reference implementation: in-memory IR, protobuf I/O, validation, and the `omle` CLI |
| [`omle-convert`](https://github.com/openmle/omle-convert) | Python | Converters from trained models to `.omle` |
| [`omle-runtime`](https://github.com/openmle/omle-runtime) | C++ (Python / Java bindings) | Inference runtime, with a stable C ABI for FFI |
| [`omle-spark`](https://github.com/openmle/omle-spark) | Scala + Python | Spark ML transformer — scores DataFrames from Scala or PySpark |
| [`omle-server`](https://github.com/openmle/omle-server) | C++ (Python package) | Open Inference Protocol (OIP) server over REST and gRPC |
| [`omle-viewer`](https://github.com/openmle/omle-viewer) | Python + TypeScript | Interactive DAG viewer for Jupyter and the browser |
| [`omle.js`](https://github.com/openmle/omle.js) | TypeScript | Browser / Node loader, validator, and execution engine |

## How they fit together

`omle` defines the format and the IR that everything else speaks.
`omle-convert` writes files; `omle-runtime`, `omle.js` and `omle-spark` read
them. `omle-server` wraps the runtime behind OIP. `omle-viewer` is built on
`omle.js`, which is why the [playground](playground/index.md) needs no server.

Two runtimes read the same file by design — a C++ engine for throughput and a
TypeScript engine for the browser. Both check the verification cases embedded in
a model on load, so a file that scores correctly in one is expected to score
identically in the other.

## Converters

Which frameworks convert, and what each one covers, is documented with the
converters themselves: see [Converters](converters/README.md) for the status
table and a page per framework.

## Contributing

The proto schema and registries are stabilising toward a v1 release. Each repo
carries its own `CONTRIBUTING.md` with development setup and the checks a change
has to pass. Contributions are especially welcome in converters, runtime
implementations, validation tooling, and the specification itself.
