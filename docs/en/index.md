# SE Pilot Overview: Identity Preservation in Software Supply Chains

> A feasibility pilot for source-grounded identity-preservation conformance
> across software supply-chain representations.

## Purpose

This project tests whether security-relevant identity commitments can be
defined from authoritative sources and evaluated systematically across
software supply-chain transformations.

The initial test is intentionally narrow:

- commitment kind: `representation_preservation`;
- identifier: Package URL (PURL);
- representations: SPDX and CycloneDX SBOMs;
- question: whether identity information survives a representation
  transformation in its canonical target location.

The project does not begin by searching for implementation defects.

It defines the preservation obligation first, establishes the evaluation
procedure, freezes the commitment and evaluator under researcher control, and
then performs engineering validation before any separately frozen
generalization execution.

## Research Motivation

Software supply-chain tools routinely transform records describing the same
components between different representations.

A transformation can remain syntactically valid while changing, relocating, or
losing identity-bearing information used by downstream security tooling.

For example, two formats may both support PURL while representing it in
different structural locations.

The relevant conformance question is therefore not merely:

> Is the transformed document valid?

It is:

> Did the transformation preserve the source-grounded identity semantics
> required on the target side?

## Initial Method

The initial pipeline is:

```text
authoritative specifications
        ↓
typed representation-preservation commitment
        ↓
representation-specific adapters
        ↓
generic evaluator
        ↓
explicit preservation or limitation classification
        ↓
finite evidence
```

The evaluator is separated from format-specific parsing.

It must not contain special cases for particular packages, historical bugs,
converters, or artifacts.

## Initial Commitment

The first commitment concerns PURL preservation across SPDX and CycloneDX.

Conceptually:

```text
source component
        ↓
independently anchor corresponding target component
        ↓
inspect source canonical PURL representation
        ↓
inspect target canonical PURL representation
        ↓
classify preservation outcome
```

The evaluator distinguishes preservation violations from explicit refusal or
limitation outcomes.

A transformation must not be classified as violating a preservation
commitment when the target representation cannot express the relevant
semantic construct or when the corresponding target component cannot be
established reliably.

See the [Run Protocol](./run.md) for the verdict vocabulary and adjudication
rules.

## Evidence Roles

The pilot distinguishes three evidence roles.

### Design Evidence

Specifications and documented mappings used to define the commitment,
representation semantics, and adjudication rules.

### Engineering Validation Evidence

Synthetic fixtures, previously known examples, controlled regression pairs,
and exploratory release sweeps used to verify evaluator behavior and
repeatability.

Known examples and behaviors observed during engineering validation are not
treated as held-out evidence when they were available before the
generalization corpus is frozen.

### Generalization Evidence

Previously unexamined transformation outputs evaluated only after the
commitment, evaluator, and adjudication procedure have been frozen and the
generalization corpus and execution conditions have been separately fixed.

The generalization stage tests whether the frozen preservation rule identifies
useful preservation failures beyond the examples known during development.

## Role in Structural Explainability

This pilot is part of the Structural Explainability research program.

It is informed by the SE-210 Operational Identity framework but does not assume
that every software supply-chain semantic rule
is an SE-210 operational-identity relation.

This initial pilot tests the lower-level preservation-conformance primitive
first.
It is not an SE-210 partition audit.

If observed transformations later produce non-trivial competing identity
groupings, the study can then evaluate whether SE-210 provides additional
structural analysis beyond the preservation checker itself.

Related work:

- [SE-210 Operational Identity paper](https://arxiv.org/abs/2607.20729)
- [Executable verification of the SE-210 finite mathematical core](https://github.com/structural-explainability/se-verification-operational-identity)

## Broader Research Direction

Software supply chains are the first proving ground for the
identity-preservation method.

The broader research question is whether the same source-grounded method can
support other domains in which identity must survive or change predictably
across representation, custody, provenance, aggregation, transformation, or
interpretation.

Potential later pilots may address other supply chains,
including energy, AI, or legal domains.

## Current Status

The initial commitment and evaluator are frozen under:

`contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`

Engineering validation has been completed against real historical artifacts
from CycloneDX/cyclonedx-cli issue #424.

The known-bad execution using `cyclonedx-cli` `0.31.0` with
`CycloneDX.Spdx.Interop` `11.0.0` produces `VIOLATED_RELOCATED`.

The first identified CLI release using a dependent library that includes the
relevant PURL fix, `cyclonedx-cli` `0.32.0` with
`CycloneDX.Spdx.Interop` `12.1.1`, produces `PRESERVED`.

An automated release sweep additionally evaluates the same preserved source,
transformation direction, frozen commitment, and evaluator across surrounding
released CLI versions.

The release sweep remains engineering-validation evidence because its release
history and results are examined before any separately frozen generalization
corpus.

No held-out generalization evidence is currently claimed.

The generalization corpus and execution conditions will be fixed separately
before any generalization execution.

For freeze, execution, corpus, and adjudication procedures, see the
[Run Protocol](./run.md).

For synthetic fixtures and engineering validation, see the
[Test Guide](./test.md).

## Study Artifacts

The study separates the following.

- [Commitment schema](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/blob/main/contracts/schema.md)
  defines the typed commitment model.
- [Commitments](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/blob/main/contracts/commitments.toml)
  contains the encoded commitments.
- [Sources](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/blob/main/contracts/sources.toml)
  records authoritative source provenance.
- [Freeze record](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/blob/main/contracts/FREEZE_01_COMMITMENT_EVALUATOR.md)
  records the researcher-controlled freeze of the initial commitment,
  interpretation rules, evaluator, and adjudication protocol.
- [Run Protocol](./run.md) defines freeze, corpus, execution, and adjudication procedures.
- [Test Guide](./test.md) defines synthetic fixtures and engineering validation.

### Validation Evidence

- [Engineering validation](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/blob/main/validation/README.md)
  records the known historical validation cases and their adjudicated results.

- [Release sweep](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/blob/main/validation/cyclonedx-cli-424-release-sweep/README.md)
  documents the automated engineering-validation sweep across released
  `cyclonedx-cli` versions.

## Repository Guidance

For repository setup, development commands, citation, licensing, and repository
structure, see the [project README](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/blob/main/README.md).
