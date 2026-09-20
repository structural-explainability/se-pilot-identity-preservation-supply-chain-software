# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

---

## [0.1.0] - 2026-09-20

### Added

- Initial `representation_preservation` commitment for Package URL (PURL).
- Source-grounded SPDX 2.3, SPDX 3.0.1, and CycloneDX representation rules.
- Generic preservation evaluator with explicit preservation, violation,
  refusal, underdetermination, and anchoring outcomes.
- Synthetic engineering fixtures covering the implemented verdict classes.
- Focused tests for PURL canonicalization, representation adapters, evaluator
  behavior, and the integrated synthetic self-test.
- Research protocol separating engineering validation from generalization.
- Researcher-controlled commitment/evaluator freeze procedure.

---

## Notes on Versioning and Releases

- We use **SemVer**:
  - **MAJOR** - breaking changes
  - **MINOR** - backward-compatible features
  - **PATCH** - fixes, documentation, tests, tooling
- Versions are driven by git tags. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

### Freezes

- Software releases and research freezes are separate lifecycle events.
- A new software release does not automatically require a new research freeze.
- A new research freeze is required only when the applicable frozen scientific
  artifacts or execution conditions change under the study protocol.

## Release Procedure (Required)

Follow these steps exactly when creating a new release.

### Task 1. Update release metadata (manual edits)

1.1. `CITATION.cff` - update `version` and `date-released`
1.2. `CHANGELOG.md` - add section, move unreleased entries, update links
1.3. `pyproject.toml` - update build system `fallback-version`

### Task 2. Validate

```shell
npx markdownlint-cli2 --fix
uvx se-manifest-schema validate-manifest --strict
uvx cffconvert --validate
.\sit.ps1

uv run python -m preservation_test.fixtures.build_and_selftest
```

### Task 3. Commit, push, tag

```shell
git add -A
git commit -m "Prepare X.Y.Z"
git push -u origin main
```

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

## Research Freeze Procedure

Research freezes are deliberate experimental boundaries and are not created
automatically as part of every software release.

### First Commitment/Evaluator Freeze

The first commitment/evaluator freeze is created after the applicable
scientific artifacts have been reviewed, validated, and committed.
Prepare the committed pre-freeze state:

```shell
npx markdownlint-cli2 --fix
uvx se-manifest-schema validate-manifest --strict
uvx cffconvert --validate
.\sit.ps1

uv run python -m preservation_test.fixtures.build_and_selftest

git status
git add -A
git commit -m "Prepare commitment/evaluator freeze"
```

The working tree must be clean before creating the freeze.
Create the freeze record explicitly:

```shell
.\freeze_01.ps1
```

Review the generated record:

```shell
Get-Content contracts/FREEZE_01_COMMITMENT_EVALUATOR.md
```

Commit the freeze record:

```shell
git add contracts/FREEZE_01_COMMITMENT_EVALUATOR.md
git commit -m "Record commitment/evaluator freeze"
```

Do not overwrite `contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`.

Additional tests and documentation may be added without breaking this freeze
when they only verify or explain the frozen behavior.

If a frozen scientific artifact must change, follow the freeze-break procedure
in `docs/en/run.md` and create a new applicable freeze.

### Generalization Freeze

After engineering validation, freeze the generalization corpus and execution
conditions separately before examining any generalization outputs.

The applicable procedure is defined in `docs/en/run.md`.

The generalization freeze does not replace the commitment/evaluator freeze.
It records the corpus and execution conditions under which the frozen evaluator
is tested.

## Only As Needed (delete a tag)

```shell
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
```

## Links

[Unreleased]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/releases/tag/v0.1.0

<!-- markdownlint-enable MD024 -->
