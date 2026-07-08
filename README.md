## Bazel Registry

[![test](https://github.com/ezhuk/bazel-registry/actions/workflows/test.yml/badge.svg)](https://github.com/ezhuk/bazel-registry/actions/workflows/test.yml)

A custom [Bazel](https://bazel.build) module registry.

## Usage

Add the registry to your `.bazelrc`:

```
common --registry=https://ezhuk.github.io/bazel-registry/
common --registry=https://bcr.bazel.build/
```

The [Bazel Central Registry](https://registry.bazel.build) is listed second so other dependencies can still be resolved normally.

Or pass the registries as command-line arguments:

```bash
bazel build //... \
  --registry=https://ezhuk.github.io/bazel-registry/ \
  --registry=https://bcr.bazel.build/
```

## License

The modules are licensed under the [MIT License](https://github.com/ezhuk/bazel-registry?tab=MIT-1-ov-file).
