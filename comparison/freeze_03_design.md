# Kernel Missing-Value Comparison Design

## Status and Chronology

This design was prepared during 2026-11-05 through 2026-11-07.

The authoritative freeze record is
`contracts/FREEZE_03_KERNEL_MISSING_VALUES.md`.
Establishment of that record fixes the design and apparatus identified
by its artifact hashes.

Hypothesis L4 was recorded before the Freeze 02 experiment.
The operational design was completed after examination of the baseline
results and preparation counts.

Pre-freeze development checks passed for the synthetic cases.
Preparation of the committed baseline evidence in memory produced the
counts recorded below.

These preparation observations precede the formal kernel computation.
They are not results from formal execution of `comparison/freeze_03_run_l4.py --run`.

Formal execution evidence is recorded separately in
`comparison/results/l4/run.json`.
The designated analysis report is `comparison/REPORT_L4.md`.

## Scope

Freeze 03 fixes the execution procedure for hypothesis L4 using the
interpretive kernel.

The study compares DISTINCT and SHARED missing-value policies on one
canonical-PURL probe. Both policies receive the same eligible occurrences
and frame regime.

L1–L3 are assigned to the separately planned
[IdentityOps language comparison](./freeze_04_design.md).

Exploration of CycloneDX `metadata.component` and alternative hash
locations is outside this study's scope.

The original hypotheses remain preserved in
[generalization/PREDICTIONS.md](../generalization/PREDICTIONS.md).

## Pinned Evidence and Implementation

- Pilot commit at the start of the baseline run:
  `9baa72323301e287a4f3c821cb638f5165b3a29a`.
- Pilot commit containing the committed baseline evidence:
  `e1befa159faff965b32a47975ac355bb6a9ccb18`.
- Interpretive kernel commit:
  `e895ace0129e321eaf6912718c341ce3eb1644eb`.

The baseline execution is recorded in
[generalization/results/run.json](../generalization/results/run.json).

The kernel dependency is declared in the inline script metadata in
[freeze_03_run_l4.py](./freeze_03_run_l4.py).

The pilot Python environment and evaluator dependencies are recorded
under Freeze 02.

## Research Question

For the declared canonical-PURL probe, how does changing missing-value
treatment from DISTINCT to SHARED affect:

- direct source–target probe agreement;
- the subset of changed agreements with hash-authorized correspondence; and
- generated identifications among observed PURL values?

Results are reported separately for each route.
Source–target pairs within a route are dependent observations.

## Preparation

`comparison/freeze_03_prepare.py` reads the pinned evidence commit using Git.

It verifies source and target SHA-256 digests against the recorded values.
It also checks the imported pilot adapter, evaluator, and normalization
module bytes against that commit.

For each completed conversion, preparation records:

- every source and target occurrence exposed by the frozen adapters;
- route, side, document path, and JSON Pointer;
- the component reference;
- normalized content-hash anchors;
- raw and normalized canonical-slot PURL values;
- probe status; and
- hash-based correspondence candidates and authorization.

Unsupported routes and conversion failures retain their route status.
They supply no completed source–target comparison for this study.

The frozen adapters expose SPDX package records and CycloneDX components,
including nested CycloneDX components.
Their scope excludes CycloneDX `metadata.component`.

## Correspondence Rule

Correspondence is derived using the frozen evaluator's `_anchor_index`
and `_anchored_targets`.

For each source occurrence, the candidate set contains the target
occurrences reached through its normalized content hashes.
Exactly one target occurrence authorizes a source–target pair.

The full target occurrence population participates in candidate derivation.
A malformed or multiple-PURL target can therefore contribute to ambiguity.
Probe eligibility is applied after correspondence derivation.

Correspondence is independent of the PURL being compared.
The implementation reuses the baseline matching rule; this study does
not independently validate that rule.

## Probe and Eligibility

PURL normalization uses `purl_canonical.canonical` from the frozen pilot.

Each occurrence receives one of the following probe statuses.

| Status    | Rule                                                                              |
| --------- | --------------------------------------------------------------------------------- |
| observed  | Exactly one distinct valid normalized PURL and no malformed canonical-slot value. |
| missing   | The canonical PURL field or matching reference is absent.                         |
| malformed | At least one present canonical-slot value fails normalization.                    |
| multiple  | More than one distinct valid normalized PURL, with no malformed value.            |

