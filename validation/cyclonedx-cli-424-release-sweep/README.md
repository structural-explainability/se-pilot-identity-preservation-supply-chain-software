# cyclonedx-cli Issue #424 Release Sweep

This directory contains an automated engineering-validation sweep of released
CycloneDX CLI versions against the frozen `purl_preservation_v1` commitment.

The sweep applies the same preserved historical SPDX source, transformation
shape, and frozen evaluator across an explicitly declared sequence of
`cyclonedx-cli` releases.

The release set, dependent library versions, execution expectations, and
preservation-verdict expectations are defined in:

`validation/cyclonedx-cli-424-release-sweep/releases.toml`

That file is the authoritative release-sweep specification.

## Evidence Role

This sweep is **engineering-validation** evidence.
It does not constitute held-out evidence of generalization.

The sweep is intentionally performed while the study is still validating and
stress-testing its scientific apparatus.
Any behavior first observed through this sweep is therefore known
before a future held-out corpus is frozen and
must not later be treated as unseen generalization evidence.

The sweep may be used to:

- verify repeatability of known engineering-validation behavior;
- test whether an observed release boundary is stable across surrounding
  releases;
- identify execution-compatibility boundaries;
- detect unexpected evaluator behavior;
- identify candidate phenomena for later study design; and
- stress-test the frozen evaluator before a subsequent corpus freeze.

## Preserved Source

Every release is evaluated using the same authoritative historical source:

`validation/cyclonedx-cli-424/source.spdx.json`

The source must not be modified to accommodate an older or newer converter
release.

Before executing the sweep, the runner verifies the source SHA-256 recorded in
`releases.toml`.

A release that cannot process the preserved source is recorded as an execution
outcome rather than being given a preservation verdict.

## Frozen Scientific Apparatus

Every successfully generated target is evaluated under the frozen commitment:
`purl_preservation_v1`.

using the frozen scientific apparatus identified by:
`contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`.

The release sweep must not modify the commitment, evaluator, source artifact,
or interpretation rules in response to sweep results.

If the sweep exposes a defect in a frozen scientific artifact, follow the
freeze-break procedure defined by the study protocol rather than modifying the
artifact in place.

## Release Selection

Releases are selected explicitly before sweep execution.
The runner does not discover additional releases dynamically.

The authoritative release list is:
`validation/cyclonedx-cli-424-release-sweep/releases.toml`.

For each release, the configuration records:

- the `cyclonedx-cli` version and tag;
- the dependent `CycloneDX.Spdx.Interop` version;
- whether that dependent library includes the relevant PURL fix;
- the expected execution state; and
- the expected frozen-evaluator verdict when evaluation is applicable.

The field:
`dependent_library_includes_purl_fix`
records a property of the dependent library.
It does not assert that the corresponding CLI execution preserves the PURL.

The field:
`expected_verdict`
records the pre-execution expectation for the frozen evaluator.

The actual evaluator result is recorded separately as:
`observed_verdict`.

## Execution Status and Preservation Verdict

Execution status and preservation verdict are distinct.

A preservation verdict is meaningful only when the converter successfully
produces a target that can be evaluated.

For example:

```text
expected_execution = source_parse_failure
observed_execution = source_parse_failure
expected_verdict = none
observed_verdict = none
```

is distinct from:

```text
expected_execution = completed
observed_execution = completed
expected_verdict = VIOLATED_RELOCATED
observed_verdict = VIOLATED_RELOCATED
```

and:

```text
expected_execution = completed
observed_execution = completed
expected_verdict = PRESERVED
observed_verdict = PRESERVED
```

A source parsing failure must not be classified as `PRESERVED`,
`VIOLATED_RELOCATED`, `UNANCHORABLE`, or another preservation verdict.

The transformation did not occur, so the preservation question was not
evaluated.

## Historical Regression Pair

Two separately preserved engineering-validation cases establish the primary
regression pair:

- `validation/cyclonedx-cli-424/`
- `validation/cyclonedx-cli-424-first-post/`

The **first case** reproduces the historical PURL relocation behavior.

The **second case** evaluates the first identified CLI release
using a dependent library version that includes the relevant PURL conversion fix.

These independently preserved cases remain the primary engineering-validation
records.

