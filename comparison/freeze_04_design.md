# IdentityOps Language Comparison - Original Exploratory Design

## Status

SUPERSEDED for the selected Freeze 04 study.
This file records the original exploratory framing.
It is not in the Freeze 04 inventory.

The selected study is defined in
[freeze_04_operation_mapping.md](./freeze_04_operation_mapping.md)
and [freeze_04_specification.md](./freeze_04_specification.md).

The freeze-record path is:
`contracts/FREEZE_04_IDENTITYOPS_COMPARISON.md`

## Relationship to Earlier Studies

Freeze 02 established the baseline preservation results.

Freeze 03 concerns the interpretive kernel's missing-value policies.
Its design is recorded in
[freeze_03_design.md](./freeze_03_design.md).

This planned study addresses the IdentityOps language.

The original L1–L4 hypotheses remain preserved in
[generalization/PREDICTIONS.md](../generalization/PREDICTIONS.md).

## Candidate Evidence and Implementation Pins

These pins identify the starting point for the design.
The completed Freeze 04 specification must identify every version actually used.

- Baseline run-start commit:
  `9baa72323301e287a4f3c821cb638f5165b3a29a`.
- Committed baseline evidence:
  `e1befa159faff965b32a47975ac355bb6a9ccb18`.
- Candidate IdentityOps version:
  `v0.1.0`, commit `7060cd084801e72f2c31175afef035d057979e8a`.

[IdentityOps v0.1.0](https://github.com/structural-explainability/se-identity-ops/tree/v0.1.0)

## Intended Questions

### L1. Agreement on the Shared Evaluable Subset

Can an IdentityOps program reproduce the pilot's preservation judgment
for occurrences satisfying the declared common eligibility conditions?

The original conditions require exactly one valid canonical source PURL
and a unique target association established independently of that PURL.

Compute and report the eligible denominator by route before scoring agreement.

If matching and normalization are reused from the pilot,
describe agreement on those stages as inherited from the shared preparation.
The comparison then tests the program, regime encoding, and outcome mapping.

### L2. Canonical and Alternative-Slot Probes

For an independently established relocation case, does the canonical-slot
probe disagree while a declared recovery probe agrees?

Report the hypothesis as unevaluable on any evidence population
with no qualifying case.

IdentityOps Experiment B provides existing engineering-validation evidence.
Any reuse of that evidence must retain its engineering-validation designation.

[IdentityOps Experiment B](https://github.com/structural-explainability/se-identity-ops/tree/v0.1.0/examples/sbom)

### L3. Evidence Accounting

Re-expression of the same observations is expected to reproduce their
consequences on the shared subset.

Any additional finding must identify the new observation or commitment
and receive the adjudication required by the study.

### Additional Utility Question

Before implementation, decide whether the study will measure a benefit
beyond agreement with the existing evaluator.

If so, specify:

- the task being performed;
- the comparison method;
- the output or evidence the language adds;
- the observable measure of that addition; and
- the criterion for reporting success, failure, or an unevaluable result.

Claims about inspectability or reproducibility require an explicit assessment.

## Decisions Required Before Freeze 04

1. Define the primary study question and its acceptance criteria.
2. Fix the evidence population and preserve its provenance.
3. Specify occurrence identity and source–target correspondence authorization.
4. Specify canonical and alternative PURL slots.
5. Specify malformed, missing, and multiple-value handling.
6. Fix the normalization implementation and version.
7. Define the IdentityOps program and regime encoding.
8. Define the mapping from program outputs to the comparison claims.
9. Select engineering controls that exercise preservation and loss or relocation.
10. Define the report fields, commands, environment, and integrity inventory.

## Adapter-Scope Exploration

The baseline analysis identified two possible later changes:

- including CycloneDX `metadata.component`; and
- admitting hashes from additional locations under a stated interpretation rule.

These questions arose after examining baseline results.
Any study adopting them must disclose that chronology and specify its
changed extraction and authorization rules before execution.

Their inclusion in Freeze 04 requires an explicit design decision.

## Implementation and Outputs

Implementation paths will be selected when the design is complete.
The Freeze 04 inventory will cover every implementation and configuration
used for the study.

The kernel study's preparation can be reused only after checking that
its occurrence scope and eligibility rules satisfy this study's questions.

Every formal output must identify its input evidence, implementation,
program, normalization, and freeze record.

## Next Design Deliverable

Complete the primary question and outcome mapping first.

Then implement and validate the adapter and IdentityOps program,
record commands and expected control outcomes,
and establish Freeze 04 before formal execution.
