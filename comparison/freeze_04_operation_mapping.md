# Freeze 04 Operation-to-Language Mapping

## Status

Working mapping.
It precedes any IdentityOps change and any Freeze 04 implementation.
It records what exists at the pinned versions below.
It adopts no language extension.
This file is designated for inclusion in the Freeze 04 inventory.
Its contents become frozen when the Freeze 04 record is established.

## Pinned Subjects

- IdentityOps v0.1.0, commit `7060cd084801e72f2c31175afef035d057979e8a`.
  Read: `SPEC.md`, `SEMANTICS.md`, `DECISIONS.md`, the interpreter and relation modules, and `examples/sbom`.
  See: [se-identity-ops v0.1.0](https://github.com/structural-explainability/se-identity-ops/tree/v0.1.0)
- Interpretive kernel, commit `e895ace0129e321eaf6912718c341ce3eb1644eb`.
  Read: loader, partition, generated, explain, differences.
- Prepared input: `comparison/prepared/freeze_02.json`,
  SHA-256 `17eaa9518e1754a860319532d8e66a317978d3a41fb711a8e47318c23f7699f7`.
- Reference rule: `_anchor_index` and `_anchored_targets` in
  [evaluate.py](../src/preservation_test/evaluator/evaluate.py),
  as of evidence commit `e1befa159faff965b32a47975ac355bb6a9ccb18`.

## Reference Operations

A policy is the set of admitted anchor algorithms.
Baseline: every algorithm the evaluator exposes.
Restricted: SHA-256, SHA-384, and SHA-512 only.
Algorithm-name normalization is the existing handling in both arms.
Algorithm names are matched as spelled in the prepared anchors.
Sources spell SHA-384 as `SHA-384` and targets spell it `SHA384`.
These labels denote the same hash algorithm but remain distinct matching
keys under the preserved handling in both arms.
The restricted policy admits `SHA-256`, `SHA-384`, and `SHA-512` as spelled here.

For each source occurrence:

1. Select the source anchors whose algorithm is admitted.
2. Find the target occurrences that share each selected anchor.
   Sharing means equal algorithm and equal value.
3. Union those targets and keep the anchors that reached each one.
4. Distinguish no selected anchor, zero targets, one target, and several targets.
5. Emit `no_source_anchor`, `no_matching_target`, `authorized`, or `ambiguous`,
   with the anchors and targets behind the class.
6. Compare the two policies for each occurrence.

Step 6 supplies the per-occurrence transition record.
A match needs an equal algorithm, so selecting source anchors alone is enough.
Filtering target anchors by the same allowlist changes no outcome.

## Corpus Facts That Constrain Encoding

Computed from the prepared input, across the 19 completed routes.

- There are 16,795 occurrences.
- 4,273 have no anchor, 9,803 have one, 1 has three, and 2,718 have eight.
- No occurrence has two values for one algorithm.

A single anchor value per occurrence discards anchors for 2,719 occurrences.
One column per algorithm loses nothing.

## Mapping

| Operation                       | IdentityOps v0.1.0                          | Kernel                     | Status                                                              |
| ------------------------------- | ------------------------------------------- | -------------------------- | ------------------------------------------------------------------- |
| 1. Select admitted algorithms   | No construct. E3 uses the declared regimes. | None                       | Convention only                                                     |
| 2. Find targets sharing anchors | `by "column"`, one value per item           | Closure of supplied pairs  | Partial                                                             |
| 3. Union targets, keep anchors  | Class closure. One shortest chain per query | None for anchors           | Partial                                                             |
| 4. Zero, one, or several        | No per-item count                           | Block sizes, in Python     | None                                                                |
| 5. Emit class with evidence     | Outcome word, counts, at most 20 examples   | None                       | Partial                                                             |
| 6. Compare two policies         | No cross-regime construct                   | Partition differences only | Partial; correspondence transitions require separate classification |

### 1. Select admitted algorithms

Kind of work: domain policy, currently performed during extraction.
Experiment B's extractor admitted SHA-256 only and took the first checksum only.
That choice is invisible to the program that reads the table.
Under E3 the choice is the set of declared regimes, which is visible in program text.
No construct names that set as a policy or checks it.
A regime's `meaning` text can name the policy, but it is documentation, not execution.
See: [extract_components.py](https://github.com/structural-explainability/se-identity-ops/blob/7060cd084801e72f2c31175afef035d057979e8a/examples/sbom/extract_components.py)

### 2. Find targets sharing anchors

Kind of work: language semantics, plus extraction of anchors into frames.
`regime NAME on CARRIER by "COLUMN"` relates items with the same non-empty value.
An item with an empty value joins no class.
Each regime reads one value per item.
Under the selected E3 encoding, the adapter retains all algorithm columns.
The restricted policy omits regimes for non-admitted algorithms;
it does not replace their anchor values with empty cells.
See: [SEMANTICS.md, Declarations](https://github.com/structural-explainability/se-identity-ops/blob/7060cd084801e72f2c31175afef035d057979e8a/SEMANTICS.md)

### 3. Union targets, keep anchors

Kind of work: language semantics.
A regime's classes are the transitive closure of its same-commitments.
The evaluator's candidate set is one hop: the targets sharing an anchor with that one source.
The two can differ in general.
`explain` returns a shortest chain found by a fixed search, with its ground (`key`, `judgment`, `step`).
It does not list every anchor that connects two items.
The kernel's `explain` derives identifications between probe outputs through frames.
It does not explain correspondence.

### 4. Zero, one, or several

Kind of work: language gap for counting, and domain policy for the rule that exactly one target authorizes.
`coverage R` reports as silent only items with an empty key and no same-commitment.
An item with an anchor that matches nothing is not silent.
So "no admitted anchor" is distinguished, and "anchor but no match" is not.
`faithful R against S` can use a role probe to count classes whose items differ in role.
It does not give a per-source target count.
`Run.same_classes` exposes the classes to Python.
Counting targets in a class then happens outside the language.

### 5. Emit class with evidence

Kind of work: results vocabulary.
Outcomes are `established`, `refuted`, and `undetermined`, with an operation word, counts, and an explanation.
Examples are capped at 20 with an omitted count.
There is no per-occurrence table.
The four correspondence classes have no direct counterpart.
Any mapping from them to outcomes or limitation causes needs a semantic justification.
Matching three labels to three counts is not a justification.

### 6. Compare two policies

Kind of work: language gap in IdentityOps.
IdentityOps has no construct that compares two regimes.
The kernel's `regime_differences(first, second)` lists each
group one partition makes and the other splits.
It works on partitions of the same frames.

Partition differences alone do not determine correspondence transitions.
Each policy's correspondence classification also requires the presence
or absence of admitted source anchors and the direct target candidate set.
Per-occurrence transitions compare those classifications using the same
source occurrence identifier within each route.

## Candidate Encodings

### E1. One frame per component, one anchor column

This is the Experiment B layout.
It discards anchors for 2,719 occurrences.
It is not adequate for the evaluator's rule.

### E2. One frame per anchor occurrence

Each frame is one (component, algorithm, value).
One regime keys on the `algorithm:value` column.
Anchors of one component are joined with `judge same` statements.
Policy is the set of non-empty values in the column,
so selection happens during extraction.

The proposed baseline encoding uses 19,028 such statements:
2 for the three-anchor occurrence and
7 for each of the 2,718 eight-anchor occurrences.
This count describes the proposed construction;
it is not a demonstrated minimum across possible encodings.

Joining anchor frames belonging to the same component introduces
transitive paths that can reach targets sharing no admitted anchor
directly with the source.
The resulting classes therefore do not implement the direct candidate
rule in general.
Agreement on this corpus would not justify substituting class membership
for direct candidate membership.

Every `judge` creates a state snapshot.
Whether the interpreter handles that volume is not measured.

### E3. (SELECTED) One regime per algorithm over component frames

Each regime keys on one algorithm's column.
Policy is the set of regimes the program declares.
Nine algorithm spellings occur in the prepared anchors.
The baseline policy declares nine regimes and the restricted policy declares three.

That makes the allowlist visible in program text.
There is no construct that combines regimes.
The union across regimes and the exactly-one test happen outside the language.

## Closure Against the Rule

The selected E3 encoding does not raise this question.
Each of its regimes reads one column, so its classes are equal-value groups.
The following observation concerns E2.

A development observation made while drafting compared, for each of the
8,386 source occurrences, the target occurrences in its E2 class with the
evaluator's one-hop candidate set.
The comparison used target occurrence identifiers within each route.
The sets were identical for every source under both policies.

Agreement on this corpus does not establish equivalence between
transitive closure and the direct matching rule.

## Expected Boundary

This section states the expected implementation boundary
for the selected E3 encoding.

The adapter exposes one anchor column per algorithm.
The IdentityOps program declares the regimes corresponding to the
admitted algorithms and computes the within-algorithm relations.

Python combines the target candidates across the selected regimes,
retains their supporting anchors, counts candidates per source,
applies the exactly-one rule, and writes the per-occurrence
classifications and policy transitions.

Freeze 04 assesses this division of responsibility and whether the
language contributes capability beyond the reference apparatus.

## Prior Knowledge Disclosure

These were examined before Freeze 04 and are development observations:

- Restricted-policy counts: authorized 3,983 to 2,858, no source anchor 37 to 2,289,
  no matching target 4,177 to 3,050, ambiguous 189 to 189.
- The closure observation above.

The 189 ambiguous count is unchanged in aggregate.
The per-occurrence comparison must establish whether they are the same occurrences.

## Implementation Decisions

### Evidence Paths

The designated Freeze 04 output directory is `comparison/results/freeze_04/`.

- `reference.json` records the Python reference classifications and anchor
  traces under both policies.
- `identityops.json` records the IdentityOps-assisted classifications and
  anchor traces under both policies.
- `transitions.json` records per-occurrence policy transitions for each
  implementation and disagreements between implementations.

Each source occurrence is identified by route, document side, and JSON Pointer.
Each policy record includes admitted and excluded source anchors, candidate
target identifiers, supporting anchors for each candidate, and
the resulting correspondence classification.

These paths are designated outputs. Their designation does not imply that
the implementations or files already exist.

### Explicitness Comparison

The reference apparatus includes:

- the Python reference implementation;
- `contracts/commitments.toml`;
- `contracts/schema.md`; and
- `contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`.

The IdentityOps apparatus includes:

- the shared extraction specification and adapter;
- the IdentityOps programs for both policies;
- the pinned language specification and semantics; and
- the Python code that combines candidates, classifies correspondence,
  preserves anchor traces, and compares outcomes.

The comparison attributes each policy decision to its actual location:
executable code, program declaration, configuration, or documentation.
A documented decision is distinguished from an executable declaration.

### Language Scope

The initial comparison uses IdentityOps v0.1.0 without a language extension.

Under E3, IdentityOps computes the within-algorithm relations
for the regimes declared by each policy.

Python performs candidate union, target counting,
the exactly-one authorization test,
per-occurrence evidence serialization, and
policy transition comparison.

Gaps identified in mapping rows 4–6 remain outside the language
for this study.
Their consequences are assessed as part of the implementation
boundary rather than addressed through a pre-comparison language extension.

Any subsequent extension constitutes a separately specified study.

### Freeze Readiness

This mapping settles the encoding, responsibility boundaries, and
designated evidence paths.

Freeze 04 establishment additionally requires completed implementations,
output schemas, validation controls, executable commands,
and an artifact inventory that pins the
prepared input and both comparison implementations.
