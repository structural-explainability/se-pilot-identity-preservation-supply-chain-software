# SE Pilot: Identity Preservation in Software Supply Chains

[![Docs Site](https://img.shields.io/badge/docs-site-blue?logo=github)](https://structural-explainability.github.io/se-pilot-identity-preservation-supply-chain-software/)
[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software)
[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

[![CI](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/actions/workflows/ci-python-zensical.yml)
[![Docs Deploy](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/actions/workflows/deploy-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/actions/workflows/deploy-zensical.yml)

> A feasibility pilot for source-grounded identity-preservation conformance
> across software supply-chain representations.

## Purpose

This repository tests whether security-relevant identity commitments can be
encoded as data and evaluated systematically across software supply-chain
transformations.

The initial pilot tests `representation_preservation` for Package URL (PURL)
across SPDX and CycloneDX representations, with explicit outcomes for cases
that are unsupported, underdetermined, unanchorable, or not applicable.

The research question is:

> Can a source-grounded preservation rule, fixed before generalization
> execution, detect when an identity-bearing identifier is preserved, dropped,
> altered, or relocated during a representation transformation?

See the [Study Overview](./docs/en/index.md) for the research design,
the [Run Protocol](./docs/en/run.md) for freeze and execution procedures,
and the [Test Guide](./docs/en/test.md) for engineering validation.

## Role in Structural Explainability

This pilot is motivated by the SE-210 Operational Identity framework:

- [Paper: SE-210 Operational Identity](https://arxiv.org/abs/2607.20729)
- [Repo: Executable verification of the finite mathematical core of SE-210](https://github.com/structural-explainability/se-verification-operational-identity)

The pilot does not assume that every software supply-chain semantic rule
is an SE-210 identity relation.

The initial preservation-conformance test precedes any claim that SE-210's
partition machinery provides additional structural value.

## Repository Structure

```text
contracts/
    schema.md
    commitments.toml
    sources.toml
    FREEZE_01_COMMITMENT_EVALUATOR.md

src/
    preservation_test/

tests/

known/
    known_violations.toml

docs/
    en/
        index.md
        run.md
        test.md
```

## Development

This repository uses `uv`.

```shell
uv self update
uv python pin 3.14

uv python install
uv lock --upgrade
uv sync

uvx pre-commit install
uv run pre-commit autoupdate

git add -A
uvx pre-commit run --all-files
# repeat if changes were made by pre-commit tasks
uvx pre-commit run --all-files

uv run ty check
uv run python -m pytest
uv run python -m zensical build

# Run engineering self-test
uv run python -m preservation_test.fixtures.build_and_selftest

# save progress
git add -A
git commit -m "your message here"
git push -u origin main
```

## Annotations

[.annotations/annotations.md](./.annotations/annotations.md)

## Citation

Citation metadata is available in [CITATION.cff](./CITATION.cff).

## License

[MIT](./LICENSE)

## Repository Manifest

The repository's role, scope, and dependencies are declared in
[SE_MANIFEST.toml](./SE_MANIFEST.toml).
