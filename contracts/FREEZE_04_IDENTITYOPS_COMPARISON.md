# Freeze 04. IdentityOps Comparison

## Scope

This record freezes the IdentityOps comparison under two anchor-algorithm policies.

The mapping records the operation-to-language decisions.
The specification records the encoding, schemas, controls, commands,
and reporting rules.

See [Operation Mapping](../comparison/freeze_04_operation_mapping.md)
and [Specification](../comparison/freeze_04_specification.md).

## Chronology

The comparison design and both arms were developed after the Freeze 03 report.
Development runs of both arms on the prepared input preceded this freeze.
Their counts and their agreement are recorded in the specification.

At establishment, `comparison/results/freeze_04/` was absent.
The frozen commands create the formal outputs.

## Pinned Inputs and Implementations

- Baseline evidence commit: `e1befa159faff965b32a47975ac355bb6a9ccb18`
- Prepared input SHA-256: `17eaa9518e1754a860319532d8e66a317978d3a41fb711a8e47318c23f7699f7`
- IdentityOps commit: `7060cd084801e72f2c31175afef035d057979e8a`

## Outputs

- Reference arm: `comparison/results/freeze_04/reference.json`
- Anchor table: `comparison/results/freeze_04/anchors.csv`
- IdentityOps arm: `comparison/results/freeze_04/identityops.json`
- Transitions: `comparison/results/freeze_04/transitions.json`

The inventory below covers the execution apparatus.
The generated outputs are preserved after execution.

## Verification

Verification checks every listed digest, the declared pins,
the prepared input digest, commit ancestry, and Freeze 02 integrity.
It permits comparison outputs after establishment.

```powershell
.\freeze_04.ps1 -Verify
```

The pre-execution content commit identifies the preparation state.
The protocol requires separate review and commitment of this record
before formal execution.
Record generation does not perform that commitment.

## Frozen Content Hashes

**Status:** FROZEN

**Frozen (UTC):** 2026-11-08T22:56:11.988167+00:00

**Frozen content commit:** `a74284bdf9a81902e46775c967ed14c25a6f5cd7`

- `0fe4a5ac024b371bae8e7839e8c3f42d98746c723df043c0f097ac3fe8856860`  `comparison/freeze_04_baseline.ido`
- `5f7758399022899ff350d2b534e48031a88e606596cef42e90de13565e9b219e`  `comparison/freeze_04_compare.py`
- `fd3a2ca91752f57e803ba94a6e7b3b38ae4d7f863c8a203142c4b9c4199e6d3d`  `comparison/freeze_04_control.py`
- `046485a20f7498714995199c7d16774135f2f0a912d0b7977b3c6a586c5f134e`  `comparison/freeze_04_identityops.py`
- `b2492098febbb6ba47d2e71a797dfa6c142f44dffeda4162a126f984fe26175b`  `comparison/freeze_04_operation_mapping.md`
- `2b687154f2abd2f146031b5a4caec44457e8d53cd5d8423e1baab25e30eafabd`  `comparison/freeze_04_reference.py`
- `1d499afae8206191aca950c89a4300ddf165911f2f0e692eb8f3daf7ae5f808a`  `comparison/freeze_04_restricted.ido`
- `92fe0f3965ab05d64daf00daf7bf38e170d4f911296bfc73a5a789ad69230f7e`  `comparison/freeze_04_specification.md`
- `f932a5e93204cbe2d9179da50281168f972a43556b7936be24466dd5f64854fa`  `contracts/FREEZE_02_GENERALIZATION.md`
- `c63a973075b6ffe1f9d8a53fbc1fed2997f19646f195d729590e123e2d295ca4`  `contracts/FREEZE_03_KERNEL_MISSING_VALUES.md`
- `d4dbf62026236accd40a7981faa1fe91d8c241d6f1c8b91915419a88057b974a`  `freeze_04.ps1`
