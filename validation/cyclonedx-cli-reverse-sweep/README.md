# cyclonedx-cli Reverse-Direction Exploratory Sweep

This directory records an exploratory engineering-validation sweep of the
frozen PURL representation-preservation commitment in the reverse
CycloneDX-to-SPDX direction.

The sweep uses the same cyclonedx-cli release family examined in the
SPDX-to-CycloneDX engineering-validation release sweep, but does not assume
that execution behavior or preservation behavior is symmetric across
directions.

## General Area of Interest

```text
cyclonedx-cli 0.30.0
    └── CycloneDX.Spdx.Interop 11.0.0

cyclonedx-cli 0.31.0
    └── CycloneDX.Spdx.Interop 11.0.0

cyclonedx-cli 0.32.0
    └── CycloneDX.Spdx.Interop 12.1.1 #fix
```

## Research Question

In the reverse CycloneDX-to-SPDX direction, what fraction of source
components can be evaluated under the frozen PURL representation-preservation
commitment, what anchoring and limitation outcomes occur, and among evaluable
components, how does preservation behavior vary across the same
converter-family release history?

A secondary exploratory question is whether any observed preservation boundary
aligns with the previously observed SPDX-to-CycloneDX release boundary.

## Evidence Role

This sweep is exploratory engineering validation.

No execution outcomes or preservation verdicts are predeclared for the reverse
direction. The sweep records observed execution, preservation, anchoring,
applicability, and limitation outcomes under the already frozen commitment and
evaluator.

Because the converter family and release history are already part of the
engineering-validation program, these results are not held-out generalization
evidence and will not be treated as such in later analysis.

Independent converter families intended for the later generalization study are
not exercised by this sweep.

## Frozen Scientific Apparatus

The sweep uses the already frozen PURL representation-preservation commitment
and evaluator recorded in:

`contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`

The sweep does not modify the frozen commitment in response to observed
reverse-direction results.

If the reverse-direction work exposes a defect in the implementation of the
frozen specification, that defect must be recorded separately from empirical
converter behavior. Any change to frozen scientific apparatus must follow the
existing freeze-break procedure.

## Known Evaluator Limitation

For SPDX 2.3 targets, the frozen adapter recognizes PURLs only in the
canonical PACKAGE-MANAGER/purl ExternalRef representation.
It does not enumerate arbitrary target fields
that may contain text derived from a PURL.

This distinction matters because textual survival does not necessarily
constitute identifier preservation.
SPDXID is an element identifier, not a PURL representation,
and SPDX 2.3 constrains its idstring to letters, numbers, `.` and `-`.
A raw PURL therefore cannot be represented conformantly in SPDXID.

Accordingly, a PURL that is absent from the canonical ExternalRef and appears
only as text inside an invalid SPDXID remains absent as a conforming PURL
representation.
The frozen evaluator classifies that case as VIOLATED_DROPPED.

The frozen evaluator will not be modified for this exploratory sweep.

## Reverse-Direction Diagnostic Inspection

The initial exploratory run produced a uniform pre-boundary result:
167/167 applicable components were independently anchored and classified as
preservation violations.

Because such uniformity could indicate a systematic adapter or evaluator error,
the generated SPDX targets were inspected manually before interpreting the
result.

The inspection confirmed that:

- the generated targets are SPDX 2.3;
- component anchoring is supported by preserved checksums;
- across both pre-boundary and post-boundary releases, the PURL text is
  incorporated into SPDXID;
- those SPDXID values contain characters not permitted by the SPDX 2.3
  SPDXID grammar and therefore do not constitute conforming PURL
  representations;
- before cyclonedx-cli 0.32.0, the source PURL is absent from the canonical
  PACKAGE-MANAGER/purl ExternalRef representation;
- beginning with 0.32.0, the canonical PACKAGE-MANAGER/purl ExternalRef is
  additionally present; and
- the frozen evaluator reports PRESERVED beginning at the same boundary.

