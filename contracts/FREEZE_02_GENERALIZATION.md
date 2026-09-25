# Freeze 02: Generalization Corpus and Execution

> Declared conditions governing the generalization experiment.

This record defines the generalization corpus, transformation apparatus,
execution procedure, validation procedure, interpretation constraints, and
artifact hashes applicable to the experiment.

Before Freeze 02 is established, these declarations define the proposed
generalization conditions.

Once Freeze 02 is established, these same declarations constitute the fixed
conditions under which the generalization experiment is executed and
interpreted.

## Scope

This freeze governs the held-out generalization experiment for the frozen
Freeze 01 `representation_preservation` commitment and evaluator.

The experiment evaluates preservation of PURL identity information across
SPDX and CycloneDX representation transformations performed by the declared
converter population.

The generalization corpus is constructed from the fixed sampling frame and
source-only eligibility, exclusion, and deterministic selection procedures
recorded in:

- `generalization/01-sampling.toml`;
- `generalization/02-candidates.toml`;
- `generalization/03-corpus.toml`; and
- `generalization/04-sources.toml`.

The transformation population and complete source-by-converter matrix are
recorded in:

- `generalization/05-transformations.toml`.

The corpus contains 10 held-out source artifacts:

- 8 CycloneDX sources; and
- 2 SPDX sources.

The transformation matrix contains 30 declared source-by-converter routes:

- 20 planned execution routes; and
- 10 routes recorded as `unsupported_pre_execution`.

Routes recorded as `unsupported_pre_execution` are not executed and are not
classified as transformation failures.

Conclusions from this experiment are limited to the declared corpus,
transformations, tool versions, platform, and frozen evaluator.

## Generalization Artifacts

The generalization experiment is defined by the following pre-outcome
artifacts:

- `contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`
  identifies the frozen commitment, evaluator, interpretation rules, and
  adjudication protocol applicable to the experiment;
- `generalization/01-sampling.toml`
  records the authored sampling specification;
- `generalization/02-candidates.toml`
  records source-only screening outcomes for the mechanically enumerated
  candidate set;
- `generalization/03-corpus.toml`
  records the deterministically selected held-out corpus;
- `generalization/04-sources.toml`
  records the exact preserved source artifacts and their provenance;
- `generalization/05-transformations.toml`
  records the converter population, target validator, executable artifacts,
  runtime dependencies, complete transformation matrix, exact command
  arguments, output paths, route statuses, and pre-execution capability
  decisions; and
- `known/known_violations.toml`
  records any defect shapes permitted to support a later `rediscovered`
  classification.

The preserved source documents under `generalization/sources/` are part of the
experimental evidence base and must remain byte-identical to the artifacts
recorded in `04-sources.toml`.

The converter, runtime, and target-validator artifacts used during execution
must match the paths and SHA-256 digests recorded in
`05-transformations.toml`.

## Evaluator Environment

The frozen Freeze 01 evaluator delegates PURL canonicalization to
`packageurl-python`.

Generalization evaluation therefore depends on the resolved Python dependency
environment as well as on the files hashed by Freeze 01.

Evaluation is performed using:

- the Python version declared in `.python-version`;
- the dependency versions resolved in `uv.lock`, including the resolved
  `packageurl-python` version; and
- `uv run --frozen`, so `uv.lock` is used as the dependency source of truth
  and is not updated during execution.

The actual Python version used during formal execution is recorded with the
execution evidence.

The generalization experiment evaluates commitment
`purl_preservation_v1` from `contracts/commitments.toml`.

## Transformation Execution

Only routes recorded as `planned` in
`generalization/05-transformations.toml` are executed.

Each planned route is executed using:

- the preserved source artifact recorded for that route;
- the exact converter artifact recorded for that converter;
- the recorded runtime artifact where one is required;
- the exact `command_argv` recorded for the route; and
- the declared target, validation-result, evaluator-result, and log paths.

The execution procedure must preserve, for each attempted route:

- route identifier;
- source identifier and SHA-256 digest;
- converter identity and version;
- exact command arguments;
- converter exit code;
- complete transformation log;
- generated target document when one is produced;
- generated target SHA-256 digest;
- target document validation result;
- complete evaluator output when evaluation can be performed; and
- sufficient execution-status information to distinguish execution,
  validation, evaluation, and adjudication outcomes.

