# Freeze 03 — Kernel Missing-Value Comparison

## Scope

This record freezes the L4 execution procedure using the interpretive kernel.

The design specifies the canonical-PURL probe, eligible occurrences,
source–target pairs, hash-authorized frame regime, both missing-value
policies, and reporting rules.

See [Kernel Missing-Value Comparison Design](../comparison/freeze_03_design.md).

## Chronology

The original L4 hypothesis predates the Freeze 02 baseline execution.

The operational design was completed after baseline inspection.
Real-evidence preparation counts were examined before this freeze.
Those counts and their implications are recorded in the frozen design.

At establishment, `comparison/prepared/` and `comparison/results/`
were absent. The frozen commands create the formal prepared artifact
and result file.

## Pinned Evidence and Kernel

- Baseline evidence commit: `e1befa159faff965b32a47975ac355bb6a9ccb18`
- Interpretive kernel commit: `e895ace0129e321eaf6912718c341ce3eb1644eb`

## Outputs and Report

- Prepared input: `comparison/prepared/freeze_02.json`
- Kernel result: `comparison/results/l4/run.json`
- Subsequent report: `comparison/REPORT_L4.md`

The inventory below covers the execution apparatus.
The generated outputs and subsequent report are preserved after execution.

## Verification

Verification checks every listed digest, the declared pins,
commit ancestry, and Freeze 02 integrity.
It permits comparison output directories after establishment.

```powershell
.\freeze_03.ps1 -Verify
```

The pre-execution content commit identifies the preparation state.
The protocol requires separate review and commitment of this record
before formal execution.
Record generation does not perform that commitment.

## Frozen Content Hashes

**Status:** FROZEN

**Frozen (UTC):** 2026-11-07T17:40:37.064630+00:00

**Frozen content commit:** `e43848ac8f27bd891c0d37bf01e9063c6f883db6`

- `d24b40cd125e2f6a600bad96059f963b5f442ca90008e7b2b09b5f979abfe187`  `comparison/freeze_03_control.py`
- `15d176c9849b5105e5996831c89dfc6706c5bda5d90083c444d360d2588ca914`  `comparison/freeze_03_design.md`
- `51b84018e95ff7bbc7a9ad10acf171ae91e4578c8986c4cdfbef4681380f4f27`  `comparison/freeze_03_prepare.py`
- `144b7ab334860bf6f8c2130d05b1acc2e76099a3197155e19ca5f66d2f7ed8cb`  `comparison/freeze_03_run_l4.py`
- `f932a5e93204cbe2d9179da50281168f972a43556b7936be24466dd5f64854fa`  `contracts/FREEZE_02_GENERALIZATION.md`
- `53e268d0aad90bafd38ffb166673aabb7486067360d85c8b1b64bb03a5c2507f`  `freeze_03.ps1`
