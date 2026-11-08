# Freeze 04 Specification

## Status

This file is in the Freeze 04 inventory.
It is frozen once the Freeze 04 record is established.

The record path is `contracts/FREEZE_04_IDENTITYOPS_COMPARISON.md`.

The operation-to-language decisions are in
[freeze_04_operation_mapping.md](./freeze_04_operation_mapping.md).
This file records the encoding, schemas, controls, commands,
and reporting rules that implement them.

## Question

Under two anchor-algorithm policies, does IdentityOps v0.1.0
add capability beyond a Python reference implementation
for the correspondence operations in the mapping?

The study compares two implementations of one rule.
It does not test whether either policy is correct.

This study does not evaluate hypotheses L1–L3 recorded in
`generalization/PREDICTIONS.md`.
Those hypotheses concern canonical-PURL agreement,
relocation probes, and evidence accounting.
Freeze 04 instead evaluates the correspondence
operations and implementation boundaries specified here.
No conclusions about L1-L3 are drawn from this comparison.

## Pinned Inputs

- Baseline evidence commit: `e1befa159faff965b32a47975ac355bb6a9ccb18`
- Prepared input: `comparison/prepared/freeze_02.json`
- Prepared input SHA-256: `17eaa9518e1754a860319532d8e66a317978d3a41fb711a8e47318c23f7699f7`
- IdentityOps commit: `7060cd084801e72f2c31175afef035d057979e8a`

The prepared input is the Freeze 03 output.
Both arms read it and refuse to run on any other digest.

## Policies

A policy is the set of admitted anchor algorithms.
Algorithm labels are matched as spelled in the prepared input.

| Policy       | Admitted algorithm labels                                                   |
| ------------ | --------------------------------------------------------------------------- |
| `baseline`   | MD5, SHA-1, SHA-256, SHA-384, SHA384, SHA-512, SHA3-256, SHA3-384, SHA3-512 |
| `restricted` | SHA-256, SHA-384, SHA-512                                                   |

Sources spell SHA-384 as `SHA-384` and targets spell it `SHA384`.
Both arms keep these as distinct matching keys.
In the prepared input, no source-target pair can match through either label under either policy.

## Classification Rule

For each source occurrence of each completed route, under each policy:

1. Take the source anchors whose algorithm is admitted.
2. Find target occurrences of the same route sharing an admitted anchor.
   Sharing means equal algorithm label and equal value.
3. Take the distinct targets reached through any admitted anchor.
4. Classify the source.

| Class                | Condition                                               |
| -------------------- | ------------------------------------------------------- |
| `no_source_anchor`   | No source anchor has an admitted algorithm              |
| `no_matching_target` | An admitted anchor exists and no target shares one      |
| `authorized`         | Exactly one distinct target shares an admitted anchor   |
| `ambiguous`          | More than one distinct target shares an admitted anchor |

Routes without a completed conversion have no classifications.

## Encoding

The IdentityOps arm uses encoding E3 from the mapping.

The adapter writes `comparison/results/freeze_04/anchors.csv`.
It has one row per occurrence, source and target, of the completed routes.
It has one column per anchor algorithm label.

| Column           | Content                                                            |
| ---------------- | ------------------------------------------------------------------ |
| `frame`          | Row identifier `f000001`, `f000002`, and so on, in route order     |
| `route_id`       | Route identifier                                                   |
| `side`           | `source` or `target`                                               |
| `pointer`        | JSON Pointer of the occurrence                                     |
| `anchor_<LABEL>` | `route_id`, a vertical bar, and the anchor value. Empty if absent. |

The route identifier prefix in each value confines every relation to one route.
Route isolation is therefore carried by the adapter's value encoding.
No IdentityOps program expresses it.

Each IdentityOps program declares one regime per admitted algorithm label.
Each regime relates occurrences sharing a value in one column.
Each program also declares one coverage check per regime.

The adapter combines, per source occurrence:

- the targets related to it by each declared regime,
- the algorithm labels behind each candidate,
- the candidate count, and
- the exactly-one test.

The pinned language has no construct for these four steps.

## Implementations

