# Freeze 02: Generalization Corpus and Execution

> Fixed conditions under which the generalization experiment will be run.

## Scope

## Frozen Generalization Artifacts

## Transformation Execution

## Target Validity

Target-document validity is recorded independently from transformation
execution and identity-preservation evaluation.

For every planned transformation route:

- a nonzero converter exit or absence of a target file is an execution failure;
- a successful converter execution that produces a target proceeds to target
  validation;
- target validation records whether the generated target is valid under the
  applicable target representation;
- an invalid target is retained and is not reclassified as an execution failure;
- when the frozen evaluator can process the target, identity-preservation
  evaluation proceeds regardless of whole-document validity; and
- target validity and identity-preservation verdict are reported as separate
  dimensions.

A successfully generated target may therefore be valid or invalid independently
of whether the frozen identity-preservation evaluator reports preservation,
violation, or another evaluator outcome.

Whole-document validity does not override, relabel, or modify a frozen evaluator
verdict.

## Known Limitations and Disclosures

## Verification

## Frozen Hashes
