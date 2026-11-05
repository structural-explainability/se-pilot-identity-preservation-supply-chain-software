# Freeze 02 Post-Experiment Notes

## Conversion Outcomes

30 source–converter routes were declared:

- 20 were planned for execution.
- 10 were declared unsupported before execution:
  - 8 Protobom routes were outside the declared input-version support.
  - 2 cdx2spdx routes were outside its supported conversion direction.
  - See: [05-transformations.toml](./05-transformations.toml)

Of the 20 attempted routes:

- 19 completed conversion, passed target validation, and completed evaluation.
- See: [run.json](./results/run.json)

1 failed conversion:

- Protobom on `gen-spdx-e38ee905f9c0`.
- The converter reported:
  `unable to serialize multiroot (2) cyclonedx, (mod.CYCLONEDX_MULTIROOT_HEADLESS disabled)`.
- The source lists two described elements in `documentDescribes`: a package and a file.
- The declared command passes no option to change this.
- It exited with code 1; it did not time out.
- Target validation and preservation evaluation were not attempted.
- See: [transform.log](./results/gen-spdx-e38ee905f9c0/protobom/transform.log)
- See: [execution.json](./results/gen-spdx-e38ee905f9c0/protobom/execution.json)

## Preservation Results by Tool

These counts are component evaluation records across routes,
not counts of unique packages.

| Tool      | Evaluation records | PRESERVED | UNANCHORABLE |
| --------- | -----------------: | --------: | -----------: |
| cdx2spdx  |              4,189 |     3,982 |          207 |
| Syft      |              4,195 |         0 |        4,195 |
| Protobom  |                  2 |         1 |            1 |
| **Total** |          **8,386** | **3,983** |    **4,403** |

No preservation-violation verdicts were reported.
Every verdict was PRESERVED or UNANCHORABLE.
These evaluator verdicts have zero records:

- VIOLATED_DROPPED
- VIOLATED_RELOCATED
- VIOLATED_ALTERED
- UNDERDETERMINED
- UNSUPPORTED
- NOT_APPLICABLE

UNSUPPORTED here is an evaluator verdict,
not the 10 routes declared unsupported before execution.
The rediscovered, new candidate, new confirmed and false positive counts
are all zero.

### cdx2spdx

Across eight held-out CycloneDX sources, 3,982 of 4,189 evaluation
records had an independently anchored target and a preserved PURL.

That is approximately 95% anchoring coverage for these routes.
All anchored observations were classified PRESERVED;
the remaining 207 were UNANCHORABLE.

This provides the largest body of assessable preservation results in this run.
See, for the route examined in detail:
[evaluation.json](./results/gen-cyclonedx-0fc86e0249ef/cdx2spdx/evaluation.json)

### Syft

All ten conversions completed and produced targets classified as valid.

All 4,195 preservation evaluation records were UNANCHORABLE.
The frozen method therefore provided no PURL-preservation determination
for these observations.

Two Syft targets have been inspected so far.
In `gen-cyclonedx-0fc86e0249ef`, the SPDX target has no checksums on any of its 1,117 packages.
Its source had a SHA-512 hash on all 1,115 components.
In `gen-spdx-0d278129197b`, the CycloneDX target has no hash on tools-java.
It carries the xlsx hash only in `externalReferences`, not in component `hashes`.
The other Syft targets have not been inspected.
These results do not establish that content-hash anchoring is impossible for Syft output generally.
See:
[gen-cyclonedx-0fc86e0249ef source](./sources/gen-cyclonedx-0fc86e0249ef.cdx.json),
[its Syft target](./results/gen-cyclonedx-0fc86e0249ef/syft/target.spdx.json),
[gen-spdx-0d278129197b source](./sources/gen-spdx-0d278129197b.spdx.json),
[its Syft target](./results/gen-spdx-0d278129197b/syft/target.cdx.json), and
[its Syft evaluation.json](./results/gen-spdx-0d278129197b/syft/evaluation.json)

### Protobom

One conversion completed and one failed.

The completed route (`gen-spdx-0d278129197b`) produced two evaluation records:
one PRESERVED and one UNANCHORABLE.
The UNANCHORABLE record is tools-java.
Protobom placed it in `metadata.component`, with its PURL and SHA-1 intact.
The frozen CycloneDX adapter does not evaluate `metadata.component`,
as Freeze 02 discloses.
No target component was found to anchor against.
See:
[target.cdx.json](./results/gen-spdx-0d278129197b/protobom/target.cdx.json),
[evaluation.json](./results/gen-spdx-0d278129197b/protobom/evaluation.json), and
[Freeze 02](../contracts/FREEZE_02_GENERALIZATION.md)

This is too little evidence for a broad conclusion about the converter.

## Reasons for UNANCHORABLE Results

