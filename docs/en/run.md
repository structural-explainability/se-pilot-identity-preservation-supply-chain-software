# Run Protocol

This document defines the researcher-controlled commitment/evaluator freeze,
engineering validation, generalization freeze, generalization execution, and
adjudication procedure for the software supply-chain identity-preservation
pilot.

Run commands from the repository root.

## Setup

Use the repository's standard `uv` environment: `uv sync`.

`source.json` is the transformation input.
`target.json` is the transformation output.

Run the evaluator. Add `--json` for machine-readable output.

```shell
uv run python -m preservation_test.evaluator.evaluate <source.json> <target.json>
uv run python -m preservation_test.evaluator.evaluate <source.json> <target.json> --json
```

For the repository's synthetic engineering fixture:

<!-- markdownlint-disable MD013 -->

```shell
uv run python -m preservation_test.evaluator.evaluate src/preservation_test/fixtures/source.spdx.json src/preservation_test/fixtures/target.cdx.json

uv run python -m preservation_test.evaluator.evaluate src/preservation_test/fixtures/source.spdx.json src/preservation_test/fixtures/target.cdx.json --json
```

<!-- markdownlint-enable MD013 -->

## Phase 1: Prepare and Freeze Commitment/Evaluator

Before engineering validation, review:

- `contracts/schema.md`;
- `contracts/commitments.toml`;
- `contracts/sources.toml`;
- evaluator implementation;
- format adapters;
- canonicalization logic;
- engineering tests;
- this run protocol; and
- adjudication rules.

The initial commitment/evaluator apparatus is not frozen until we explicitly
create the first freeze.

The freeze record is: `contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`.

The freeze also records the relevant file content hashes.

The generalization corpus and execution conditions are frozen separately in
Phase 3 after engineering validation.

If a frozen schema, commitment, interpretation rule, evaluator, or
adjudication rule must change after engineering validation begins, the
commitment/evaluator freeze is broken.

If a frozen corpus definition or generalization execution condition must change
after generalization execution begins, the applicable generalization freeze is
broken.

If a frozen artifact must be edited:
Record the break, make the correction against authoritative sources, create a
new freeze, and identify subsequent results with the new freeze.

## Phase 2: Engineering Validation

Previously known cases may be used to test whether the frozen evaluator
reproduces expected real-world behavior.

These cases are engineering validation evidence.

They are not blind generalization evidence
when their failure shapes were known during design.

One known validation target is the historical CycloneDX conversion behavior
associated with cyclonedx-cli issue #424.

For a real validation pair:

1. Obtain the source SPDX SBOM.
2. Convert it using the historical tool/version under evaluation.
3. Preserve the source file, target file, tool version, command, and hashes.
4. Run the frozen evaluator against the preserved validation pair.
5. Record the evaluator result.
6. Independently confirm the classification against the applicable
   specifications and mapping rules.

A known-fixed version or independently known-good conversion should also be
evaluated when available.

Expected engineering behavior is not itself sufficient evidence of
generalization.

If a validation case exposes a defect in a frozen commitment or evaluator,
the freeze is broken.

The correction must be grounded in authoritative sources rather than fitted
silently to the observed case.

Confirmed known historical violations may be recorded in:

```text
known/known_violations.toml
```

These labels allow later corpus results to distinguish rediscovery from
previously unrecorded findings.

## Phase 3: Freeze Generalization Corpus and Execution

After engineering validation is complete, define the generalization corpus and
execution conditions before examining any generalization outputs.

The generalization freeze must record at least:

- the applicable commitment/evaluator freeze;
- corpus membership;
- source SBOM identifiers;
- source SBOM content hashes;
- converter identities;
- converter versions;
- transformation directions;
- exact transformation commands;
- source format/version and intended target format/version where known;
- inclusion and exclusion criteria; and
- the procedure for retaining generated target files and evaluator outputs.

The generalization freeze record is: `contracts/FREEZE_02_GENERALIZATION.md`.

The corpus and execution conditions are not frozen until the researcher
explicitly creates this second freeze.

No generalization transformation outputs may be examined before this freeze.

