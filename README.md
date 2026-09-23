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
```

### Engineering Validation

The engineering self-test is complete and is retained as validation evidence.
Do not rerun it.

```shell
# Historical engineering-validation command:
# uv run python -m preservation_test.fixtures.build_and_selftest

# Verify that the frozen commitment and evaluator still match Freeze 01:
uv run python -m preservation_test.generalization.verification.verify_freeze_01
```

### Generalization Preparation

The numbered generalization steps are deterministic, write-once preparation steps.

They intentionally do not overwrite existing scientific records or preserved
evidence.
Do not delete an existing numbered artifact to make a step run again.
Before Freeze 02, an artifact should be regenerated only when its upstream
input has intentionally changed and the resulting downstream records are being
explicitly invalidated and rebuilt.

```shell
# Derive prior-validation exclusions for the sampling specification
uv run python -m preservation_test.generalization.p01_build_candidates `
    --print-derived-exclusions

# Copy the derived exclusions to generalization/01-sampling.toml.

# Prepare the fixed external sampling frame
uv run python -m preservation_test.generalization.p01_prepare_sampling_frame

# Build the complete source-only candidate inventory
Remove-Item generalization/02-candidates.toml
uv run python -m preservation_test.generalization.p01_build_candidates

# Build the deterministic held-out corpus from eligible candidate units
Remove-Item generalization/03-corpus.toml
uv run python -m preservation_test.generalization.p02_build_corpus

# Preserve the exact selected source bytes and provenance
Remove-Item generalization/04-sources.toml
uv run python -m preservation_test.generalization.p03_preserve_sources

# Install tools
.\install_generalization_tools.ps1

# Construct the complete pre-outcome transformation plan
Remove-Item generalization/05-transformations.toml
uv run python -m preservation_test.generalization.p04_build_transformations `
    --syft bin/generalization/syft.exe `
    --syft-version "1.52.0" `
    --sbom-convert bin/generalization/sbom-convert.exe `
    --sbom-convert-version "0.0.8" `
    --cdx2spdx-jar bin/generalization/cdx2spdx.jar `
    --cdx2spdx-version "0.1.5" `
    --java "bin/generalization/jdk-21.0.12.1+1/bin/java.exe" `
    --java-version "21.0.12.1+1" `
    --sbom-utility bin/generalization/sbom-utility.exe `
    --sbom-utility-version "0.19.2"

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