A present empty string, JSON null, or PURL reference without its locator
is malformed under this preparation rule.

Repeated raw references that normalize to one valid PURL supply one
canonical value. Their raw occurrences remain recorded.

Preparation records malformed and multiple-value flags separately.
Its primary status gives malformed values precedence.

The scalar probe includes observed and missing occurrences.
Malformed and multiple occurrences are excluded; their counts are
reported by route and side.

## Direct Comparisons

Within each completed route, the comparison includes every eligible
source occurrence paired with every eligible target occurrence.
Each source–target pair occurs once.
The pair population is identical under both policies.

Direct agreement is equality of the outputs returned by the pinned
kernel loader:

- DISTINCT assigns each missing cell a separate output.
- SHARED assigns missing cells within the probe one shared output.

Hash authorization is recorded separately for changed pairs.
Agreement between missing values supplies no independent evidence
of source–target correspondence.

The route-level results contain:

- eligible source and target counts;
- excluded counts by side and reason;
- missing source and target counts;
- total eligible source–target pairs;
- direct agreements under each policy;
- changed direct agreements;
- changed agreements with hash authorization;
- pairs with two observed values;
- changes among those observed-value pairs; and
- witnesses for changes and unexpected outcomes.

## Independent Count Check

For this single probe, the predicted number of changed direct comparisons is:

`missing source cells x missing target cells`

A two-missing pair is predicted to disagree under DISTINCT and agree
under SHARED.

A pair of observed values is predicted to retain the same agreement
outcome under both policies.

The two-missing prediction is classified as unevaluable for any route
with zero two-missing pairs.
The observed-value control is assessed separately wherever eligible
observed-value pairs exist.

Contrary outcomes remain part of the result record.

## Frame Regime and Generated Identifications

Each eligible occurrence is a frame identified by side and JSON Pointer
within its route.

The frame partition starts with a singleton class for every eligible frame.
Each hash-authorized source–target pair with two eligible endpoints
contributes a join.
The frame regime is the equivalence closure of those joins.

The same frame partition and canonical-PURL probe are used under both policies.

The kernel's generated relation acts on probe outputs.
Its blocks are recorded under both policies, including the originating
frame locations of missing outputs.

Generated identifications are compared on pairs of distinct observed
PURL values present under both policies.
The results contain gained and lost identification counts and a witness
when an identification changes.

Direct source–target agreement counts and generated output-identification
counts use different carriers and are reported separately.

## Preparation Observations Before Freeze 03

The development preparation examined all 19 completed routes in memory.
It produced the following source-side correspondence counts.

| Correspondence status | Source occurrences across routes |
| --------------------- | -------------------------------: |
| authorized            |                            3,983 |
| ambiguous             |                              189 |
| no_matching_target    |                            4,177 |
| no_source_anchor      |                               37 |
| **Total**             |                        **8,386** |

Every source occurrence was classified as observed.
There were zero missing, malformed, or multiple-PURL source occurrences.

Nine Syft routes each had one missing target occurrence.
The Syft route `gen-spdx-0d278129197b--syft` had zero missing target occurrences.
The cdx2spdx and completed Protobom routes had zero missing target occurrences.

The two-missing pair count was therefore zero on every completed route.

These preparation observations imply the following expectations for formal
execution:

- zero changed direct agreements;
- an unchanged observed-value control; and
- zero changes among generated observed-PURL identifications.

The routes with missing targets have zero hash-authorized pairs.
Their missing target frames remain singleton classes in the frame partition.

These expectations were derived before Freeze 03 from inspected preparation
results. Formal execution records the kernel computation under the frozen
procedure; it does not constitute an unanticipated test of those counts.

## Synthetic Checks

The preparation self-test checks occurrence identity, nested traversal,
malformed and multiple PURLs, and matching before probe exclusion.
It then prepares the pinned baseline evidence in memory and prints
correspondence and probe-status counts.

The L4 runner self-test uses synthetic records.
It checks six changed direct agreements, one hash-authorized changed pair,
an unchanged observed-value control, one gained generated identification,
and the zero-two-missing-pair case.

Successful synthetic checks establish behavior on the declared control
cases. They are separate from the formal baseline comparison.

## Development Environment and Checks

