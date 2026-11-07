# Freeze 03: Kernel Missing-Value Comparison Results

## Summary

The kernel comparison evaluated 19 completed baseline routes under
DISTINCT and SHARED missing-value policies.

Both policies produced identical direct agreement counts.
No generated identifications among distinct observed PURL values changed.

The observed-value control was met on all 19 evaluated routes.
The two-missing prediction was unevaluable on every route because
no eligible source occurrence had a missing canonical PURL.

These outcomes match the expectations derived from preparation counts
examined before Freeze 03.

## Evidence and Provenance

- Preparation-state commit:
  `e43848ac8f27bd891c0d37bf01e9063c6f883db6`.
- Freeze-record commit:
  `99ad51c3a4fc415bb4880a05d43b5c4668f3bc3b`.
- Prepared-input and result commit:
  `a0463f4c6db027eff8f692954e751dd3098f780b`.
- Baseline evidence commit:
  `e1befa159faff965b32a47975ac355bb6a9ccb18`.
- Interpretive kernel commit:
  `e895ace0129e321eaf6912718c341ce3eb1644eb`.

Study artifacts:

- [Frozen design](./freeze_03_design.md)
- [Freeze 03 record](../contracts/FREEZE_03_KERNEL_MISSING_VALUES.md)
- [Prepared input](./prepared/freeze_02.json)
- [Kernel results](./results/l4/run.json)