An attempted planned route is an execution failure when the converter exits
nonzero or does not produce the declared target document.

A route recorded as `unsupported_pre_execution` is not attempted and is not an
execution failure.

No held-out transformation output may be examined before this Freeze 02 record
is established.

The implementation that performs this procedure is part of the experimental
apparatus and must be hash-recorded before Freeze 02 is established.

Every planned route is executed from the repository root so that relative paths
in the declared command arguments resolve from the same location.

For Syft execution:

- `SYFT_CHECK_FOR_APP_UPDATE=false` is set;
- undeclared `SYFT_*` environment variables must not affect execution; and
- Syft configuration files outside the declared experimental apparatus must not
  affect execution.

The effective environment supplied to each converter is recorded with the
execution evidence.

Converter-generated targets are not assumed to be byte-reproducible across
executions because converters may generate timestamps, namespaces, or other
execution-derived values.

The target produced by the formal execution of a route is retained as the
experimental evidence.

A route is not silently re-executed to obtain a different target.
If another execution is required, the original attempt is retained and the
additional execution is separately identified.

## Target Document Validation

Target document validation is recorded independently from transformation
execution and identity-preservation evaluation.

For every planned transformation route:

- a nonzero converter exit or absence of a target document is an execution
  failure;
- a successful converter execution that produces a target document proceeds to
  target document validation;
- target document validation records whether the generated target conforms to
  the applicable target representation;
- a target document that fails validation is retained and is not reclassified
  as an execution failure;
- when the frozen Freeze 01 evaluator can process the target document,
  identity-preservation evaluation proceeds regardless of the target document
  validation result; and
- the target document validation result and evaluator verdict are recorded and
  reported separately.

A successfully generated target document may therefore pass or fail target
document validation independently of whether the frozen Freeze 01 evaluator
reports `PRESERVED`, `VIOLATED_*`, or another evaluator verdict.

Target document validation does not override, relabel, or modify an evaluator
verdict.

Target document validation has three recorded outcomes:

- `valid`: the validator completed and reported conformance;
- `invalid`: the validator completed and reported non-conformance; and
- `validation_error`: the validator could not complete validation.

`validation_error` is neither an execution failure nor an `invalid` result.
It is reported separately.

For SPDX 2.3 targets, sbom-utility uses its applicable SPDX 2.3 schema variant
for validation.

When the frozen evaluator cannot process a generated target document, the
route records `evaluation_error` together with the evaluator's complete error
output.

`evaluation_error` is not an evaluator verdict and is not a preservation
violation.

## Known Limitations and Disclosures

The experiment is a bounded generalization pilot and is not a statistically
representative survey of production SBOMs or SBOM transformation tooling.

The held-out sampling frame consists of fixed revisions of official SPDX and
CycloneDX example repositories.
Conclusions therefore apply to this declared frame and
should not be interpreted as prevalence estimates for software
supply chains generally.

The 10-member corpus contains 8 CycloneDX sources and 2 SPDX sources.

The planned transformation matrix is directionally unbalanced:

- 16 planned routes are CycloneDX-to-SPDX; and
- 4 planned routes are SPDX-to-CycloneDX, over 2 held-out SPDX sources.

The SPDX-to-CycloneDX direction contains [EXACT COUNT] applicable source PURLs
across those 2 held-out sources.

This direction therefore supports more limited generalization evidence than
the larger CycloneDX-to-SPDX route population.

Corpus members are not assumed to be statistically independent.
The transformation route is the primary execution unit, and component-level
or PURL-level observations are nested within routes and source artifacts rather
than treated as independent experimental replicates.

The selected converter population is deliberately bounded and is not claimed
to be exhaustive or statistically representative of all SBOM transformation
implementations.

Some declared source-by-converter combinations are recorded as
`unsupported_pre_execution` because the source representation falls outside
the converter's documented capability.
These routes remain in the complete matrix and are not replaced
by different corpus members.

The cdx2spdx CycloneDX routes are planned attempts even though the converter
does not publish a source-version support matrix comparable to the one
available for Protobom.
Their inclusion therefore tests the declared route without asserting
documented support for each selected CycloneDX source version.

