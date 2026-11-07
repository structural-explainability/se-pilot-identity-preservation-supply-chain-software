# Kernel Missing-Value Comparison Design

## Status and Chronology

Prepared during 2026-11-05 through 2026-11-07.

This design becomes frozen when
`contracts/FREEZE_03_KERNEL_MISSING_VALUES.md`
is established and verified.

Hypothesis L4 was recorded before the Freeze 02 experiment.
The operational design below was completed after examining the baseline
results and the preparation counts.

The attached development record reports successful synthetic checks and
an in-memory preparation of the committed Freeze 02 evidence.
The preparation counts and their implications are recorded below.

Formal execution output will be preserved separately.
The results report will be `comparison/REPORT_L4.md`.

## Scope

Freeze 03 executes hypothesis L4 using the interpretive kernel.

It compares DISTINCT and SHARED missing-value policies on one canonical-PURL
probe, using the same eligible occurrences and frame regime under both policies.

L1–L3 are assigned to the planned
[IdentityOps language comparison](./IDENTITYOPS_COMPARISON_DESIGN.md).

The exploratory adapter-scope question concerning `metadata.component`
and alternative hash locations remains a separate future study.

The historical predictions are preserved in
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
[run_l4.py](./run_l4.py).

The pilot Python environment and evaluator dependencies are recorded
under Freeze 02.

## Question

For the declared canonical-PURL probe, how does changing missing-value
treatment from DISTINCT to SHARED affect:

- direct source–target probe agreement;
- the subset of changed agreements with hash-authorized correspondence; and
- generated identifications among observed PURL values?

Report each route separately.
Source–target pairs within a route are dependent observations.

## Preparation

`comparison/prepare.py` reads the pinned evidence commit using Git.

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

Use the frozen evaluator's `_anchor_index` and `_anchored_targets`.

For each source occurrence, gather the target occurrences reached through
its normalized content hashes.
Exactly one target occurrence authorizes a source–target pair.

Retain the full target occurrence population when deriving candidates.
A malformed or multiple-PURL target can therefore contribute to ambiguity.

Apply probe eligibility after deriving correspondence.

Correspondence is independent of the PURL being compared.
The implementation reuses the baseline matching rule, so this study
does not independently validate that rule.

## Probe and Eligibility

Use `purl_canonical.canonical` from the frozen pilot.

Each occurrence receives one of these probe statuses:

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

The preparation records malformed and multiple-value flags separately.
Its primary status gives malformed values precedence.

The scalar probe includes observed and missing occurrences.
Report excluded malformed and multiple occurrences by route and side.

## Direct Comparisons

Within each completed route, compare every eligible source occurrence
with every eligible target occurrence.

Include each source–target pair once.
Keep the same pair population under both policies.

For each policy, compare the outputs returned by the pinned kernel loader:

- DISTINCT assigns each missing cell a separate output.
- SHARED assigns missing cells within the probe one shared output.

Record independently whether each changed pair has hash authorization.

For each route, report:

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

For a two-missing pair, the prediction is disagreement under DISTINCT
and agreement under SHARED.

For two observed values, the prediction is unchanged agreement.

If a route has zero two-missing pairs, report the two-missing prediction
as unevaluable for that route.
Report the observed-value control separately wherever its eligible pairs exist.

Keep contrary outcomes in the result record.

## Frame Regime and Generated Identifications

Each eligible occurrence is a frame identified by side and JSON Pointer
within its route.

Start with a singleton class for every eligible frame.
Join the endpoints of each hash-authorized source–target pair whose
endpoints are both eligible for the probe.
Take the equivalence closure of those joins.

Use that same frame partition and the canonical-PURL probe under both policies.

The kernel's generated relation acts on probe outputs.
Record its blocks under both policies, including the originating frame
locations of missing outputs.

Compare generated identifications on pairs of distinct observed PURL values
present under both policies.
Report gained and lost identifications and retain a changed-pair witness.

Direct source–target agreement counts and generated output-identification
counts use different carriers and are reported separately.

## Known Preparation Results Before Freeze 03

The development preparation examined all 19 completed routes in memory.
Its recorded source-side correspondence counts were:

| Correspondence status | Source occurrences across routes |
| --------------------- | -------------------------------: |
| authorized            |                            3,983 |
| ambiguous             |                              189 |
| no_matching_target    |                            4,177 |
| no_source_anchor      |                               37 |
| **Total**             |                        **8,386** |

Every source occurrence was classified observed.
There were zero missing, malformed, or multiple-PURL source occurrences.

Nine Syft routes each had one missing target occurrence.
The Syft route `gen-spdx-0d278129197b--syft` had zero missing target occurrences.
The cdx2spdx and completed Protobom routes had zero missing target occurrences.

