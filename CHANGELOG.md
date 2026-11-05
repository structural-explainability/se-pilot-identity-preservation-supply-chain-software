# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

---

## [Unreleased]

### Added

- Added [Freeze 02 Post-Experiment Notes](./generalization/FREEZE_02_POST_EXPERIMENT.md)
  with route outcomes, preservation verdict counts, and per-route anchoring coverage.
- Added `docs/en/executor.md` documenting executor evidence, environment controls, timeouts, and interruption policy.
- Added formal Freeze 02 generalization execution evidence under `generalization/results/`.
  19 of 20 planned routes completed; one Protobom route recorded an execution failure.
- Added an Evidence Layout section to the Freeze 02 draft record
  describing predeclared evidence paths, `execution.json` lifecycle, and the run manifest.
- Added validator exit-code decision rules, subprocess timeout rules,
  and the executor environment allowlist to the Freeze 02 draft record.
- Added the required contents of an adjudication record to the Freeze 02 draft record.
- Added the complete Freeze 02 artifact-hash inventory to the Freeze 02 draft record,
  including the Java runtime, apparatus modules, predictions, and smoke evidence.
- Added an untracked-file check to the clean-tree guard in `freeze_02.ps1`.

### Changed

- Changed the Freeze 02 draft record to state that the first formal execution of each route is the evidence of record
  and that no retry or resume is implemented under the freeze.
- Changed the Freeze 02 draft record to describe the evaluator invocation as made by the executor's own interpreter
  and to record the Python version in the run manifest.
- Changed the Freeze 02 draft record to name the two defect shapes declared in `known/known_violations.toml`
  and to state that a `rediscovered` match is on direction, verdict, and target location, not on cause.
- Changed the Freeze 02 draft record to separate the eight Protobom and two cdx2spdx `unsupported_pre_execution` routes.
- Changed `README.md` repository structure and Development guidance.
  It now forbids dependency upgrades and reruns of `run.ps1` once smoke preparation is complete.
- Changed the Release Procedure in `CHANGELOG.md` to forbid rerunning `.\run.ps1` after smoke evidence exists.

### Fixed

- Fixed the 0.4.0 section headings in `CHANGELOG.md`.
- Fixed the doubled parenthesis in the Documentation link in `README.md`.
- Fixed the dangling conjunction in the Freeze 02 draft result classes.

---

## [0.4.0] - 2026-11-05

Validated generalization preparation and execution apparatus before SBOM Freeze 02.
This release does not establish the research freeze
or include held-out generalization results.

### Added

- Added `count.ps1` for the source-only count of canonical SPDX source PURLs.
- Added the generalization executor with separate transformation,
  target-validation, and preservation-evaluation evidence.
- Added explicit subprocess timeouts, controlled execution environments,
  execution records, and refusal to overwrite existing results.
- Added explicit Freeze 02 creation and post-freeze integrity verification.
- Added complete Java runtime inventory and SHA-256 verification covering
  every file in the repository-local JDK.
- Added a known-source Windows smoke-test workflow using the pinned
  converters, Java runtime, validator, and frozen evaluator.
- Added narrow execution-plan regeneration that retains corpus membership,
  route classifications, and converter identities.
- Added pre-execution baseline predictions and IdentityOps comparison
  hypotheses in `generalization/PREDICTIONS.md`.
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
- added exact preservation of selected held-out Git blobs under
  `generalization/sources/`
- added `generalization/04-sources.toml` as the provenance and hash record for
  preserved held-out source bytes
- added deterministic pre-outcome transformation-matrix construction for every
  held-out source and declared converter family
- added `generalization/05-transformations.toml` as the pre-outcome execution
  plan for the held-out generalization experiment
- added explicit planned and unsupported-pre-execution route classification
  without replacing unsupported corpus members
- added repo-local installation of the pinned generalization converter toolchain,
  including Syft, Protobom `sbom-convert`, SPDX `cdx2spdx`, and a portable
  Eclipse Temurin JDK
- added repo-local `sbom-utility` target validation as a separately frozen
  experimental instrument
- added predeclared target-validation paths and validation commands for planned
  transformation routes
- added separate target-validity handling so whole-document validity can be
  recorded independently from frozen identity-preservation evaluation

### Changed

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
- updated `.gitignore` to retain generalization transformation logs as research evidence
- updated the generalization tool installer to pin tool versions and centralize
  repository, download, and artifact-path configuration
- updated the generalization transformation plan to freeze exact converter
  artifacts, SHA-256 hashes, tagged documentation references, and the repo-local
  Java runtime used by `cdx2spdx`
- updated Protobom capability declarations to derive supported source versions
  and target versions from centralized constants

### Validated

- Completed the Windows x64 engineering smoke test and its verification.
- Exercised all three declared converters on known validation sources.
- Recorded a maximum subprocess duration of approximately 3.92 seconds
  against the declared 300-second timeout.
- Retained smoke plans, generated targets, evaluator outputs, validation
  results, logs, and execution records under `validation/executor-smoke/`.
- Kept engineering smoke evidence separate from held-out generalization.

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

## Includes earlier work from 2026-09-20

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

These results remain engineering-validation evidence
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

### One-Time Zenodo Authorization

1. Sign in to Zenodo.
2. Open your profile menu in the upper-right.
3. Select GitHub.
4. Click Sync now.
5. Find structural-explainability/ this repo.
6. Turn on the repository toggle/slider.
7. Refresh the page and confirm it appears as enabled.
8. Zenodo will ingest future GitHub Releases from this repo.

