# Pre-execution predictions

Prepared: 2026-11-05.

These predictions are reviewed and committed
before the first held-out generalization transformation is executed.

The prediction record is included in Freeze 02's artifact inventory.
Its prospective status depends on the committed chronology.

## Evidence boundary

Known-case engineering validation has been examined.

The held-out experiment uses the corpus and routes declared in
01-sampling.toml through 05-transformations.toml.

No held-out transformation was run while preparing this prediction record.

Predictions are not selection rules.
Unexpected outcomes do not authorize replacing sources, converters,
routes, or reported observations.

## Baseline predictions

### B1: Source-side anchoring limitation

Source-only inspection found six canonical PURL occurrences across the two
SPDX sources, of which five have content hashes.

For each successfully evaluated route over the SPDX source containing the
unhashed PURL, that occurrence is expected to be UNANCHORABLE under the
unchanged evaluator.

Additional UNANCHORABLE results may arise from absent or ambiguous target
anchors.

Basis: the evaluator requires a source content-hash anchor
independently of whether the PURL survives conversion.

### B2: Directional relocation limitation

CycloneDX-to-SPDX routes will not produce VIOLATED_RELOCATED
under the frozen evaluator.

A PURL retained outside the recognized SPDX canonical external-reference
slot may instead receive VIOLATED_DROPPED.

Basis: the frozen SPDX adapter does not collect noncanonical PURL locations.

### B3: Rediscovery classification

Under the currently declared known-defect shapes,
a confirmed CycloneDX-to-SPDX VIOLATED_DROPPED result
will be classified as rediscovered.

Only VIOLATED_ALTERED can be new confirmed in that direction.

Basis: known/known_violations.toml and the frozen evaluator vocabulary.

No exact count of preserved observations, confirmed violations,
execution failures, or new findings is predicted.

No converter ranking is predicted.

## IdentityOps comparison hypotheses

These hypotheses precede the baseline run.
They do not constitute a completed specification or
freeze of the later IdentityOps comparison.

Before running that comparison, separately freeze its adapter,
language implementation, inputs, programs, normalization,
missing-value rules, and outcome mapping.

### L1: Agreement on the common evaluable subset

For source components with exactly one valid canonical PURL and a unique,
independently established hash-based target association,
an IdentityOps canonical-PURL probe is expected to agree
with the pilot regarding whether the canonical PURL value is preserved.

Compare only this explicitly shared subset.
Do not treat omitted or unsupported cases as agreements.

A disagreement is evidence to investigate the adapter, normalization,
probe semantics, or mapping.

### L2: Relocation has a distinct probe pattern

When the source PURL is absent from the target canonical slot but
retained unchanged in a declared alternative slot:

- the canonical-slot comparison is expected to disagree;
- a probe that explicitly recovers that same PURL from either declared slot
  is expected to agree.

The extraction rule must be fixed before comparison.
A generic concatenation or unordered collection is not assumed equivalent
to the pilot's scalar preservation test.

### L3: The language alone does not create new defect evidence

Re-expressing the same observations in IdentityOps is expected
to reproduce consequences on the shared subset.

Additional explanations or witnesses are not new real-converter violations.

Any claimed additional finding must identify the
new observation or commitment and receive independent adjudication.

### L4: Missing-value sensitivity

Run the kernel comparison under both declared policies:

- DISTINCT: separate missing cells are distinct outputs.
- SHARED: missing cells share an absent output within a probe.

For fixed probes and frame regime,
pairwise comparisons with two missing cells are expected
to differ between the policies:
they disagree under DISTINCT and agree under SHARED.

Direct pairwise comparisons between two observed values
are expected to remain unchanged.

Generated equivalence closures may differ more broadly
because SHARED can introduce additional chains.

Report both policies separately, including missingness counts,
witnesses, and any changes in generated identifications.
Do not select a preferred policy after seeing which gives a stronger result.

## Reporting

Report met, contradicted, and unevaluable predictions.

Report execution and evaluation failures separately
from preservation verdicts.

Retain unsupported, underdetermined, unanchorable, and
not-applicable observations.

A conditional prediction whose conditions were never met
is unevaluable, not confirmed.
