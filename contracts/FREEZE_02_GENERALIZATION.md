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

Evaluation is performed with the Python version declared in `.python-version`.
Dependency versions are those resolved in `uv.lock`,
including the resolved `packageurl-python` version.
The executor is launched with `uv run --frozen`,
so `uv.lock` is the dependency source of truth and is not updated during execution.
The executor invokes the frozen evaluator with its own interpreter:
`python -m preservation_test.evaluator.evaluate <source> <target> --json --commitment-file contracts/commitments.toml --commitment-id purl_preservation_v1`.
The actual Python version used during formal execution is recorded in the run manifest.
The frozen evaluator rejects a target document that begins with a UTF-8 byte-order mark.
Such a target yields `evaluation_error`.

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

Each converter runs with an environment built from an explicit allowlist.
The allowlist holds
`SystemRoot`, `WINDIR`, `TEMP`, `TMP`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`,
a minimal `PATH`, `SYFT_CHECK_FOR_APP_UPDATE=false`, and
a `JAVA_HOME` pinned to the repository-local JDK.
Undeclared `SYFT_*` variables, Java options, Python options,
and proxy variables are not inherited.

Before the first route, the executor refuses to run
if a Syft configuration file exists in the
local, user, or XDG locations that Syft searches.
The effective Syft configuration is captured before any route runs.
The effective environment supplied to each converter is recorded with the execution evidence.

Every subprocess runs under the `timeout_seconds`
declared in `05-transformations.toml`.
A timeout terminates the process tree and retains the available output.
A converter timeout is an execution failure.
A validator timeout is `validation_error`.
An evaluator timeout is `evaluation_error`.

Converter-generated targets are not assumed to be byte-reproducible across
executions because converters may generate timestamps, namespaces, or other
execution-derived values.

The target produced by the formal execution of a route is retained as the
experimental evidence.

The first formal execution of each planned route is the evidence of record.
No formal retry or resume is implemented under this freeze.
The executor refuses any invocation against a populated results directory.
`retry_directory_pattern` in `05-transformations.toml`
is a reserved field and authorizes no re-execution.
A host interruption leaves its evidence in place.

Completing an interrupted execution requires
an explicit amendment or new freeze,
with evidence kept in a separately located directory.
No attempt is silently replaced or selected for a better outcome.

## Evidence Layout

Every evidence path is predeclared in `05-transformations.toml`.
The executor does not choose evidence locations.

Each planned route declares paths for the target document,
the validation result, the evaluator result, the converter log,
the validator log, the evaluator log, and an `execution.json` record.

The `execution.json` record is written
with status `started` before the converter
is launched and is updated after each step.
It records route identity, attempt number, start and end times,
source and target SHA-256 digests,
converter identity, exact command arguments,
working directory, effective environment,
each exit code, timeout status, and the validation and evaluation outcomes.

The run manifest at `run_manifest_path` records the mode,
repository commit, interpreter, platform, plan digest,
the SHA-256 of this record, the Syft configuration check,
route progression, and completion state.

An execution record still at `started` after an interruption is not resumed.

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

Validator exit code 0 is `valid` and exit code 2 is `invalid`,
provided a result file exists.
A validator timeout, a launch error, any other exit code,
or a missing result file is `validation_error`.
The recorded validation decision is the exit code.
The result file is retained as evidence and may be empty.

For SPDX 2.3 targets, sbom-utility uses its applicable
SPDX 2.3 schema variant for validation.

When the frozen evaluator cannot process a generated target document, the
route records `evaluation_error` together with the evaluator's complete error
output.

`evaluation_error` is not an evaluator verdict and is not a preservation
violation.

## Adjudication and Interpretation

Every evaluator result is retained and reported.

Evaluator verdicts are interpreted according to the frozen Freeze 01
commitment and evaluator.

A candidate `VIOLATED_DROPPED`, `VIOLATED_RELOCATED`, or
`VIOLATED_ALTERED` result is subjected to adjudication.

A candidate preservation violation is confirmed only when:

1. the source PURL is present in the source semantic role;
2. the target representation supports the required PURL semantic role;
3. the source and target records are validly associated under the frozen
   anchoring procedure; and
4. the target fails the frozen preservation obligation by dropping,
   relocating, or altering the PURL.

Adjudication confirms or rejects the candidate preservation violation.
It does not change or relabel the evaluator's violation subtype.
Adjudication inspects the raw source and target documents and
does not reuse evaluator output as evidence.

For each adjudicated finding, the adjudication record contains:

- the source component's JSON as it appears in the source document;
- the anchored target component's JSON as it appears in the target document;
- every location in the target document where the source PURL string
  or its canonical form occurs; and
- the decision for each of the four criteria, with a reason.

Formal route results are reported using the following result classes:

- `rediscovered`: a confirmed `VIOLATED_*` result
  matching a defect shape declared in `known/known_violations.toml` before Freeze 02.
  A match is on direction, verdict, and where given target location.
  It does not assert the same cause, converter, or version as the established case;
- `new confirmed`: a confirmed `VIOLATED_*` result for which no predeclared
  defect shape matches;
- `false positive`: a candidate `VIOLATED_*` result rejected by adjudication;
- `preserved`: evaluator verdict `PRESERVED`;
- `expected/refused`: evaluator verdict `UNSUPPORTED` or `NOT_APPLICABLE`;
- `underdetermined`: evaluator verdict `UNDERDETERMINED`; and
- `unanchorable`: evaluator verdict `UNANCHORABLE`.

Result classes apply to individual source PURLs within evaluated routes.
Route-level outcomes are reported per route:
execution failure, validation outcome, and `evaluation_error`.

No result class is silently discarded.

`known/known_violations.toml` declares two defect shapes.
`purl-to-cyclonedx-properties` is SPDX to CycloneDX with verdict `VIOLATED_RELOCATED`.
`purl-absent-from-spdx-canonical-ref` is CycloneDX to SPDX with verdict `VIOLATED_DROPPED`.
Matching depends on direction, verdict, and, where given, target location.
It does not depend on converter, package, or anchor.
Because `VIOLATED_RELOCATED` cannot occur for SPDX targets,
every confirmed CycloneDX-to-SPDX `VIOLATED_DROPPED` result
matches a predeclared shape.
Only `VIOLATED_ALTERED` can therefore be `new confirmed` in that direction.

`UNANCHORABLE` results are reported in full, including their count and
fraction by route.
No post hoc threshold is used to remove a route or source
from interpretation.

The transformation route, defined by one preserved source and one converter,
is the primary execution unit. Component-level and PURL-level observations
within a route are nested observations and are not treated as independent
experimental replicates.

## Known Limitations and Disclosures

The experiment is a bounded generalization pilot and is not a statistically
representative survey of production SBOMs or SBOM transformation tooling.

The held-out sampling frame consists of fixed revisions of official SPDX and
CycloneDX example repositories.
Conclusions therefore apply to this declared frame and
should not be interpreted as prevalence estimates for software
supply chains generally.

The 10-member corpus contains **8 CycloneDX sources and 2 SPDX sources**.
The planned transformation matrix is directionally unbalanced:

- 16 planned routes are CycloneDX-to-SPDX; and
- 4 planned routes are SPDX-to-CycloneDX, over **2 held-out SPDX sources**.

The SPDX-to-CycloneDX direction contains **6 canonical source PURL occurrences**
across those 2 held-out sources (see `.\count.ps1`).

- 4 canonical PURL occurrences in `gen-spdx-e38ee905f9c0.spdx.json`
- 2 canonical PURL occurrences in `gen-spdx-0d278129197b.spdx.json`
- 6 total packages with exactly one canonical PURL
- 5 of those 6 also have a content hash

This direction therefore supports more limited generalization evidence than
the larger CycloneDX-to-SPDX route population.

The selected converter population is deliberately bounded and is not claimed
to be exhaustive or statistically representative of all SBOM transformation
implementations.

Ten declared source-by-converter combinations are recorded
as `unsupported_pre_execution`.
Eight are Protobom routes over CycloneDX 1.2 and 1.3 sources,
which fall outside its documented JSON input support.
Two are cdx2spdx routes over SPDX sources,
because cdx2spdx implements CycloneDX-to-SPDX conversion only.

These routes remain in the complete matrix and are not replaced
by different corpus members.

The deterministic within-unit selection rule selected CycloneDX 1.2 or 1.3
documents for every CycloneDX corpus member, including selection units that
also contained later-version documents.

Those selected CycloneDX versions fall outside Protobom's declared JSON input
support for CycloneDX 1.4 through 1.7.

Consequently, Protobom has no planned CycloneDX-to-SPDX route in this
experiment.
Its 8 corresponding source-by-converter routes remain in the matrix as
`unsupported_pre_execution` rather than being replaced by different
source artifacts.

Freeze 01 grounds the CycloneDX canonical PURL location in the CycloneDX 1.6
specification.

Applying the frozen evaluator to CycloneDX 1.2 and 1.3 source documents assumes
that `component.purl` has the same relevant preservation semantics in those
versions.

That assumption is disclosed as a limitation of the generalization scope.

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
uv run --frozen python -m preservation_test.generalization.verification.verify_05_freeze_02
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
- every file in the repository-local Java runtime;
- every Python module of the apparatus except the generated `_version.py`, including the execution implementation and the pre-freeze and post-freeze verification implementations;
- `freeze_02.ps1`;
- `generalization/PREDICTIONS.md`;
- the smoke plan and smoke evidence under `validation/executor-smoke/`; and
- `known/known_violations.toml`.

The exact digest values are generated from the repository state used to
establish Freeze 02 and are not manually inferred from version labels.

The Freeze 02 record is not included in its own content-hash set.
Its exact contents are fixed by the Git commit
that records the established freeze
after this record is generated and reviewed.

Any later change to an artifact covered by this freeze requires application of
the appropriate freeze-break procedure
before affected generalization evidence
can be interpreted under a new freeze.