### Task 1. Update release metadata (manual edits)

1.1. `CITATION.cff` - update `version` and `date-released`
1.2. `CHANGELOG.md` - add section, move unreleased entries, update links
1.3. `pyproject.toml` - update build system `fallback-version`

### Task 2. Set Up and Validate

```shell
uvx pup-clean --delete
npx markdownlint-cli2 --fix
uvx se-manifest-schema validate-manifest --strict
uvx cffconvert --validate
.\sit.ps1

# Update GitHub Actions and pin all action references to immutable SHAs
uvx gha-tools autoupdate --pin=all --write .github/workflows

# Then audit the resulting GitHub configuration for security findings
uvx zizmor@latest .github/
```

### Task 3. Git Add-Commit-Push, Then Tag

```shell
git add -A
git commit -m "Prep X.Y.Z"
git push -u origin main
```

Verify actions run on GitHub. After success:

```shell
git tag vX.Y.Z -m "X.Y.Z"
git push origin vX.Y.Z
```

### Task 4. Verify the Release and Zenodo archive

The release-on-tag workflow publishes a GitHub Release
for MAJOR and MINOR tags only (vX.Y.0).
PATCH tags (vX.Y.Z, Z > 0) stay as tags.

To verify:

```shell
gh release view vX.Y.Z  # confirm Release exists with notes + artifacts
gh run list --workflow=release-pypi.yml   # confirm the workflow succeeded
```

If Zenodo archiving is enabled, confirm that the release has a
version-specific DOI and is linked to the repository's concept DOI.
Record the DOI in CITATION.cff only when it has been assigned and verified.

```shell
uvx --from se-manifest-schema se-manifest check-version --require-tag
```

Confirms CITATION.cff version matches the pushed git tag.
Run this after `git push origin vX.Y.Z`; it will fail before that point.

## Notes on Freeze

A software release may be created before Freeze 02 is established.

A software release tag does not establish Freeze 02 and does not prevent
additional pre-freeze work.
For changes before Freeze 02, make, validate, and commit those changes normally.

Freeze 02 is established separately by the research-freeze procedure below
against the exact committed pre-freeze state.
A final software release tag may also be created for that state,
but the software tag and the research freeze
remain separate lifecycle events.

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

After engineering validation, the generalization corpus and execution
conditions are frozen separately before any generalization output is examined.

The generalization freeze does not replace the commitment/evaluator freeze.
It records the corpus and execution conditions under which the frozen
Freeze 01 evaluator is tested.

Before Freeze 02 is established,
`contracts/FREEZE_02_GENERALIZATION.md` is a draft and may be revised.

#### Prepare the Final Pre-Freeze-02 State

Complete all intended changes to the generalization design, preparation
implementation, verification, execution procedure, disclosures, and Freeze 02
draft before establishing the freeze.

Dependency updates must already be complete.
Do not run `uv lock --upgrade` as part of this procedure.

Generalization preparation with `.\run.ps1` and the
Windows x64 engineering smoke test must already be complete.

IMPORTANT: Do not rerun `.\run.ps1` once the smoke evidence exists.
It regenerates `05-transformations.toml`, which the smoke evidence was recorded against.
The ordered commands are in the Execution Workflow of `generalization/README.md`.

Review the pre-freeze state, then run the normal repository validation:

```powershell
.\sit.ps1
```

Review all changes before committing.

```powershell
git add -A
git commit -m "Prepare generalization freeze"
git push -u origin main
```

A software release tag may be created for this exact pre-freeze state if
desired, using the normal release procedure above.
The software tag is useful provenance but is not itself Freeze 02.
After committing the final pre-freeze state, do not rerun `run.ps1`.
Verify the committed state without rebuilding it:

```powershell
uv run --locked python -m preservation_test.generalization.verification.verify_05_freeze_02

git status
```

The verification must succeed and `git status` must report a clean working
tree before Freeze 02 is created.

If verification fails or the working tree is not clean, do not create
Freeze 02.
Correct the pre-freeze state, commit the correction, rerun the verification,
and again confirm a clean working tree.

#### Establish Freeze 02

After the final pre-freeze state is committed, verified, and clean, establish
Freeze 02 explicitly:

```powershell
.\freeze_02.ps1
```

The Freeze 02 procedure must not execute a generalization transformation or
inspect any generalization transformation or evaluator output.
Review the finalized freeze record at:

```text
contracts/FREEZE_02_GENERALIZATION.md
```

Confirm that it records the intended corpus, execution conditions, environment,
artifact hashes, limitations, and applicable Freeze 01 commitment/evaluator.
Commit the Freeze 02 record:

```powershell
git add contracts/FREEZE_02_GENERALIZATION.md
git commit -m "Record generalization freeze"
git push -u origin main
```

Do not overwrite `contracts/FREEZE_02_GENERALIZATION.md` after Freeze 02 has
been established.
Do not run `run.ps1` after Freeze 02 has been established.

Formal held-out generalization execution may begin only after the Freeze 02
record has been reviewed and committed.

If a frozen corpus definition, execution condition, environment dependency,
or other Freeze 02 artifact must change after Freeze 02 is established,
follow the freeze-break procedure in `docs/en/run.md`, create a new applicable
generalization freeze, and identify subsequent evidence with that new freeze.

## Only As Needed (delete a tag)

```shell
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
```

## Links

[Unreleased]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/releases/tag/v0.4.0
[0.3.0]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/releases/tag/v0.3.0
[0.1.0]: https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/releases/tag/v0.1.0

<!-- markdownlint-enable MD024 -->
