# First Commitment/Evaluator Freeze

**Status:** FROZEN

**Frozen (UTC):** 2026-09-20T18:19:16Z

**Frozen content commit:** `ef3a5dacdf1a483f41d87ee955d365376e63a220`

## Purpose

This freeze was explicitly created by the researcher after review of the
pre-execution commitment, implementation, tests, and protocol.

It fixes the initial `representation_preservation` commitment and the
scientific implementation used for subsequent engineering validation.

The pilot was motivated in part by previously known preservation failures,
including the general failure shape reported in cyclonedx-cli #424.

Accordingly, the initial commitment and evaluator are not a blind first test
of that historical case. Previously known cases are engineering validation
evidence, not held-out evidence of generalization.

The files listed below define the frozen representation-preservation
commitment, its authoritative provenance, its interpretation rules, its
implementation, and its adjudication protocol.

Any case used as evidence of generalization must not have been examined
before the applicable generalization freeze.

## Frozen Artifacts

- `contracts/schema.md`
- `contracts/sources.toml`
- `contracts/commitments.toml`
- `src/preservation_test/evaluator/purl_canonical.py`
- `src/preservation_test/evaluator/formats.py`
- `src/preservation_test/evaluator/evaluate.py`
- `docs/en/run.md`

## Frozen Content Hashes

- `0152c46447091a8275a75763d678f1e06901fc2cd2a7abebceccee41aeca1cb7`  `contracts/schema.md`
- `f0882a8eca596ec5ec7fb5557a1d390844c33c2420187fe3b8041b78b4f63c60`  `contracts/sources.toml`
- `e8f78876ffeba76f1875a3b9a01f2ceafa2dba140544c32ebaa09087406eb539`  `contracts/commitments.toml`
- `3ff56f45fafca7097cc73171c16b1f8dddf0487ffbffeee436cddc05c90ff427`  `src/preservation_test/evaluator/purl_canonical.py`
- `6aac22257a25db0464588310af2dfd7e109bb6e31c31c644bee335febfc2a03a`  `src/preservation_test/evaluator/formats.py`
- `8f4c8893bcb45447baad016d18e10658f7d40b23101e4da1d79bb4316073984d`  `src/preservation_test/evaluator/evaluate.py`
- `e629d4f9a75f8955f14be848056c91247feefa182fbb6423163eb465d1abcf3b`  `docs/en/run.md`

## Post-Freeze Testing

Additional tests may be added after this freeze without breaking it if they
only verify the behavior of the frozen artifacts.

If a new test reveals that a frozen artifact must change, the freeze is
broken. The defect must be recorded, corrected against the authoritative
sources, and followed by a new explicit commitment/evaluator freeze before
generalization execution.

A recorded-and-continued edit is not permitted. Changes to frozen scientific
content require an explicit new freeze.

## Engineering Validation

Cases whose failure shape or relevant behavior was known during study design
remain engineering validation evidence even when executed after this freeze.

Successful reproduction of such cases does not constitute evidence of
generalization.

## Freeze-Break Log

None.