Consequently, the two-missing pair count is already known to be zero
on every completed route.

The observed-value control is expected to be met.
Zero changed direct agreements are expected.

Zero changes among generated observed-PURL identifications are expected.
The routes with missing targets have zero hash-authorized pairs.
Their missing target frames remain singleton classes in the frame partition.

These expectations follow from preparation results inspected before Freeze 03.
The formal execution records the kernel computation under the frozen procedure.

## Synthetic Checks

The preparation self-test checks occurrence identity, nested traversal,
malformed and multiple PURLs, and matching before probe exclusion.
In the current preparation implementation, it then prepares the real pinned
evidence in memory and prints its counts.

The L4 runner self-test uses synthetic records.
It checks six changed direct agreements, one hash-authorized changed pair,
an unchanged observed-value control, one gained generated identification,
and the zero-two-missing-pair case.

Record the actual command output when performing the pre-freeze checks.

## Development Commands: Reproducible Setup

Run these commands from the repository root:

```powershell
uv sync --locked
if ($LASTEXITCODE -ne 0) { throw "Locked environment synchronization failed." }

uv pip install --python .\.venv\Scripts\python.exe -r .\comparison\run_l4.py
if ($LASTEXITCODE -ne 0) { throw "Comparison dependency setup failed." }

uv run --frozen ruff check comparison
if ($LASTEXITCODE -ne 0) { throw "Comparison lint checks failed." }

uv run --frozen ty check comparison
if ($LASTEXITCODE -ne 0) { throw "Comparison type checks failed." }

.\freeze_03.ps1 -Check
```

The dependency installation reads the kernel pin from `run_l4.py`.
It makes that dependency available to the pilot environment's editor
and type checker after synchronization.

The formal L4 command uses the script's inline dependency declaration.

## Freeze 03 Inventory

The freeze mechanism hashes:

- `comparison/KERNEL_MISSING_VALUES_DESIGN.md`
- `comparison/prepare.py`
- `comparison/run_l4.py`
- `comparison/freeze_comparison.py`
- `freeze_03.ps1`
- `contracts/FREEZE_02_GENERALIZATION.md`

The Freeze 03 verifier also verifies Freeze 02.

The index, planned Freeze 04 design, changelog, and post-run report remain
outside the Freeze 03 inventory.

At establishment, `comparison/prepared/` and `comparison/results/`
must both be absent.
Verification permits them afterward.

## Establishment and Execution

Run all commands from the repository root.

### 1. Check and commit the preparation state

Complete the development checks above.
Review, commit, and push the final design and implementation.
Confirm that `git status --short` produces no output.

### 2. Establish Freeze 03

```powershell
.\freeze_03.ps1 -Establish
```

Review the generated file:

`contracts/FREEZE_03_KERNEL_MISSING_VALUES.md`

Commit and push that record before executing the comparison.

### 3. Prepare and execute

```powershell
& {
    $ErrorActionPreference = "Stop"

    .\freeze_03.ps1 -Verify

    uv run --frozen python comparison/prepare.py --prepare
    if ($LASTEXITCODE -ne 0) {
        throw "Comparison preparation failed."
    }

    .\freeze_03.ps1 -Verify

    uv run --no-project comparison/run_l4.py --run
    if ($LASTEXITCODE -ne 0) {
        throw "L4 execution failed."
    }

    .\freeze_03.ps1 -Verify
}
```

The runners enforce output-file non-overwrite checks.
The commands above supply the freeze-verification gates.

### 4. Preserve the execution evidence

```powershell
git add -f -- comparison/prepared/ comparison/results/
git diff --cached --stat
git commit -m "Record Freeze 03 kernel comparison evidence"
git push origin main
```

Preserve any partial output and error information if a command fails.
Review the failure before authorizing another attempt.

### 5. Write the report

Write `comparison/REPORT_L4.md` after preserving the evidence.

Report:

- the preparation and result commits;
- the verified Freeze 03 digest;
- the prepared-input and runner digests recorded in the result;
- route eligibility and exclusions;
- direct counts under both policies;
- the product check and changed-pair witnesses;
- generated identification results;
- met, contradicted, and unevaluable clauses of L4; and
- what was known from preparation before Freeze 03.

## Interpretation Limits

The original missing-value hypothesis predates Freeze 02.
The selected probe, pair population, and operational procedure were completed
after baseline inspection.

The preparation counts already predict zero direct changes on this dataset.
Report that chronology when interpreting the formal computation.

The synthetic checks exercise policy-sensitive cases.
The formal study measures which of those conditions occur in the selected
preserved documents.