- 4,177: no target component shared a declared content-hash anchor.
- 189: content-hash anchors resolved to multiple target components.
- 37: the source component had no usable content-hash anchor.

`No usable anchor` does not mean that no hash appeared
anywhere in the document.

The 189 ambiguous matches occurred on the cdx2spdx route for
`gen-cyclonedx-0fc86e0249ef`.
That route had 1,115 evaluation records, and 189 is 17.0% of them.
It was the only UNANCHORABLE reason on that route.
Under the frozen matching rule,
189 observations in this document matched multiple target components.
Whether that pattern generalizes to other documents
with nested npm packages remains open.
See:
[evaluation.json](./results/gen-cyclonedx-0fc86e0249ef/cdx2spdx/evaluation.json)

## UNANCHORABLE Count and Fraction by Route

Each cell gives `UNANCHORABLE / evaluation records`
and the corresponding percentage for one source–converter route.

| Source                       |             cdx2spdx |                   Syft |          Protobom |
| ---------------------------- | -------------------: | ---------------------: | ----------------: |
| `gen-cyclonedx-9dcf635da297` |             0/3 (0%) |             3/3 (100%) |       Unsupported |
| `gen-cyclonedx-001a52237a69` |           0/201 (0%) |         201/201 (100%) |       Unsupported |
| `gen-cyclonedx-9179c4025ab4` |           0/201 (0%) |         201/201 (100%) |       Unsupported |
| `gen-cyclonedx-f1c2f23c4645` |           0/840 (0%) |         840/840 (100%) |       Unsupported |
| `gen-cyclonedx-0fc86e0249ef` |    189/1,115 (17.0%) |     1,115/1,115 (100%) |       Unsupported |
| `gen-cyclonedx-2e4891eb0992` |            0/43 (0%) |           43/43 (100%) |       Unsupported |
| `gen-cyclonedx-445136956fe1` |           0/903 (0%) |         903/903 (100%) |       Unsupported |
| `gen-cyclonedx-a2e17be40185` |        18/883 (2.0%) |         883/883 (100%) |       Unsupported |
| `gen-spdx-e38ee905f9c0`      |          Unsupported |             4/4 (100%) | Conversion failed |
| `gen-spdx-0d278129197b`      |          Unsupported |             2/2 (100%) |         1/2 (50%) |
| **All evaluated routes**     | **207/4,189 (4.9%)** | **4,195/4,195 (100%)** |     **1/2 (50%)** |

Unsupported means the route was declared `unsupported_pre_execution`.
Those ten routes and the one failed conversion produced no evaluation records,
so their UNANCHORABLE fractions are undefined.

## SPDX-to-CycloneDX Coverage

The two SPDX sources contained six source PURL observations.
See:
[gen-spdx-e38ee905f9c0](./sources/gen-spdx-e38ee905f9c0.spdx.json) and
[gen-spdx-0d278129197b](./sources/gen-spdx-0d278129197b.spdx.json)

- Syft evaluated all six, but every result was UNANCHORABLE.
- Protobom evaluated two: one PRESERVED and one UNANCHORABLE.
- Protobom failed conversion on the other source, which contained four
  source PURL observations.

One SPDX-to-CycloneDX observation received a definitive
preservation verdict in this run.
See:
[Syft, gen-spdx-e38ee905f9c0](./results/gen-spdx-e38ee905f9c0/syft/evaluation.json),
[Syft, gen-spdx-0d278129197b](./results/gen-spdx-0d278129197b/syft/evaluation.json), and
[Protobom, gen-spdx-0d278129197b](./results/gen-spdx-0d278129197b/protobom/evaluation.json)

## Interpretation

- The formal experiment ran.
- Execution evidence was preserved under `generalization/results/`.
- The evaluator reported 3,983 PRESERVED observations overall.
- No dropped, relocated, or altered PURL violations were reported.
- The 4,403 UNANCHORABLE results limit what can be concluded.
  They are explicit limitation outcomes, not preservation successes
  or preservation violations.
- No preservation-violation verdicts currently require adjudication.
- The Protobom execution failure remains a recorded outcome.
  No retry is authorized under Freeze 02.
  Any rerun with a changed configuration requires a new freeze.

## Remaining Work

- Inspect the source and target hash representations for Syft routes
  to explain the missing matches.
  Inspected so far: `gen-cyclonedx-0fc86e0249ef` and `gen-spdx-0d278129197b`.
  Not yet inspected: the other 7 Syft CycloneDX-to-SPDX routes and `gen-spdx-e38ee905f9c0`.
- Tabulate the three UNANCHORABLE reasons by converter.
- Compare the outcomes with the baseline predictions in `generalization/PREDICTIONS.md`.
- Run `verify_06_freeze_02` and confirm Freeze 02 still verifies after the run.
- Preserve the original verdicts and evidence during that analysis.