The frozen evaluator reads `kind`, `id`, and `representable_in` from the
commitment record.

Canonical and noncanonical locations, content-hash anchoring, the
exactly-one-source-PURL rule, and canonical PURL comparison are implemented
directly in the frozen adapter and evaluator code.

That code implements the values declared in the commitment record, but it does
not read those values dynamically from every corresponding declaration in the
commitment record.

The comment in `contracts/commitments.toml` stating that slot declarations
"are read by the format adapters" is therefore inaccurate.
Because that file is covered by Freeze 01, the frozen file is not edited; the
implementation limitation is disclosed here.

`noncanonical_slots` is declared for CycloneDX only.

For CycloneDX-to-SPDX routes, `VIOLATED_RELOCATED` therefore cannot occur
under the frozen evaluator.

A source PURL that survives in an SPDX target outside the recognized canonical
`PACKAGE-MANAGER`/`purl` external reference may therefore be reported as
`VIOLATED_DROPPED` rather than `VIOLATED_RELOCATED`.

Adjudication confirms or rejects a candidate violation but does not reclassify
the evaluator's violation subtype.

The CycloneDX adapter evaluates entries under `components`, including nested
components, but does not evaluate `metadata.component`.

The SPDX adapter evaluates package records, including the described package.

The source populations evaluated by the two adapters therefore do not have
identical document-level subject coverage.

The generalization toolchain is prepared for Windows x64.
Results from this execution do not by themselves establish
equivalent behavior on other operating systems or architectures.

Before the generalization sampling specification was fixed, an aggregate
source-only feasibility scan was performed on the declared sampling frame.
No transformation outputs or evaluator comparisons
were examined during that scan.

The CycloneDX `bom-examples` repository had also previously supplied the
Dropwizard source used in reverse-direction engineering validation.
That prior use is disclosed because the repository
later forms part of the generalization sampling frame;
the generalization corpus itself was constructed by the predeclared source-only rules
and excludes previously declared validation material.

## Verification

Before Freeze 02 is established and before any held-out transformation is
executed, the repository must pass the complete Freeze 02 prerequisite
verification.

The verification procedure confirms:

- Freeze 01 byte integrity;
- provenance from the authored sampling specification through candidate
  screening and corpus construction;
- corpus membership and generated-record hashes;
- preserved-source membership, paths, sizes, and SHA-256 digests;
- exact correspondence between the corpus and preserved-source records;
- converter artifact paths and SHA-256 digests;
- required runtime artifact paths, versions, and SHA-256 digests;
- target-validator artifact path and SHA-256 digest;
- completeness and uniqueness of the source-by-converter transformation
  matrix;
- planned and `unsupported_pre_execution` route invariants;
- declared transformation and validation commands;
- pre-execution matrix counts; and
- that formal generalization execution has not begun.

The prerequisite gate is run with:

```powershell
uv run python -m preservation_test.generalization.verification.verify_05_freeze_02
```

Freeze 02 must not be established if this verification fails.

## Artifact Hashes

Freeze 02 records SHA-256 digests for the exact artifacts whose identity must
remain fixed during generalization execution.

The recorded set includes at least:

- `contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`;
- `uv.lock`;
- `.python-version`;
- `generalization/01-sampling.toml`;
- `generalization/02-candidates.toml`;
- `generalization/03-corpus.toml`;
- `generalization/04-sources.toml`;
- `generalization/05-transformations.toml`;
- every preserved source document referenced by `04-sources.toml`;
- every converter artifact referenced by `05-transformations.toml`;
- every required runtime artifact referenced by `05-transformations.toml`;
- the target-validator artifact referenced by `05-transformations.toml`;
- the generalization execution implementation;
- the Freeze 02 verification implementation;
- `known/known_violations.toml`, which may declare no defect shapes; if it
  declares none, no generalization result is classified as rediscovered; and
- this Freeze 02 record.

The exact digest values are generated from the repository state used to
establish Freeze 02 and are not manually inferred from version labels.

Any later change to an artifact covered by this freeze requires application of
the applicable freeze-break procedure before affected generalization evidence
can be interpreted under a new freeze.