| Path                                  | Role                                              |
| ------------------------------------- | ------------------------------------------------- |
| `comparison/freeze_04_reference.py`   | Python reference arm, standard library only       |
| `comparison/freeze_04_identityops.py` | Table adapter, IdentityOps runner, and classifier |
| `comparison/freeze_04_baseline.ido`   | IdentityOps program for the baseline policy       |
| `comparison/freeze_04_restricted.ido` | IdentityOps program for the restricted policy     |
| `comparison/freeze_04_compare.py`     | Arm comparison and transition record              |
| `comparison/freeze_04_control.py`     | Freeze check, establish, and verify               |
| `freeze_04.ps1`                       | PowerShell entry point                            |

Each arm records the SHA-256 of its own script in its output.
The IdentityOps arm also records the SHA-256 of both programs
and of the anchor table.
Each program pins the SHA-256 of the anchor table.
IdentityOps stops the run if the table differs from the pin.

## Output Schemas

All outputs are in `comparison/results/freeze_04/`.
Each JSON file is written once and refuses to overwrite an existing file.

### Per-Policy Record

The reference and IdentityOps arms use the same record for each source occurrence.

| Field                 | Content                                                              |
| --------------------- | -------------------------------------------------------------------- |
| `admitted_algorithms` | Source algorithm labels admitted by the policy, sorted               |
| `excluded_algorithms` | Source algorithm labels the policy does not admit, sorted            |
| `candidates`          | Target pointers sharing an admitted anchor, with `shared_algorithms` |
| `classification`      | One of the four classes                                              |

Candidates are listed in target order for the reference arm
and in frame order for the IdentityOps arm.
Frames follow target order within a route, so the lists are comparable.

### `reference.json` and `identityops.json`

Top level:
`schema_version`, `arm`, `evidence_commit`, `prepared_input`, `prepared_sha256`,
`script_sha256`, and `routes`.

The reference arm adds `policies` and `totals`.
The IdentityOps arm adds `identityops_commit`, `table`, `programs`,
and `identityops_results`.
`identityops_results` holds the IdentityOps check outputs for each policy.

Each route has `route_id`, `status`, and `analysis_status`.
An evaluated route also has `counts` per policy and `records`.
An evaluated reference route also has `agreement_with_prepared_baseline`.
Each record has `pointer`, `baseline`, and `restricted`.

### `transitions.json`

Top level:
`schema_version`, `script_sha256`, `inputs`, `arms`, `causes`,
`ambiguity_persistence`, `routes`, `agreement`, and `occurrences`.

- `inputs` gives the path and SHA-256 of both arm outputs.
- `arms` gives, per arm, the baseline-to-restricted class matrix,
  the occurrence count, and the number of changed occurrences.
- `causes` gives, per arm, the changed occurrences grouped by transition
  and by the algorithm labels admitted under baseline and not under restricted.
- `ambiguity_persistence` gives, per arm, how many occurrences are ambiguous
  under both policies and how many keep the same candidate set.
- `routes` gives the class matrix per route and arm.
- `agreement` gives the arm-to-arm differences in classification,
  candidates, and algorithm lists, and up to 20 examples.
- `occurrences` lists every source occurrence with its baseline and restricted
  classes in each arm.

## Validation Controls

The three scripts with a `--self-test` run it before the freeze and create no output.
The control script's `--check` creates no output either.

| Control                              | Script      | Checks                                                                       |
| ------------------------------------ | ----------- | ---------------------------------------------------------------------------- |
| Synthetic cases                      | reference   | Every class, route isolation, policy-sensitive anchors, SHA-384 spelling     |
| Agreement with the prepared baseline | reference   | Baseline status and candidates equal the Freeze 02 evaluator for all sources |
| Synthetic cases                      | IdentityOps | The same cases through the programs, the adapter, and the classifier         |
| Table digest pins                    | IdentityOps | Both programs pin the digest of the table built from the prepared input      |
| Regime consistency                   | IdentityOps | Each program declares the regimes the adapter combines                       |
| Synthetic transitions                | compare     | Matrices, causes, ambiguity persistence, and disagreement detection          |
| Input pins and ancestry              | control     | Evidence commit, input digest, IdentityOps commit, ancestry, inventory       |

The synthetic input has eight sources in one route and one source in a second.
It covers:

- one authorized source,
- one source with no matching target,
- one ambiguous source,
- one source with no anchor,
- one source whose only anchor is SHA-1,
- one source with SHA-1 and SHA-256 anchors, ambiguous under baseline and authorized under restricted,
- one source whose SHA-384 anchor meets a SHA384 target, and
- one source whose SHA-384 anchor meets a SHA-384 target.

