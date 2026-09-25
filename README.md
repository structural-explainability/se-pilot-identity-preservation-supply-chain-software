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

## Current Engineering Validation

The frozen `purl_preservation_v1` commitment and evaluator have been exercised
against historical artifacts from CycloneDX/cyclonedx-cli issue #424.

The engineering validation establishes a **release-history boundary** for the same
preserved SPDX source and transformation direction:

```text
cyclonedx-cli 0.29.0
    source_parse_failure

cyclonedx-cli 0.29.1 through 0.31.0
    VIOLATED_RELOCATED

cyclonedx-cli 0.32.0 and subsequent releases in the configured sweep
    PRESERVED
```

The applicable pre-fix releases therefore reproduce the historical PURL
relocation behavior, while releases using the dependent library after the
relevant PURL conversion fix preserve the PURL in the canonical CycloneDX
`component.purl` slot.

The automated release sweep evaluates the same preserved source with the same
frozen commitment and evaluator across the explicitly declared release
sequence.
It also records execution failures separately from preservation verdicts,
so inability to process the source is not conflated with a
representation-preservation failure.

This result demonstrates that the frozen evaluator distinguishes the known
preservation defect from its absence across the tested release boundary rather
than merely identifying differences between generated documents.

These results remain **engineering-validation** evidence.
The issue, defect shape, converter, transformation direction,
and release boundary were known or examined during validation
and therefore do not constitute held-out evidence of generalization.

The preserved validation cases are under [`validation/`](./validation/), and
the automated release-sweep specification and results are under
[`validation/cyclonedx-cli-424-release-sweep/`](./validation/cyclonedx-cli-424-release-sweep/).

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

# Verify that uv.lock still matches pyproject.toml.
# Do not update dependency resolution during ordinary development.
uv lock --check

uv sync --locked
uv audit --frozen

# Update GitHub Actions and pin all action references to immutable SHAs
uvx gha-tools autoupdate --pin=all --write .github/workflows

# Then audit the resulting GitHub configuration for security findings
uvx zizmor@latest .github/

uv run --locked prek install -f
uv run --locked prek update --freeze --cooldown-days 7

git add -A
uv run --locked prek run --all-files
# repeat if changes were made
uv run --locked prek run --all-files

# run common chores (formats Python in .md files also)
uv run --locked ruff format .
uv run --locked ruff check . --fix
uv run --locked ty check
uv run --locked python -m pytest
uv run --locked python -m zensical build
# audit dependencies (advisory: findings are reported, nothing blocks)
uv audit --frozen
```

### Dependency Updates

Dependency updates are deliberate maintenance operations and are not part of
ordinary development, SIT, engineering validation, or generalization
execution.

For the current experiment, dependency updates have stopped.

Engineering validation is complete, and the generalization preparation
artifacts have already been generated.
Do not run `uv lock --upgrade` again before or during Freeze 02 execution.

For a future maintenance cycle, before beginning a new experimental preparation
sequence, dependencies may be updated with:

```shell
uv lock --upgrade
uv sync --locked
git diff -- pyproject.toml uv.lock .python-version
uv run --locked ty check
uv run --locked python -m pytest
uv run --locked python -m zensical build
```

Review and commit any dependency changes explicitly before beginning the next
experimental preparation sequence.

### Engineering Validation

The engineering self-test is complete and is retained as validation evidence.
Do not rerun it.

```shell
# Historical engineering-validation command:
# uv run --locked python -m preservation_test.fixtures.build_and_selftest

# Verify that the frozen commitment and evaluator still match Freeze 01:
uv run --locked python -m preservation_test.generalization.verification.verify_01_freeze_01
```

### Generalization Preparation

Generalization preparation is performed by the repository-root `run.ps1`
script.
Run `.\run.ps1` **only before Freeze 02 is established**.

It rebuilds the generated generalization artifacts from `02-candidates.toml`
through `05-transformations.toml` and runs the required verification gates.

Do not run it after Freeze 02 is established or after formal generalization
execution has begun.

After it succeeds, review and commit the resulting pre-freeze state before
establishing Freeze 02.

```shell
# save progress
git add -A
git commit -m "your message here"
git push -u origin main
```

## Generalization Overview

- [README.md](./generalization/README.md)

## Generalization Inputs

- [01-sampling.toml](./generalization/01-sampling.toml)

## Generalization Toolchain

- [install_generalization_tools.ps1](./install_generalization_tools.ps1)

## Generalization Generated Artifacts

- [02-candidates.toml](./generalization/02-candidates.toml)
- [03-corpus.toml](./generalization/03-corpus.toml)
- [04-sources.toml](./generalization/04-sources.toml)
- [05-transformations.toml](./generalization/05-transformations.toml)

## Annotations

[.annotations/annotations.md](./.annotations/annotations.md)

## Citation

Citation metadata is available in [CITATION.cff](./CITATION.cff).

## License

[MIT](./LICENSE)

## Repository Manifest

The repository's role, scope, and dependencies are declared in
[SE_MANIFEST.toml](./SE_MANIFEST.toml).