The committed execution evidence is available at
[evidence commit a0463f4](https://github.com/structural-explainability/se-pilot-identity-preservation-supply-chain-software/commit/a0463f4c6db027eff8f692954e751dd3098f780b).

## Integrity Verification

The execution transcript records successful Freeze 03 verification
before preparation, between preparation and execution, and after execution.
All three checks returned the same freeze-record digest:

```text
Freeze 03 verified: c63a973075b6ffe1f9d8a53fbc1fed2997f19646f195d729590e123e2d295ca4
```

Review of the committed artifacts confirmed that all six inventory
digests match the files recorded by Freeze 03.

The prepared-input and runner digests also match the values recorded
in `comparison/results/l4/run.json`.

| Artifact         | SHA-256                                                            |
| ---------------- | ------------------------------------------------------------------ |
| Freeze 03 record | `c63a973075b6ffe1f9d8a53fbc1fed2997f19646f195d729590e123e2d295ca4` |
| Prepared input   | `17eaa9518e1754a860319532d8e66a317978d3a41fb711a8e47318c23f7699f7` |
| L4 runner        | `144b7ab334860bf6f8c2130d05b1acc2e76099a3197155e19ca5f66d2f7ed8cb` |
| L4 result        | `6cb06a3bd5e51d72b38f3b864e67329cc5feaa67b4c5038402a6ab8e1aab9a33` |

The committed-artifact review did not rerun the converters or formal
kernel computation.

## Route Population

The prepared input and result retain all 30 baseline route records:

- 19 completed routes received kernel comparison results.
- 10 routes retained their `unsupported_pre_execution` status.
- One Protobom route retained its `execution_failure` status.

The 11 routes without completed conversions supplied no comparison pairs.
They were not classified as kernel failures.

## Eligibility and Direct Comparisons

Across the 19 evaluated routes:

| Measure                                          |     Count |
| ------------------------------------------------ | --------: |
| Eligible source occurrences                      |     8,386 |
| Eligible target occurrences                      |     8,409 |
| Missing source occurrences                       |         0 |
| Missing target occurrences                       |         9 |
| Excluded malformed or multiple-value occurrences |         0 |
| Eligible source-target pairs                     | 7,265,755 |
| Pairs with two observed values                   | 7,261,562 |
| Hash-authorized source-target pairs              |     3,983 |
| Direct agreements under DISTINCT                 |     9,856 |
| Direct agreements under SHARED                   |     9,856 |
| Expected changed direct agreements               |         0 |
| Actual changed direct agreements                 |         0 |
| Changed hash-authorized agreements               |         0 |
| Unexpected direct outcomes                       |         0 |

These totals count occurrences and pairs across routes.
They are not counts of unique packages or independent experimental trials.

The direct agreement counts were recomputed from the
prepared canonical PURL values, outside the runner, and
matched the result on every evaluated route.
This checks the runner, not the preparation that produced the prepared values.

Of the 7,265,755 eligible source–target pairs,
4,193 contained a missing target value.
This equals the sum of source occurrences on the nine routes
with one missing target:
4,189 CycloneDX-source occurrences
plus four SPDX-source occurrences.

The remaining 7,261,562 pairs contained two observed values.
No pair contained a missing source value.

## Per-Route Results

The table abbreviates `gen-cyclonedx-` as `cdx-` and `gen-spdx-` as `spdx-`.
Source identifiers otherwise retain their recorded suffixes.

Every listed route had zero missing source occurrences, zero exclusions,
and zero changed direct agreements.
The agreement column is the count under each policy.

| Source            | Converter | Eligible sources | Eligible targets | Missing targets | Authorized pairs | Agreements per policy |
| ----------------- | --------- | ---------------: | ---------------: | --------------: | ---------------: | --------------------: |
| cdx-9dcf635da297  | syft      |                3 |                5 |               1 |                0 |                     3 |
| cdx-9dcf635da297  | cdx2spdx  |                3 |                4 |               0 |                3 |                     3 |
| cdx-001a52237a69  | syft      |              201 |              203 |               1 |                0 |                   201 |
| cdx-001a52237a69  | cdx2spdx  |              201 |              202 |               0 |              201 |                   201 |
| cdx-9179c4025ab4  | syft      |              201 |              203 |               1 |                0 |                   201 |
| cdx-9179c4025ab4  | cdx2spdx  |              201 |              202 |               0 |              201 |                   201 |
| cdx-f1c2f23c4645  | syft      |              840 |              842 |               1 |                0 |                   840 |
| cdx-f1c2f23c4645  | cdx2spdx  |              840 |              841 |               0 |              840 |                   840 |
| cdx-0fc86e0249ef  | syft      |            1,115 |            1,117 |               1 |                0 |                 1,851 |
| cdx-0fc86e0249ef  | cdx2spdx  |            1,115 |            1,116 |               0 |              926 |                 1,851 |
| cdx-2e4891eb0992  | syft      |               43 |               45 |               1 |                0 |                    43 |
| cdx-2e4891eb0992  | cdx2spdx  |               43 |               44 |               0 |               43 |                    43 |
| cdx-445136956fe1  | syft      |              903 |              905 |               1 |                0 |                   903 |
| cdx-445136956fe1  | cdx2spdx  |              903 |              904 |               0 |              903 |                   903 |
| cdx-a2e17be40185  | syft      |              883 |              885 |               1 |                0 |                   883 |
| cdx-a2e17be40185  | cdx2spdx  |              883 |              884 |               0 |              865 |                   883 |
| spdx-e38ee905f9c0 | syft      |                4 |                4 |               1 |                0 |                     3 |
| spdx-0d278129197b | syft      |                2 |                2 |               0 |                0 |                     2 |
| spdx-0d278129197b | protobom  |                2 |                1 |               0 |                1 |                     1 |

Direct agreement is equality of canonical-PURL probe outputs across
the full eligible source-target product.
It does not authorize correspondence.

Repeated PURL values can produce multiple agreeing pairs for one occurrence.
This explains why agreement counts can exceed source occurrence counts.

In particular, the Syft agreement counts do not replace its Freeze 02
UNANCHORABLE verdicts.
The independent hash rule authorized no Syft pairs.

## Missing-Value Policy Results

For each evaluated route, the independent count check was:

`missing source occurrences x missing target occurrences = 0`

The actual changed-agreement count was also zero on every route.
All 19 product checks passed.
No changed-pair witnesses exist because no direct agreement changed.

Missing canonical PURL values occurred only on the target side:
one occurrence on each of nine Syft routes.
Those routes had no hash-authorized source–target pairs.

No source–target pair contained two missing values.

The result classified the two-missing prediction as `unevaluable`
on all 19 routes.

The observed-value control was classified as `met` on all 19 routes.
None of the 7,261,562 source-target pairs with two observed values
changed agreement between policies.

## Generated Identifications

The runner compared 3,343,902 unordered pairs of distinct observed
PURL values, summed across routes.

- Identifications gained under SHARED: 0.
- Identifications lost under SHARED: 0.
- Changed observed-value identification witnesses: none.

These comparisons concern relations on probe outputs.
They are distinct from the direct source-target occurrence comparisons.

The routes containing missing targets had no hash-authorized pairs.
Their missing target frames remained singleton classes in the frame regime.
The observed-value generated-identification results matched the
pre-freeze expectation of no change.

## Hypothesis Assessment

| L4 clause or control                                  | Result                       | Basis                                            |
| ----------------------------------------------------- | ---------------------------- | ------------------------------------------------ |
| Two-missing direct agreement changes under SHARED     | Unevaluable on all 19 routes | No eligible two-missing source-target pairs      |
| Observed-value direct agreement is unchanged          | Met on all 19 routes         | Zero changes among eligible observed-value pairs |
| Changed direct counts equal the missing-count product | Met on all 19 routes         | Expected and actual counts were both zero        |
| Generated observed-value identifications change       | No changes observed          | Zero gained or lost identifications              |

No direct-policy outcome contradicted the recorded expectations.

The synthetic checks exercised policy-sensitive cases before the freeze.
Their outcomes remain engineering-validation evidence and do not supply
missing cases for the formal dataset.

## Interpretation

The formal computation reproduced the behavior predicted from preparation
counts inspected before Freeze 03.

The L4 hypothesis predates the Freeze 02 execution.
The probe, pair population, and procedure were completed after the baseline
results and the preparation counts were known.
The formal run therefore confirmed expectations that were already
known from preparation.

This dataset exercises the observed-value control but does not exercise
the two-missing source-target condition that distinguishes the policies.
The absence of changes therefore does not establish that the policies
are equivalent in general.

The comparison documents the applicability limit of the selected
missing-value test on these preserved SBOM records.
It does not increase independently authorized correspondence coverage,
change the Freeze 02 preservation verdicts, or establish IdentityOps
language utility.

L1-L3 remain assigned to the separately planned Freeze 04 language study.
No Freeze 04 result is claimed in this report.
