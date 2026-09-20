# Representation-Preservation Engineering Tests

This document describes the engineering validation used before experimental
execution.

These tests verify that the implementation behaves consistently with the
declared commitment and verdict model.

They do not constitute generalization evidence.

## Initial Scope

The initial implementation supports one commitment kind:

```text
representation_preservation
```

The initial identifier is Package URL (PURL).

The initial representation adapters support SPDX and CycloneDX.

The implementation is organized under:

```text
src/preservation_test/

    evaluator/
        evaluate.py
        formats.py
        purl_canonical.py

    fixtures/
        build_and_selftest.py
        source.spdx.json
        target.cdx.json
```

The declarative research artifacts are maintained separately:

```text
contracts/
    schema.md
    commitments.toml
    sources.toml
    FREEZE_01_COMMITMENT_EVALUATOR.md
```

Known historical labels are maintained under:

```text
known/
    known_violations.toml
```

The execution and freeze procedure is defined in:

```text
docs/en/run.md
```

## Design Invariants

The implementation should preserve the following separation of concerns.

### Generic evaluator

`evaluate.py` knows:

- the typed commitment;
- preservation obligations;
- the verdict vocabulary;
- generic evaluation flow.

It must not contain special cases for:

- particular bugs;
- particular packages;
- particular SBOM artifacts;
- particular converter versions.

### Format adapters

`formats.py` knows how supported representations encode the semantic fields
required by the evaluator.

Format-specific representation details belong here rather than in the generic
evaluation logic.

### PURL interpretation

`purl_canonical.py` handles PURL interpretation and canonicalization.

PURL semantics should be grounded in the Package URL specification and
reference implementation rather than project-specific normalization rules.

### Anchoring

The identifier whose preservation is being tested must not be the sole basis
for establishing that the source and target records correspond.

Missing or ambiguous correspondence must be reported rather than silently
resolved.

## Synthetic Self-Test

Run the synthetic engineering self-test from the repository root:

```shell
uv run python src/preservation_test/fixtures/build_and_selftest.py
```

The synthetic fixtures should exercise the evaluator's supported outcome
classes.

Current outcome classes include:

```text
PRESERVED
VIOLATED_DROPPED
VIOLATED_RELOCATED
VIOLATED_ALTERED
UNSUPPORTED
UNANCHORABLE
NOT_APPLICABLE
```

The purpose of these fixtures is to verify implementation behavior.

They do not establish that any real converter violates a preservation
commitment.

## Verdict Expectations

### PRESERVED

The required source identity value is represented in the required canonical
target location under the frozen commitment.

### VIOLATED_DROPPED

The required source identity value is not represented in the target as required
by the commitment.

### VIOLATED_RELOCATED

The required identity value survives in the target representation but not in
the semantic location required by the commitment.

### VIOLATED_ALTERED

A corresponding target identity value exists, but the value differs in a way
classified as non-preserving by the commitment.

### UNSUPPORTED

The target representation cannot support the required semantic obligation
under the commitment.

This is a refusal, not a violation.

### UNANCHORABLE

The evaluator cannot establish the required source-to-target component
correspondence under the anchoring procedure.

This is reported explicitly and must not be silently discarded.

### NOT_APPLICABLE

The source record does not satisfy the applicability conditions for the
commitment.

This is not a violation.

## Test Suite

Run the repository tests with:

```shell
uv run python -m pytest
```

Static checks are run with:

```shell
uv run ty check
```

Repository-wide checks are run with:

```shell
uvx pre-commit run --all-files
```

Documentation is validated with:

```shell
uv run python -m zensical build
```

These engineering checks may be executed repeatedly during development.

They are distinct from the frozen experimental execution described in the
[Run Protocol](./run.md).

## Freeze Boundary

Engineering self-tests may be developed and executed before the experimental
freeze.

Once the researcher creates the experimental freeze, changes to frozen
scientific artifacts must follow the freeze-break procedure defined in the
[Run Protocol](./run.md).

The presence of passing synthetic tests does not itself establish that the
experiment has been frozen or that the method has generalized to real
transformations.
