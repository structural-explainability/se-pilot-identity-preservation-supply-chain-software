# Engineering Validation Evidence

This directory contains real-world engineering-validation cases
evaluated against the frozen commitment/evaluator apparatus.

These cases are not generalization evidence.

A validation case may be included here when its relevant behavior or failure
shape was known during study design, or when it is intentionally selected as
a known-good control.

Each case directory should preserve or reference:

- the authoritative source representation;
- the generated target representation;
- source and target content hashes;
- converter identity and version;
- the exact transformation command;
- the applicable commitment/evaluator freeze;
- the evaluator command;
- the machine-readable evaluator result; and
- the expected and adjudicated classifications.

Validation cases must not modify the frozen commitment or evaluator merely to
produce an expected result.

If validation exposes a defect in a frozen scientific artifact, follow the
freeze-break procedure in `docs/en/run.md`.

## Initial Engineering Validation Results

### 1. `validation/cyclonedx-cli-424`

```text
0.31.0 / Spdx.Interop 11.0.0
expected: VIOLATED_RELOCATED
observed: VIOLATED_RELOCATED
```

### 2. `validation/cyclonedx-cli-424-first-post`

```text
0.32.0 / Spdx.Interop 12.1.1
expected: PRESERVED
observed: PRESERVED
```
