# Post Freeze 02 Comparisons

This directory contains studies using the preserved SBOM generalization evidence.

## Study Sequence

| Freeze | Study                           | Purpose                                                                                                      |
| ------ | ------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 01     | Commitment and evaluator        | Fix the preservation obligation and evaluation procedure.                                                    |
| 02     | Generalization baseline         | Execute the declared conversions and evaluate preservation under the frozen method.                          |
| 03     | Kernel missing-value comparison | Measure the effects of DISTINCT and SHARED on canonical-PURL probe agreements and generated identifications. |
| 04     | IdentityOps language comparison | Compare IdentityOps with a Python reference under two anchor-algorithm policies.                             |

Freeze 02 was executed and its results were committed.
The Freeze 03 design and implementation are available here.
The Freeze 04 apparatus is available here.

## Freeze 02 Baseline

- [Pre-execution predictions](../generalization/PREDICTIONS.md)
- [Freeze 02 record](../contracts/FREEZE_02_GENERALIZATION.md)
- [Formal execution record](../generalization/results/run.json)
- [Post-experiment notes](../generalization/FREEZE_02_POST_EXPERIMENT.md)

## Freeze 03. Kernel Missing-Value Comparison

The study implements hypothesis L4 with `se-interpretive-kernel`.

The preparation counts were examined before Freeze 03.
They showed zero missing source PURLs on all completed routes.
The design records that prior observation and the resulting expectations.

- [Design and commands](./freeze_03_design.md)
- [Preparation](./freeze_03_prepare.py)
- [L4 runner](./freeze_03_run_l4.py)
- [Freeze mechanism](./freeze_03_control.py)
- [PowerShell entry point](../freeze_03.ps1)

The freeze mechanism creates:
`contracts/FREEZE_03_KERNEL_MISSING_VALUES.md`

The formal commands create:

- `comparison/prepared/freeze_02.json`
- `comparison/results/l4/run.json`

The designated post-execution report is:
`comparison/REPORT_L4.md`

The report follows preservation of the formal execution evidence.

## Freeze 04. IdentityOps Comparison

The study compares a Python reference arm with an IdentityOps-assisted arm
under a baseline and a restricted anchor-algorithm policy.

The preparation counts and development runs were examined before Freeze 04.
The specification records that chronology.

- [Operation mapping](./freeze_04_operation_mapping.md)
- [Specification](./freeze_04_specification.md)
- [Reference arm](./freeze_04_reference.py)
- [IdentityOps arm](./freeze_04_identityops.py)
- [Baseline program](./freeze_04_baseline.ido)
- [Restricted program](./freeze_04_restricted.ido)
- [Arm comparison](./freeze_04_compare.py)
- [Freeze mechanism](./freeze_04_control.py)
- [PowerShell entry point](../freeze_04.ps1)
- [Original exploratory design](./freeze_04_design.md)

The freeze mechanism creates:
`contracts/FREEZE_04_IDENTITYOPS_COMPARISON.md`

The formal commands create:

- `comparison/results/freeze_04/reference.json`
- `comparison/results/freeze_04/anchors.csv`
- `comparison/results/freeze_04/identityops.json`
- `comparison/results/freeze_04/transitions.json`

The original L1–L4 predictions remain in their frozen historical record.
The follow-on designs identify which hypotheses each study addresses.

## Evidence Handling

The preparation command reads the pinned Freeze 02 evidence commit.
The comparison runner reads the prepared JSON.

Both formal commands refuse to overwrite their output files.

Freeze 03 records the design, implementation, wrapper, and Freeze 02 record.
Its verifier also invokes the Freeze 02 integrity verifier.

Freeze 04 records the mapping, specification, both arms, both programs,
the comparison, the wrapper, and the Freeze 02 and Freeze 03 records.
Its verifier also invokes the Freeze 02 integrity verifier.