## Chronology and Development Observations

These were examined before the freeze.
They come from development runs of both arms on the pinned prepared input.

- Baseline counts, from Freeze 03:
  authorized 3,983, ambiguous 189, no matching target 4,177, no source anchor 37.
- Restricted counts:
  authorized 2,858, ambiguous 189, no matching target 3,050, no source anchor 2,289.
- The two arms agreed on all 8,386 source occurrences under both policies.
- The reference arm agreed with the prepared Freeze 02 evaluator
  on status and candidates for all 8,386 sources.
- 2,252 occurrences changed class.
  All 2,252 have SHA-1 as the algorithm admitted under baseline and not under restricted.
- All 189 occurrences ambiguous under baseline remain ambiguous
  with the same candidates under restricted.
- Each arm ran in under two seconds on the prepared input.
- The anchor table SHA-256 is `00897db38b7c3f5c1b27b1a54cae990a9d894ff36a7434a623f0f5fcc4bca3b3`.

The formal run therefore tests reproducibility under the frozen apparatus.
It does not test an outcome unknown to the author.

## Decision Ledger

The report states where each policy decision is held in each arm.

| Decision                             | Reference arm                    | IdentityOps arm                                                  |
| ------------------------------------ | -------------------------------- | ---------------------------------------------------------------- |
| Baseline admits all labels           | Code, `is_admitted`              | Program, nine regime declarations, and script, `POLICY_REGIMES`  |
| Restricted admits three labels       | Code, `RESTRICTED_ALGORITHMS`    | Program, three regime declarations, and script, `POLICY_REGIMES` |
| Spelling kept distinct               | Code, labels compared as spelled | Program, separate regimes and columns                            |
| Equal value within one algorithm     | Code, dictionary equality        | Language, regime equality on one column                          |
| Empty value joins no class           | Not applicable                   | Language semantics                                               |
| Confinement to one route             | Code, per-route index            | Adapter, route prefix in each value                              |
| Union of targets across anchors      | Code                             | Script                                                           |
| Candidate count and exactly-one rule | Code                             | Script                                                           |
| Anchor trace per candidate           | Code                             | Script                                                           |
| Per-occurrence class                 | Code                             | Script                                                           |
| Policy transition                    | Compare script                   | Compare script                                                   |

Each IdentityOps policy is held in two places, the program and `POLICY_REGIMES`.
The self-test checks that they agree.
No language construct checks it.

## Commands

Before the freeze:

```powershell
.\freeze_04.ps1 -Check
```

After the freeze record is established, reviewed, and committed:

```powershell
.\freeze_04.ps1 -Verify
uv run --frozen python comparison/freeze_04_reference.py --run
uv run --no-project comparison/freeze_04_identityops.py --run
uv run --frozen python comparison/freeze_04_compare.py --run
```

The comparison runs only after both arms have written their outputs.

Each run command refuses to overwrite an existing output.
A failed run is reported and is not repeated under this record.

## Reporting Rules

The report states:

- the counts per class and policy for each arm,
- the transition matrix and the number of changed occurrences,
- the algorithm labels behind each changed occurrence,
- whether the ambiguous occurrences are the same occurrences under both policies,
- every arm-to-arm difference, with its examples,
- the decision ledger as executed, and
- the IdentityOps coverage check results, stated as what they say about the table.

The report separates what IdentityOps computed
from what the adapter and Python computed.

## Permitted Conclusions

If the arms agree on every occurrence under both policies,
the report may state that IdentityOps v0.1.0 added little or no capability
for this operation set under encoding E3.
The report ties that statement to the table below.

| Step                                   | Computed by |
| -------------------------------------- | ----------- |
| Within-algorithm shared-value relation | IdentityOps |
| Combining relations across algorithms  | Python      |
| Candidate counting and exactly-one     | Python      |
| Anchor traces and classification       | Python      |

If the arms differ on any occurrence,
the report states the difference and its cause.
It makes no capability claim until the cause is identified.
A correction requires a new freeze.

If any control fails, no formal run is made.

The study makes no claim about:

- whether either anchor policy is correct,
- hash-algorithm strength or equivalence,
- identifiers beyond the 19 completed routes, or
- IdentityOps with a language extension.
