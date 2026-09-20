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
preserved / violated / refused / underdetermined
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

Synthetic fixtures and previously known examples
used to verify implementation behavior.

Known examples are not treated as blind evidence
when they were available during development.

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

Before creating the first commitment/evaluator freeze, the researcher will
review the commitment schema, source grounding, implementation, engineering
tests, and adjudication protocol.

After engineering validation, the generalization corpus and execution
conditions will be fixed separately before any generalization run.

No generalization evidence is claimed before the applicable freezes and
subsequent execution.

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

## Repository Guidance

For repository setup, development commands, citation, licensing, and repository
structure, see the [project README](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/blob/main/README.md).