The **release sweep supplements them** by testing whether the observed behavior
persists consistently across the surrounding release history.
The sweep does not replace either validation case.

## Running the Sweep

Run from the repository root:

```powershell
uv run python -m preservation_test.validation.release_sweep
```

For each configured release, the runner:

1. acquires the configured Windows x64 release executable;
2. confirms the executable version;
3. records the executable SHA-256;
4. transforms the unchanged preserved SPDX source;
5. records execution failures separately from evaluator results;
6. verifies a successfully generated CycloneDX target;
7. records the target SHA-256;
8. runs the frozen evaluator;
9. preserves the complete machine-readable evaluator result;
10. compares observed execution status with expected execution status;
11. compares applicable observed verdicts with their predeclared expectation;
12. writes an aggregate machine-readable sweep result.

Downloaded executables are retained under the repository-local ignored binary
directory and are not scientific source artifacts.

## Generated Evidence

Per-release generated evidence is written under:

`validation/cyclonedx-cli-424-release-sweep/artifacts/`.

Successful transformations preserve:

```text
artifacts/<version>/target.cdx.json
artifacts/<version>/result.json
```

The aggregate sweep result is:

`validation/cyclonedx-cli-424-release-sweep/results.json`.

The aggregate result records, as applicable:

- release version and tag;
- dependent library version;
- whether the dependent library includes the relevant PURL fix;
- executable-reported version;
- executable SHA-256;
- expected execution status;
- observed execution status;
- expected preservation verdict;
- observed preservation verdict;
- generated target SHA-256;
- CycloneDX format and specification version;
- applicable evaluator verdicts;
- mismatches from the declared expectation; and
- execution error information when transformation does not complete.

## Interpretation

A **matching sweep result** means that the observed execution and preservation
behavior agrees with the expectations declared before the automated sweep.

For the PURL preservation boundary, the intended question is
whether the same frozen identity-preservation commitment:

- detects relocation when the relevant PURL is outside the canonical
  CycloneDX `component.purl` slot; and
- reports preservation when the relevant PURL occupies the canonical slot.

Running the same preserved source across surrounding releases tests whether
that behavioral boundary is repeatable across release history.

An unexpected result is evidence to investigate.
It must not be rewritten to match the expected release boundary.

## Execution Failures

**Execution failures** are preserved as first-class sweep outcomes.
For example, an older release may fail before transformation because it cannot
deserialize a construct in the unchanged historical source.
Such a result establishes an execution-compatibility boundary, not a
preservation verdict.

The runner should continue with subsequent releases when an expected,
classified historical execution failure occurs.
Unexpected failures remain visible in the aggregate result.

## Future Validation Sweeps

Future engineering-validation sweeps may examine additional converters,
directions, formats, or transformations.
Those sweeps remain engineering validation when their results are observed
before the corresponding study corpus is frozen.

When transformations succeed but components cannot be compared under the
frozen commitment, classifications such as `UNANCHORABLE` or
`UNDERDETERMINED` must remain visible rather than being silently excluded.

For broader converter sweeps, anchoring and applicability rates should be
reported alongside preservation violations so that apparent preservation rates
are not interpreted without their coverage context.

Any future held-out generalization study must define and freeze its corpus
selection procedure before observing its evaluation results.

## Observed Results

The configured release sweep completed with all observed execution states and
preservation verdicts matching their predeclared expectations.

```text
0.29.0   source_parse_failure
0.29.1   VIOLATED_RELOCATED
0.29.2   VIOLATED_RELOCATED
0.30.0   VIOLATED_RELOCATED
0.31.0   VIOLATED_RELOCATED
0.32.0   PRESERVED
0.33.0   PRESERVED
0.33.1   PRESERVED
```

The sweep therefore identifies three distinct regions for this preserved
historical source:

1. an initial release that cannot parse the source;
2. a contiguous band of releases that complete the transformation but violate
   the frozen PURL-preservation commitment; and
3. a contiguous band beginning with `cyclonedx-cli` `0.32.0` in which the
   frozen evaluator reports `PRESERVED`.

The transition from `VIOLATED_RELOCATED` to `PRESERVED` coincides with the
first configured CLI release using a dependent `CycloneDX.Spdx.Interop`
version that includes the relevant PURL conversion fix.

These results are **engineering-validation** evidence only.
They do not constitute held-out evidence of generalization.