The inspection ruled out a simple reverse-adapter lookup failure and confirmed
that the preservation boundary concerns canonical PURL representation, not
whole-document SPDX validity.

## Source Selection

The CycloneDX source used for the release sweep must be fixed before any
release in the sweep is executed against it.

The source must not be selected or modified in response to observed
reverse-direction cyclonedx-cli behavior.

Before execution, preserve:

- the source artifact;
- its provenance;
- its SHA-256 digest;
- the CycloneDX specification version;
- the source-selection rationale; and
- the date on which source selection was fixed.

The authoritative source path and SHA-256 digest are recorded in
`releases.toml`.

The source should contain enough independently represented component
information to exercise component anchoring without using the PURL being
evaluated as its own anchor.

The source should also preserve naturally occurring identifier structure.
Identifiers must not be added solely to force particular evaluator outcomes.

### Source Selection Process

Select the first official [CycloneDX](https://github.com/CycloneDX) JSON example,
in repository/path order, that:

1. is valid against a published CycloneDX specification;
2. contains at least two components;
3. contains at least one component with a canonical component.purl;
4. contains at least one component with both component.purl and a cryptographic hash;
5. was not generated by cyclonedx-cli;
6. was selected without executing any tested cyclonedx-cli release against it.

For example, look in [bom-examples repo](https://github.com/CycloneDX/bom-examples).

Then <https://github.com/CycloneDX/bom-examples/tree/master/SBOM/dropwizard-1.3.15>.

Then <https://github.com/CycloneDX/bom-examples/blob/master/SBOM/dropwizard-1.3.15/bom.json>

Get-FileHash validation/cyclonedx-cli-reverse-sweep/source.cdx.json -Algorithm SHA256

Record the SHA in releases.toml.

## Release Selection

`releases.toml` is the authoritative release specification for this sweep.

The release set is fixed explicitly rather than discovered dynamically during
execution.

It uses the same cyclonedx-cli release series examined by the forward
engineering-validation sweep:

- 0.29.0
- 0.29.1
- 0.29.2
- 0.30.0
- 0.31.0
- 0.32.0
- 0.33.0
- 0.33.1

The associated CycloneDX.Spdx.Interop versions are recorded for provenance and
for later comparison with the forward-direction release history.

The field `dependent_library_includes_purl_fix` records the already established
library-history boundary. It is historical metadata only.

It does not define an expected reverse-direction outcome.

## No Predeclared Reverse Verdict

This is an exploratory sweep.

The configuration therefore does not contain an `expected_verdict` field for
the reverse direction.

The sweep must not infer a reverse-direction expectation from the known
SPDX-to-CycloneDX result.

In particular, the presence of the PURL conversion change in a dependent
library does not establish in advance that reverse-direction behavior is
preserved, violated, symmetric, or even executable for the selected source.

Observed classifications are recorded only after execution.

## Execution and Preservation Are Separate

Execution status and preservation outcome are separate observations.

Examples include:

- a converter may fail before producing an SPDX target;
- a target may be produced while a source component cannot be independently
  anchored;
- a component may be applicable but underdetermined under the frozen
  commitment;
- an evaluable component may preserve its PURL;
- an evaluable component may violate the preservation commitment.

An execution failure does not receive a preservation verdict.

An unanchorable or underdetermined component must not be counted as preserved.

## Outcomes Recorded

For each release, the sweep should record at least:

- observed execution status;
- total source components;
- applicable components;
- evaluable components;
- `PRESERVED`;
- preservation-violation outcomes;
- `UNANCHORABLE`;
- `UNDERDETERMINED`;
- `NOT_APPLICABLE`; and
- any other frozen evaluator outcome that occurs.

The sweep should retain the specific evaluator classifications rather than
collapsing them prematurely into a binary pass/fail value.

## Coverage

Coverage is a first-class result of this sweep.

For each successfully executed release, report the fraction of source
components that reach a preservation verdict and the fractions that instead
produce anchoring, applicability, or limitation outcomes.

At minimum, derive:

- evaluable fraction;
- unanchorable fraction;
- underdetermined fraction;
- preserved fraction among evaluable components; and
- violation fraction among evaluable components.

Preservation percentages must not hide components excluded by anchoring or
limitation outcomes.

A release with a high preservation rate among evaluable components but a low
evaluable fraction must be reported as such.

## Interpretation

The sweep does not begin with a hypothesis that the forward release boundary
must appear in reverse.

Possible informative results include:

- predominantly preserved reverse transformations;
- a preservation transition aligned with the forward release boundary;
- a different reverse-direction transition;
- preservation violations not observed in the forward direction;
- high `UNANCHORABLE` rates;
- `UNDERDETERMINED` cases that exercise previously unused branches of the
  frozen commitment;
- source or target processing failures; or
- stable behavior across the entire tested release series.

These outcomes have different meanings and must remain distinguishable in the
recorded evidence.

## Relationship to the Forward Sweep

The forward engineering-validation sweep is recorded separately in:

`validation/cyclonedx-cli-release-sweep/`

That sweep tests predeclared expectations derived from a known historical
SPDX-to-CycloneDX defect and its release-history boundary.

This reverse sweep differs methodologically:

- the transformation direction is CycloneDX to SPDX;
- reverse preservation verdicts are not known in advance;
- the primary purpose is to pressure-test the frozen preservation commitment,
  anchoring procedure, and limitation outcomes in the opposite direction; and
- comparison with the forward release boundary occurs only after the reverse
  observations have been recorded.

The forward and reverse sweeps therefore answer different engineering-
validation questions.

## Relationship to Generalization

This sweep does not consume independent converter families reserved for the
later generalization study.

Results obtained here are known before that generalization corpus is frozen
and therefore cannot later be presented as unseen generalization evidence.

The purpose of this sweep is instead to expose implementation, anchoring,
cardinality, applicability, or directionality problems cheaply within the
already studied converter family before a separately frozen generalization
study is executed.

## Generated Evidence

Generated evidence should be written beneath this directory without modifying
the fixed source or release specification.

A suggested structure is:

```text
validation/cyclonedx-cli-reverse-sweep/
├── README.md
├── releases.toml
├── results.json
├── population-check.txt
├── validation-checks/
│   ├── spdx-validator-0.31.0.txt
│   ├── spdx-validator-0.32.0.txt
│   └── spdx-validator-summary.json
└── artifacts/
    ├── 0.29.0/
    │   ├── target.spdx.json
    │   └── result.json
    ├── 0.29.1/
    │   ├── target.spdx.json
    │   └── result.json
    └── ...
```

A target artifact exists only when the corresponding transformation completes
successfully.

`results.json` is the aggregate machine-readable record of the sweep.

## Routing

```text
A  PURL genuinely absent
   -> converter behavior
   -> VIOLATED_DROPPED may stand

B  PURL is in the canonical SPDX representation,
   but the adapter fails to recognize it
   -> adapter implementation defect
   -> repair adapter, document freeze break, re-freeze, rerun

C  PURL survives in the SPDX target,
   but outside the canonical representation recognized by the commitment
   -> real preservation violation
   -> current evaluator gets the broad fact right ("not preserved canonically")
      but may misclassify DROPPED vs RELOCATED

D  PURL is exactly where the frozen adapter expects it,
   yet the evaluator still reports violation
   -> evaluator logic defect
   -> stop and debug before interpreting anything
```

## Manual Inspection

Does the corresponding package have externalRefs?

For each ExternalRef:
referenceCategory?
referenceType?
referenceLocator?

Does the literal source PURL occur anywhere in the target?

If not literally:
is there an altered/malformed representation that is recognizably derived
from it?

## Results

```text
[0.29.0] Spdx.Interop 10.0.0 expectation_role=exploratory
[0.29.0] execution=completed evaluable=167/167 PRESERVED=0 VIOLATED=167 UNANCHORABLE=0 UNDERDETERMINED=0
[0.29.1] Spdx.Interop 10.0.1 expectation_role=exploratory
[0.29.1] execution=completed evaluable=167/167 PRESERVED=0 VIOLATED=167 UNANCHORABLE=0 UNDERDETERMINED=0
[0.29.2] Spdx.Interop 10.0.2 expectation_role=exploratory
[0.29.2] execution=completed evaluable=167/167 PRESERVED=0 VIOLATED=167 UNANCHORABLE=0 UNDERDETERMINED=0
[0.30.0] Spdx.Interop 11.0.0 expectation_role=exploratory
[0.30.0] execution=completed evaluable=167/167 PRESERVED=0 VIOLATED=167 UNANCHORABLE=0 UNDERDETERMINED=0
[0.31.0] Spdx.Interop 11.0.0 expectation_role=exploratory
[0.31.0] execution=completed evaluable=167/167 PRESERVED=0 VIOLATED=167 UNANCHORABLE=0 UNDERDETERMINED=0
[0.32.0] Spdx.Interop 12.1.1 expectation_role=exploratory
[0.32.0] execution=completed evaluable=167/167 PRESERVED=167 VIOLATED=0 UNANCHORABLE=0 UNDERDETERMINED=0
[0.33.0] Spdx.Interop 12.1.1 expectation_role=exploratory
[0.33.0] execution=completed evaluable=167/167 PRESERVED=167 VIOLATED=0 UNANCHORABLE=0 UNDERDETERMINED=0
[0.33.1] Spdx.Interop 12.1.2 expectation_role=exploratory
[0.33.1] execution=completed evaluable=167/167 PRESERVED=167 VIOLATED=0 UNANCHORABLE=0 UNDERDETERMINED=0
```

Summary

```text
0.29.0-0.31.0
    hashes preserved
    components anchor successfully
    PURLs absent from canonical SPDX ExternalRef
    167/167 -> VIOLATED_DROPPED

0.32.0-0.33.1
    hashes preserved
    components anchor successfully
    canonical PACKAGE-MANAGER/purl ExternalRef appears
    167/167 -> PRESERVED
```

The exploratory reverse-direction sweep independently exhibits the same release boundary:
all 167 evaluable PURLs are non-preserved through cyclonedx-cli 0.31.0
and all 167 are canonically preserved beginning with 0.32.0.

## Post Interpretation

The reverse CycloneDX-to-SPDX sweep exhibits the same 0.32.0 release boundary
as the forward sweep.

Through cyclonedx-cli 0.31.0, all 167 applicable source components are
independently anchored, but their PURLs are absent from the canonical SPDX
PACKAGE-MANAGER/purl ExternalRef representation.

The PURL text nevertheless appears inside package SPDXID values such as:

```text
SPDXRef-pkg:maven/com.fasterxml.jackson.core/jackson-annotations@2.9.10?type=jar
```

That textual occurrence does not constitute a preserved SPDX PURL
representation.
SPDXID is an SPDX element identifier, and the SPDX 2.3
identifier grammar permits only letters, numbers, `.` and `-`
in its idstring.
The raw PURL introduces characters such as `:`, `/`, `@`, and `?`
that are not permitted there.

The pre-boundary reverse result is therefore appropriately classified as
VIOLATED_DROPPED:
no conforming PURL representation survives in the SPDX
target, even though text derived from the PURL remains physically present in
the document.

Beginning with cyclonedx-cli 0.32.0, the converter additionally emits the
canonical PACKAGE-MANAGER/purl ExternalRef for all 167 applicable components,
and the frozen evaluator reports PRESERVED for all 167.

The malformed PURL-derived SPDXID pattern persists after this boundary.
Independent SPDX validation rejects both the 0.31.0 and 0.32.0 generated
documents for the same SPDXID-related reasons.

The observed release boundary therefore concerns PURL representation
preservation rather than whole-document SPDX validity:

```text
before 0.32.0
    no canonical PURL ExternalRef
    invalid PURL-derived SPDXID
    -> VIOLATED_DROPPED

from 0.32.0
    canonical PURL ExternalRef present
    invalid PURL-derived SPDXID persists
    -> PRESERVED under the frozen PURL-preservation commitment
```

Causation is not inferred from the release sweep alone.

## Distinct Failure Modes at the Same Release Boundary

The forward and reverse sweeps exhibit the same observed 0.32.0 release
boundary but different pre-boundary preservation failures.

In the forward SPDX-to-CycloneDX direction, the PURL survives in a
noncanonical CycloneDX property rather than component.purl.
The frozen evaluator classifies that behavior as VIOLATED_RELOCATED.

In the reverse CycloneDX-to-SPDX direction before 0.32.0, the PURL is absent
from the SPDX PACKAGE-MANAGER/purl ExternalRef representation.
Its text also appears inside an SPDXID value that does not satisfy the SPDX 2.3
identifier grammar.
Independent validation confirms that this malformed SPDXID pattern
persists on both sides of the preservation boundary.
The frozen evaluator classifies the pre-boundary preservation behavior as
VIOLATED_DROPPED because no conforming PURL representation is present.

Thus the same release boundary is associated with two distinct
representation-preservation failure shapes:

```text
SPDX -> CycloneDX
    PURL survives in a noncanonical representational slot
    -> VIOLATED_RELOCATED

CycloneDX -> SPDX
    no conforming PURL representation survives
    -> VIOLATED_DROPPED
```

Beginning with cyclonedx-cli 0.32.0, both directions produce the canonical
PURL representation expected by the frozen commitment.

The release sweep establishes the behavioral boundary but does not by itself
establish the causal mechanism responsible for the change.

## Stable Evaluation Population

The evaluator population was stable across all tested cyclonedx-cli releases.
See `rev-ck.ps1`.

Each release produced results for the same 167 source-component references.
Relative to the 0.29.0 baseline, every later release had:

- `same=True`
- `added=0`
- `missing=0`

The reported `167/167` denominator therefore refers to the same source-component
population throughout the release sweep rather than to changing per-release
subsets.

## Independent SPDX Validation

The generated SPDX targets for cyclonedx-cli 0.31.0 and 0.32.0 were checked
with the independent `spdx-tools` validator.
See `rev-validate.ps1`.

The results were:

```text
0.31.0
    invalid_external_document_ref = 167
    invalid_internal_spdx_id      = 167
    missing_external_document_ref = 167
    license_expression            = 1

0.32.0
    invalid_external_document_ref = 167
    invalid_internal_spdx_id      = 167
    missing_external_document_ref = 167
    license_expression            = 1
```

Both generated SPDX documents remain invalid for the same SPDXID reason.

For both releases, the validator reported 167 occurrences of each of the
following SPDXID-related problems:

- invalid external-document-reference parsing;
- invalid internal SPDX identifier syntax; and
- unresolved external document references.

Both targets also produced one unrelated license-expression validation error.

```text
Before 0.32.0:
    PURL absent from canonical SPDX ExternalRef
    PURL text embedded in invalid SPDXID
    -> VIOLATED_DROPPED

From 0.32.0 onward:
    PURL present in canonical SPDX ExternalRef
    PURL text still embedded in invalid SPDXID
    -> PRESERVED under the frozen PURL-preservation commitment
    -> generated SPDX remains independently invalid for a separate reason
```

The malformed PURL-derived SPDXID pattern therefore persists across the
0.32.0 preservation boundary.

The preservation transition at 0.32.0 is narrower: beginning with that
release, the converter additionally emits the PURL in the canonical
PACKAGE-MANAGER/purl ExternalRef representation. The frozen
representation-preservation commitment therefore changes from
VIOLATED_DROPPED to PRESERVED even though whole-document SPDX validation
continues to fail for the independently observed SPDXID issue.

## Next Steps

1. Keep independent converter families reserved for FREEZE_02 and the later
   generalization study.

2. Investigate the CycloneDX.Spdx.Interop release history separately if a
   causal explanation for the shared 0.32.0 boundary is needed.
   Do not infer causation from release alignment alone.