The following commands specify the comparison development setup and checks.
Their working directory is the repository root.

```powershell
uv sync --locked
if ($LASTEXITCODE -ne 0) { throw "Locked environment synchronization failed." }

uv pip install --python .\.venv\Scripts\python.exe -r .\comparison\freeze_03_run_l4.py
if ($LASTEXITCODE -ne 0) { throw "Comparison dependency setup failed." }

uv run --frozen ruff check comparison
if ($LASTEXITCODE -ne 0) { throw "Comparison lint checks failed." }

uv run --frozen ty check comparison
if ($LASTEXITCODE -ne 0) { throw "Comparison type checks failed." }

.\freeze_03.ps1 -Check
```

Dependency installation reads the kernel pin from `freeze_03_run_l4.py`.
It makes that dependency available to the pilot environment's editor
and type checker after synchronization.

The formal L4 command uses the script's inline dependency declaration.

The `-Check` operation runs both self-tests and verifies establishment
prerequisites apart from the clean-tree requirement.
It creates no formal comparison artifacts.

## Freeze 03 Inventory

The freeze mechanism hashes these files:

- `comparison/freeze_03_design.md`
- `comparison/freeze_03_prepare.py`
- `comparison/freeze_03_run_l4.py`
- `comparison/freeze_03_control.py`
- `freeze_03.ps1`
- `contracts/FREEZE_02_GENERALIZATION.md`

The Freeze 03 verifier also verifies Freeze 02.

The comparison index, planned Freeze 04 design, changelog, and post-run
report are outside the Freeze 03 inventory.

At establishment, `comparison/prepared/` and `comparison/results/`
must both be absent.
Verification permits those directories after establishment.

## Establishment Protocol

Establishment requires a clean, committed preparation state.
The preparation state includes the final design and implementation.
An empty `git status --short` output indicates the required clean tree.

The establishment command is:

```powershell
.\freeze_03.ps1 -Establish
```

The command generates and verifies:

`contracts/FREEZE_03_KERNEL_MISSING_VALUES.md`

The protocol requires review, commit, and push of that record before
formal preparation and execution.
Record generation does not itself perform those Git operations.

## Formal Execution Protocol

The following sequence specifies formal preparation, execution, and
the surrounding integrity checks from the repository root.

```powershell
& {
    $ErrorActionPreference = "Stop"

    .\freeze_03.ps1 -Verify

    uv run --frozen python comparison/freeze_03_prepare.py --prepare
    if ($LASTEXITCODE -ne 0) {
        throw "Comparison preparation failed."
    }

    .\freeze_03.ps1 -Verify

    uv run --no-project comparison/freeze_03_run_l4.py --run
    if ($LASTEXITCODE -ne 0) {
        throw "L4 execution failed."
    }

    .\freeze_03.ps1 -Verify
}
```

The runners enforce output-file non-overwrite checks.
The command sequence supplies the freeze-verification gates.

The prepared input is `comparison/prepared/freeze_02.json`.
The kernel result is `comparison/results/l4/run.json`.

## Evidence Preservation

The evidence-preservation commands are:

```powershell
git add -f -- comparison/prepared/ comparison/results/
git diff --cached --stat
git commit -m "Record Freeze 03 kernel comparison evidence"
git push origin main
```

A failed command requires preservation of any partial output and error
information. Another attempt requires review and explicit authorization;
failure does not authorize replacement of existing evidence.

## Reporting Requirements

The designated report is `comparison/REPORT_L4.md`.
It is prepared after preservation of the execution evidence and is outside
the frozen apparatus.

The report records:

- the preparation and result commits;
- the verified Freeze 03 digest;
- the prepared-input and runner digests recorded in the result;
- route eligibility and exclusions;
- direct counts under both policies;
- the product check and changed-pair witnesses;
- generated identification results;
- met, contradicted, and unevaluable clauses of L4; and
- the preparation observations known before Freeze 03.

## Interpretation Limits

The original missing-value hypothesis predates Freeze 02.
The selected probe, pair population, and operational procedure were completed
after baseline inspection.

The preparation counts predict zero direct changes on this dataset.
That chronology limits the interpretation of the formal computation.

The synthetic checks exercise policy-sensitive cases.
The formal study assesses whether those conditions occur in the selected
preserved documents and records the kernel's behavior on those inputs.
