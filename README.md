## Bazel Registry

[![test](https://github.com/ezhuk/bazel-registry/actions/workflows/test.yml/badge.svg)](https://github.com/ezhuk/bazel-registry/actions/workflows/test.yml)

A custom registry that provides [Bazel](https://bazel.build) module metadata and overlay build files for selected dependencies that are missing from or slow to update in the [Bazel Central Registry](https://registry.bazel.build).

## Usage

Add the registry to your `.bazelrc`:

```
common --registry=https://ezhuk.github.io/bazel-registry/
common --registry=https://bcr.bazel.build/
```

Or pass the registries as command-line arguments:

```bash
bazel build //... \
  --registry=https://ezhuk.github.io/bazel-registry/ \
  --registry=https://bcr.bazel.build/
```

## License

The registry metadata, patches and overlay build files are licensed under the [MIT License](https://github.com/ezhuk/bazel-registry?tab=MIT-1-ov-file).