If the frozen corpus definition or execution conditions must change after
generalization execution begins, the **generalization freeze is broken**.
Record the break, make the justified correction, create a new generalization
freeze, and identify subsequent results with the new freeze.

The generalization freeze does not replace or modify the applicable
commitment/evaluator freeze; it records the corpus and execution conditions
under which that frozen evaluator will be tested.

## Phase 4: Generalization Run

The generalization run asks:

> Does the unchanged, source-grounded preservation rule identify valid
> preservation failures in previously unexamined transformation outputs?

The corpus and execution conditions must already be fixed by the applicable
generalization freeze before any outputs are examined.

The corpus definition should record:

- source SBOM identifier;
- source SBOM content hash;
- ecosystem or artifact type;
- converter;
- converter version;
- transformation direction;
- exact transformation command;
- source and target format versions where known;
- generated target content hash.

The initial corpus should include multiple independent transformations rather
than being curated toward known failures.

Candidate coverage may include:

- multiple converters;
- SPDX to CycloneDX;
- CycloneDX to SPDX where supported by the commitment;
- multiple software ecosystems;
- multiple real SBOMs.

For each source/transformation/target tuple, run:

```shell
uv run python -m preservation_test.evaluator.evaluate <source-path> <target-path> --json
```

Retain the resulting JSON output together with the source hash, target hash,
converter identity, converter version, transformation command, and applicable
freeze identifier.

### Phase 4: Result Classification

Experimental results are classified into separate evidence piles.

#### Rediscovered

A `VIOLATED_*` result corresponding to a violation already recorded as known
before the generalization run.

#### New Confirmed

A `VIOLATED_*` result not previously recorded as known that survives the
predefined adjudication procedure.

#### Expected or Refused

Cases for which the method explicitly declines to assert a preservation
violation because the target representation is unsupported or the commitment
is not applicable.

#### Underdetermined

`UNDERDETERMINED` results are reported separately.
They indicate that the authoritative commitment does not determine which valid
source identifier must occupy the target canonical representation under the
declared cardinality rule.
They are not preservation violations and are not silently converted into
passes or failures.

#### False Positive

A `VIOLATED_*` result that does not survive adjudication.

#### Unanchorable

`UNANCHORABLE` results are reported separately.

They are not silently excluded from the denominator.

A high unanchorable rate may indicate that preservation results for a
particular converter or transformation are not interpretable reliably.

### Phase 4: Adjudication Procedure

A candidate preservation violation is confirmed only when the applicable
commitment and authoritative sources support the conclusion.

For a PURL preservation finding, confirm that:

1. the source PURL is present in the source representation in the semantic role
   required by the frozen commitment;
2. the target representation supports the required PURL semantic role;
3. the source and target records are validly associated under the frozen
   anchoring procedure; and
4. the target fails the frozen preservation obligation by dropping, relocating,
   or altering the PURL as defined by the commitment.

Adjudication must use the specifications and frozen commitment.

Similarity to a previously known defect is not sufficient evidence.

A finding that cannot satisfy the frozen adjudication criteria is not counted
as a confirmed violation.

## Phase 5: Assess Generalization

After adjudication, report at least:

```text
known historical violations evaluated
known violations rediscovered
generalization cases evaluated
new candidate violations
new confirmed violations
false positives
unsupported outcomes
underdetermined outcomes
not-applicable outcomes
unanchorable outcomes
```

Do not report only confirmed findings.
The false-positive, refusal, and unanchorable counts are part of the method
evaluation.
A non-empty set of new confirmed violations would provide evidence that the
frozen rule generalized beyond the known engineering examples within the
tested corpus.

A result with no new confirmed violations is also informative.
It may show that the commitment:

- reproduces known preservation failures but does not generalize within the
  tested corpus;
- encounters substantial anchoring limitations;
- encounters representational ambiguity;
- produces unacceptable false positives; or
- accurately finds no additional violations in the tested corpus.

The result should be reported as observed rather than
treated as a failed experiment.

## Later Commitment Kinds

Directional matching conformance, including the historical Grype 0.117/0.118
case, is outside the initial `representation_preservation` commitment kind.

It should be added only as a distinct typed commitment kind after the initial
preservation loop is complete.

Do not modify `representation_preservation` to absorb directional matching
semantics.
