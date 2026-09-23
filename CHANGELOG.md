# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

## Added

- added Freeze 01 integrity verification against the hashes recorded in `contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`
- added validation evidence hash tests for retained release-sweep targets
- added the Freeze 02 generalization sampling specification in `generalization/01-sampling.toml`
- added the `preservation_test.generalization` implementation for deterministic held-out corpus preparation
- added generalization data models and reusable utilities for candidate enumeration,
  candidate identification, source inspection, deterministic sorting, exclusions,
  Git-blob access, repository preparation, hashing, PURL inspection,
  sampling configuration, source detection, subject resolution,
  TOML generation, and validation-exclusion derivation
- added automated preparation of the fixed CycloneDX and SPDX sampling-frame repositories
  at their pinned revisions
- added deterministic source-only candidate enumeration and screening
- added `generalization/02-candidates.toml` as the complete audit record of screened candidates
- added deterministic corpus construction from eligible candidates using the
  predeclared `source_standard + subject` selection unit and lowest-SHA-256 rule
- added `generalization/03-corpus.toml` as the selected held-out generalization corpus
- added corpus provenance verification against the recorded
  `01-sampling.toml` and `02-candidates.toml` hashes
- added initial Freeze 02 prerequisite verification for the corpus,
  preserved-source record, transformation matrix, and Freeze 01 integrity
- added generalization tests covering sampling configuration,
  source-only screening, deterministic corpus construction,
  provenance and hash handling, and supporting utility behavior
- added test modules corresponding to the generalization utility modules

## Updated

- updated `.gitattributes` to preserve research evidence bytes without Git line-ending normalization
- updated `.pre-commit-config.yaml` to prevent line-ending and
  final-newline hooks from modifying preserved research evidence
- restored retained validation sweep targets to the byte representation matching their previously recorded SHA-256 hashes
- updated generalization tooling to verify Freeze 01 integrity before source-only candidate screening
- updated generalization tooling to derive and enforce prior-validation exclusions before held-out corpus construction
- updated sampling configuration validation to enforce the predeclared census-of-eligible-units method,
  `source_standard + subject` selection unit, and lowest-source-SHA-256 within-unit rule
- updated source-only screening tests to follow the numbered `p01` candidate-inventory and `p02` corpus-construction pipeline
- increased automated test coverage of the repository to more than 70%

---

## [0.3.0] - 2026-09-20

### Added

- Added the reverse-direction exploratory engineering-validation sweep for
  CycloneDX-to-SPDX PURL representation preservation.
- Added the fixed reverse-sweep source artifact from the CycloneDX
  `bom-examples` repository, with recorded provenance and SHA-256 digest.
- Added an explicit reverse release matrix covering cyclonedx-cli
  0.29.0 through 0.33.1 and the associated CycloneDX.Spdx.Interop versions.
- Added `reverse_sweep.py` to execute the fixed release set, run the frozen
  `purl_preservation_v1` evaluator, preserve per-release artifacts, and produce
  aggregate results.
- Added reverse-direction coverage reporting, including applicable,
  evaluable, preserved, violated, unanchorable, underdetermined, unsupported,
  and not-applicable outcomes.
- Added reverse-sweep engineering evidence showing a stable 167-component
  evaluation population across all tested releases.
- Added the observed reverse preservation boundary:
  cyclonedx-cli 0.29.0 through 0.31.0 produced 167/167
  `VIOLATED_DROPPED` results, while 0.32.0 through 0.33.1 produced 167/167
  `PRESERVED` results.
- Added manual structural inspection of generated SPDX 2.3 targets to confirm
  that pre-boundary PURLs are absent from the canonical
  `PACKAGE-MANAGER/purl` ExternalRef representation.
- Added evidence that PURL text is incorporated into generated `SPDXID` values
  whose syntax does not conform to the SPDX 2.3 identifier grammar.
- Added independent SPDX validation with `spdx-tools` for pre-boundary and
  post-boundary targets.
- Added validator evidence showing that the malformed PURL-derived `SPDXID`
  pattern persists across the 0.32.0 preservation boundary, even after
  canonical PURL ExternalRefs begin to appear.
- Added explicit separation between PURL representation-preservation
  conformance and whole-document SPDX validity.
- Added the two-direction engineering-validation comparison:
  forward pre-boundary behavior is `VIOLATED_RELOCATED`, while reverse
  pre-boundary behavior is `VIOLATED_DROPPED`.
- Added preservation of raw validator output and machine-readable validator
  summaries for the reverse sweep.
- Added documentation distinguishing exploratory engineering-validation
  evidence from later held-out generalization evidence.

---

## [0.2.0] - 2026-09-20

### Added

- Real-artifact engineering validation for CycloneDX/cyclonedx-cli issue #424.
- Preserved historical SPDX source provenance recovered from the immutable
  Google Distroless attestation.
- Known-bad validation execution using `cyclonedx-cli` `0.31.0` with
  `CycloneDX.Spdx.Interop` `11.0.0`.
- First-post validation execution using `cyclonedx-cli` `0.32.0` with
  `CycloneDX.Spdx.Interop` `12.1.1`.
- Automated deterministic CycloneDX CLI release sweep using the same preserved
  source, frozen commitment, and frozen evaluator across configured releases.
- Explicit separation of converter execution outcomes from preservation
  verdicts, including `source_parse_failure` when transformation does not
  complete.
- Release-sweep configuration recording dependent library versions, whether
  the dependent library includes the relevant PURL fix, expected execution
  states, and expected evaluator verdicts.
- Per-release generated target and evaluator evidence plus aggregate
  machine-readable release-sweep results.
- Tests for release-sweep configuration invariants and the declared PURL-fix
  boundary.

### Validated

- `cyclonedx-cli` `0.29.0` produces the expected source parse failure for the
  preserved historical source.
- `cyclonedx-cli` `0.29.1` through `0.31.0` produce the expected
  `VIOLATED_RELOCATED` classification.
- `cyclonedx-cli` `0.32.0` through `0.33.1` produce the expected `PRESERVED`
  classification.
- All configured release-sweep execution states and evaluator verdicts match
  their predeclared engineering-validation expectations.

### Documentation

- Documented the known-bad and first-post engineering-validation records.
- Documented the automated release sweep, evidence role, execution/verdict
  distinction, generated artifacts, and interpretation boundaries.
- Updated study status to distinguish completed engineering validation from
  future held-out generalization execution.

These results remain \*_engineering-validation_- evidence
and do not constitute held-out evidence of generalization.

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

git add -A
git commit -m "Prepare commitment/evaluator freeze"

# Regenerate and verify the synthetic fixture against the committed state
uv run python -m preservation_test.fixtures.build_and_selftest

git status
# must report a clean working tree before creating the freeze.
```

The working tree must be clean before creating the freeze.
If rerunning the self-test modifies either generated fixture file, do not
create the freeze.
Review the difference, commit the corrected pre-freeze
state, rerun the self-test, and confirm that the working tree remains clean.

After confirming clean, create the freeze record explicitly:

```shell
.\freeze_01.ps1
```

Review the generated record at `contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`

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

[Unreleased]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/releases/tag/v0.3.0
[0.2.0]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/releases/tag/v0.2.0
[0.1.0]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/releases/tag/v0.1.0

<!-- markdownlint-enable MD024 -->
