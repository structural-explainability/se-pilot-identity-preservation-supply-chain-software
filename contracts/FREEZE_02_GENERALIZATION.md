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
`SystemRoot`, `WINDIR`, `TEMP`, `TMP`, `TMPDIR`, `HOME`,
`USERPROFILE`, `APPDATA`, `LOCALAPPDATA`,
`XDG_CONFIG_HOME`, and `XDG_CONFIG_DIRS`,
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

Every route evidence path and the run manifest path are predeclared
in `05-transformations.toml`.
The executor writes the effective Syft configuration log to
`syft-config.log` within the declared `results_directory`.

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

## Frozen Content Hashes

**Status:** FROZEN

**Frozen (UTC):** 2026-11-05T14:34:02.033998+00:00

**Frozen content commit:** `5bb17fe05ed18ba6c0ca260d17ad821c58998995`

- `a876e0b10411037a012498b9fe18d9bc1df32ed8b722a13564dc944ddcfd9135`  `.python-version`
- `8a570cf7f19fada550f850b3724d07ac9b67109d1fc8136fcf7306946b9162fa`  `bin/generalization/cdx2spdx.jar`
- `c02756bcd9fa8191bf0fda4451bc018414dd44ee35bf09922c24377a475e4b5a`  `bin/generalization/jdk-21.0.12.1+1/NOTICE`
- `88ace577a9c51061cb7d1a36babbbefa48212fadc838ffde98fdfff60de18386`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-console-l1-1-0.dll`
- `c062477ad3bfdc57b0cc402179637a214dab5045c8d644592c7decca7d18aa50`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-console-l1-2-0.dll`
- `1bd81dfd19204b44662510d9054852fb77c9f25c1088d647881c9b976cc16818`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-datetime-l1-1-0.dll`
- `591358eb4d1531e9563ee0813e4301c552ce364c912ce684d16576eabf195dc3`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-debug-l1-1-0.dll`
- `d56ce7b1cd76108ad6c137326ec694a14c99d48c3d7b0ace8c3ff4d9bcee3ce8`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-errorhandling-l1-1-0.dll`
- `91d249d7bc0e38ef6bcb17158b1fdc6dd8888dc086615c9b8b750b87e52a5fb3`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-fibers-l1-1-0.dll`
- `fc9d86cec621383eab636ebc87ddd3f5c19a3cb2a33d97be112c051d0b275429`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-fibers-l1-1-1.dll`
- `1ca895aba4e7435563a6b43e85eba67a0f8c74aa6a6a94d0fc48fa35535e2585`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-file-l1-1-0.dll`
- `4cadbc0c39da7c6722206fdcebd670abe5b8d261e7b041dd94f9397a89d1990d`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-file-l1-2-0.dll`
- `93c624b366ba16c643fc8933070a26f03b073ad0cf7f80173266d67536c61989`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-file-l2-1-0.dll`
- `39095f59c41d76ec81bb2723d646fde4c148e7cc3402f4980d2ade95cb9c84f9`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-handle-l1-1-0.dll`
- `8f105771b236dbcb859de271f0a6822ce1cb79c36988dd42c9e3f6f55c5f7eb9`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-heap-l1-1-0.dll`
- `53b25e753ca785bf8b695d89dde5818a318890211dc992a89146f16658f0b606`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-interlocked-l1-1-0.dll`
- `a9b13a1cd1b8c19b0c6b4afcd5bb0dd29c0e2288231ac9e6db8510094ce68ba6`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-kernel32-legacy-l1-1-1.dll`
- `7f39ba298b41e4963047341288cab36b6a241835ee11ba4ad70f44dacd40906c`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-libraryloader-l1-1-0.dll`
- `6ee44dd0d8510dc024c9f7c79b1b9fa88c987b26b6beb6653ddd11751c34e5dc`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-localization-l1-2-0.dll`
- `0512a35316ec9180437f86696a84c5c06a7e4e82e050055a656e5bf9fca206f9`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-memory-l1-1-0.dll`
- `c05f1fffe3b5a2738ea54ce9485cca026fb9635f982626fba1e1dcc531897273`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-namedpipe-l1-1-0.dll`
- `c4eca98c3c67b6395d5b005b00ac1eb0318b86b23aa71035a44c2b1602befba9`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-processenvironment-l1-1-0.dll`
- `5ccb89e93d67bc3288d4e84649c5346e66e15e3d7cd65d989daf3f4cb584be9a`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-processthreads-l1-1-0.dll`
- `4ad565a8ba3ef0ea8ab87221ad11f83ee0bc844ce236607958406663b407333e`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-processthreads-l1-1-1.dll`
- `7809160932f44e59b021699f5bc68799eb7293ee1fa926d6fcca3c3445302e61`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-profile-l1-1-0.dll`
- `9dc1e91e71c7c054854bd1487cb4e6946d82c9f463430f1c4e8d1471005172b1`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-rtlsupport-l1-1-0.dll`
- `60fc31d2a0c634412f529dba76af3b9bf991352877c6dae528186d3935704cfd`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-string-l1-1-0.dll`
- `3a72b4f29f39a265d32ad12f0ce15dbf60129c840e10d84d427829ede45e78ad`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-synch-l1-1-0.dll`
- `efc1e4460984a73cf47a3def033af1c8f3b1dbc1a56cd27781d3aacf3e3330cb`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-synch-l1-2-0.dll`
- `b203d862ddef1dd62bf623fc866c7f7a9c317c1c2ae30d1f52cb41f955b5698e`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-sysinfo-l1-1-0.dll`
- `2703635d835396afd0f138d7c73751afe7e33a24f4225d08c1690b0a371932c0`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-sysinfo-l1-2-0.dll`
- `33f4fddc181066fce06b2227bded813f95e94ed1f3d785e982c6b6b56c510c57`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-timezone-l1-1-0.dll`
- `6eda016742a6171205a387a14b3c0b331841567740376f56768f8c151724207d`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-core-util-l1-1-0.dll`
- `b762061b688aae679afe788904d2c9970f74a7dac98f3b42463d08f25e483d3f`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-conio-l1-1-0.dll`
- `ebb2ae5535a64f65daeab8235585114fc9dd2cf1a49f5852d446250b998b6ae4`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-convert-l1-1-0.dll`
- `17d63275d00bdd8670422b95bd264c532998e0a1b041079e54fce4b6b7a55819`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-environment-l1-1-0.dll`
- `9a9e2a65a281644e368d0f272b95ba5f6b445d1c35910d06056c5ebeb77402db`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-filesystem-l1-1-0.dll`
- `bab9ac3ec83e380ae51e4295ef3bf2c738627812d3a49d1e713661abbc8dc57a`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-heap-l1-1-0.dll`
- `bd14c67ea28e21d6257ad780a37122c9b5773f69e693f5db6bffaee4d839526e`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-locale-l1-1-0.dll`
- `606d66d82db562ea7979179d06486a0f94d079941d26b80a1e2c49d29959df6f`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-math-l1-1-0.dll`
- `95f49efbe8107786733fa7c474025cf3fee0ac632f240367b296c736d06572aa`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-multibyte-l1-1-0.dll`
- `1bc82bed6143d2bf1b6b08a7809f4a5e29317d6fddd338a7da3c0223522e4bbf`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-private-l1-1-0.dll`
- `f6156b1020380ec4f0e48577ebedaaef5fb1ab1f337d8b4e72e6a33a7567a9cc`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-process-l1-1-0.dll`
- `c5902934d026d7e15fbe9917d474f3322846a41a25e66f4b2b1f758801879f4b`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-runtime-l1-1-0.dll`
- `a9c5a153d8c0286f9b41a2b1c65854ad9e6471b8755b7de87bae4470e60bcab6`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-stdio-l1-1-0.dll`
- `25b8f83a7767211b11132775a0e27a45aa4ec8ab4e6572599f9c172ae3606b40`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-string-l1-1-0.dll`
- `7c7f6393f06de11750adb09cc5698ae55cd9fb27b2e51e207286feb1b5b2b156`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-time-l1-1-0.dll`
- `d8ba5f17b9ffcbf3aeaf3fa1da226832d2fa90f81acce0cd669464e76ce434ac`  `bin/generalization/jdk-21.0.12.1+1/bin/api-ms-win-crt-utility-l1-1-0.dll`
- `92951d2477164e9d53f660bfcadfd2bf0a35b452f58cec082dc2fb93451dbe88`  `bin/generalization/jdk-21.0.12.1+1/bin/attach.dll`
- `6fd29b7267eb02df00229b44f34d561be1e56b313ada754bcea1acf7c3562a83`  `bin/generalization/jdk-21.0.12.1+1/bin/awt.dll`
- `3c47a691cbc2fa3a89d6ee61acdb3a69907721e5b0acb0321744c17d2adac226`  `bin/generalization/jdk-21.0.12.1+1/bin/dt_shmem.dll`
- `4ac7c5a219c0e6ffe580575d3938ef66c5e588f53a857e242cd7aa805b69c80b`  `bin/generalization/jdk-21.0.12.1+1/bin/dt_socket.dll`
- `eb6b8f2f52c0488c4d00a88d9f6bc61ab665808d5b1549c0960a60ae1ead3390`  `bin/generalization/jdk-21.0.12.1+1/bin/extnet.dll`
- `2cd3b5ebc97aff79685c34024ef13a3880aed9c26bb9d82c673ee765b134b6a5`  `bin/generalization/jdk-21.0.12.1+1/bin/fontmanager.dll`
- `213a2ed1d5130ce40b5d3b8495fd41d9841c844da1116fd3a2b4eab85259c20c`  `bin/generalization/jdk-21.0.12.1+1/bin/freetype.dll`
- `06254d6d72a98f8222adc61223a2421da32862918e6ce7f3217fb169d8bc8d25`  `bin/generalization/jdk-21.0.12.1+1/bin/instrument.dll`
- `2087c0a7f3e13baa2dff6e964973447ae6b0ca1e2b4a4dbad17d921f26d30354`  `bin/generalization/jdk-21.0.12.1+1/bin/j2gss.dll`
- `75072bd82258964cdcd103a423f2ad414fd471f6576af4355b1e713d1a72ae80`  `bin/generalization/jdk-21.0.12.1+1/bin/j2pcsc.dll`
- `4e534b0d5cb52f0ad3757a588e0c61a9175022d21d11b4b92beabf0454d77576`  `bin/generalization/jdk-21.0.12.1+1/bin/j2pkcs11.dll`
- `d68238ac8c72ef8ec17b09da2cd3f5285f7a00533477c27eea7ec1c29d42dc9a`  `bin/generalization/jdk-21.0.12.1+1/bin/jaas.dll`
- `4403b7e0e46e907db3ba70489756aba52e9b72de1392580fea7f6ab0837d3096`  `bin/generalization/jdk-21.0.12.1+1/bin/jabswitch.exe`
- `d229e7c8a41921e44daa8b1964895c6ac8ac41344ea157b1d035072c565032cd`  `bin/generalization/jdk-21.0.12.1+1/bin/jaccessinspector.exe`
- `24c4a09d2b06da7e56685df101389473baacaad7bccf1e5e84128b80919ff894`  `bin/generalization/jdk-21.0.12.1+1/bin/jaccesswalker.exe`
- `63252d4bf24035ddba3d98fd23e0a2a414d5e860a49f180ce4ac35f52febe043`  `bin/generalization/jdk-21.0.12.1+1/bin/jar.exe`
- `865248d9f2940455bc836889ddc2edfdf68a0c663fba8b01024a50778cd245e4`  `bin/generalization/jdk-21.0.12.1+1/bin/jarsigner.exe`
- `9b484b6a703e890292ab3bdb43c81c17eac1eecce585a28205d32ae42c3bc049`  `bin/generalization/jdk-21.0.12.1+1/bin/java.dll`
- `82051fdab26319d77d20cc0065045d05ec00b3e3d05f44935d7c06b96b621d55`  `bin/generalization/jdk-21.0.12.1+1/bin/java.exe`
- `6491c705845e53841db92658040c2e4c40e0fa1486ea357e412bf1091e767b87`  `bin/generalization/jdk-21.0.12.1+1/bin/javaaccessbridge.dll`
- `00f7c6f9ec89ebba4bb96cf8760403cccf1268df2eae8685900ba38e58a7aff9`  `bin/generalization/jdk-21.0.12.1+1/bin/javac.exe`
- `e58691e911585470f36a980e6442566f1cbca142240ff2397aa784b559017eb0`  `bin/generalization/jdk-21.0.12.1+1/bin/javadoc.exe`
- `bc96c9e9e4a3eb21b06a5f3107229d411415ecc686c10219421626f8a1871147`  `bin/generalization/jdk-21.0.12.1+1/bin/javajpeg.dll`
- `edc73c5ef6d21a5058e3e4594f6907a7d6c9813ed3ddb55806f708debfcf8488`  `bin/generalization/jdk-21.0.12.1+1/bin/javap.exe`
- `0d0448174d811b743faed2c1600b6174f33e65506e196b177effe0cd7a04cdb2`  `bin/generalization/jdk-21.0.12.1+1/bin/javaw.exe`
- `a3a888fed957b49b88cd42ceea4335123ea4ca50fcfaf60f88ab961bdbd6289e`  `bin/generalization/jdk-21.0.12.1+1/bin/jawt.dll`
- `19f307f8f957ee26a87a0de32dd62f6c13392f49dc8f982e36f84e767bc1db52`  `bin/generalization/jdk-21.0.12.1+1/bin/jcmd.exe`
- `031a79e696ccccc5cdd4d101efeec2a6f8e4ce3a9dd3e038ab9328eb8d2f8b9d`  `bin/generalization/jdk-21.0.12.1+1/bin/jconsole.exe`
- `e04637a948a1e95c466f46ddbceeb20d1fe04558d825df612dc11fca2372b54e`  `bin/generalization/jdk-21.0.12.1+1/bin/jdb.exe`
- `a20708e4a224bd2a484155fc7b7487a7159168e4fef3bb1367008a65a386ca1e`  `bin/generalization/jdk-21.0.12.1+1/bin/jdeprscan.exe`
- `02104296d10532b89efbf70d150bb859024e6d1ce192d6f2809602f54b56e685`  `bin/generalization/jdk-21.0.12.1+1/bin/jdeps.exe`
- `195e07cbdc22d8667c00978de0e669b34639287383b3a5c3467d6343560c66ba`  `bin/generalization/jdk-21.0.12.1+1/bin/jdwp.dll`
- `5c7e26a40b605745eda687bac35686c6c2e601a75ea93b66aec48ea92dc94da6`  `bin/generalization/jdk-21.0.12.1+1/bin/jfr.exe`
- `b6b5aafced52ffe5248289551d2d6e0a90586ecb29a2c044bbaa89e1197e4541`  `bin/generalization/jdk-21.0.12.1+1/bin/jhsdb.exe`
- `8123408896077c9fcdcb0d5809d5bdf6e96a3e3a1a15bec2dc7432f68b42acf4`  `bin/generalization/jdk-21.0.12.1+1/bin/jimage.dll`
- `1ca30e035c7558839b616b1e66116e11a2b400ce5067adc66a5e344ead3fc5b9`  `bin/generalization/jdk-21.0.12.1+1/bin/jimage.exe`
- `7148a90893ac63cfa86552c33326f8bfbc9e11c4c00c947f58f276fcc4d78362`  `bin/generalization/jdk-21.0.12.1+1/bin/jinfo.exe`
- `1e189c727f043e924cb8779b673702ba836faa7c9e752e2743b69cde70a2c1fb`  `bin/generalization/jdk-21.0.12.1+1/bin/jli.dll`
- `0d79a070f8626fdd6cdf3d05410726012eadc09d9ab841cadc966477bff431db`  `bin/generalization/jdk-21.0.12.1+1/bin/jlink.exe`
- `55ffe2f346509ffe4e7041d3e37340adeb908f354b49243b8d4432572b097c64`  `bin/generalization/jdk-21.0.12.1+1/bin/jmap.exe`
- `8e2a7de57160901a51c673268384541345de0df5acdfaadf471946d189b5129a`  `bin/generalization/jdk-21.0.12.1+1/bin/jmod.exe`
- `007390513bc14073994b9dfe57046434c0cc9a513642a2f80cbb5f9355b94460`  `bin/generalization/jdk-21.0.12.1+1/bin/jpackage.dll`
- `afd944cbf952a461d283a7df7714c12cdc05fd29441eae04526966d71357e9a2`  `bin/generalization/jdk-21.0.12.1+1/bin/jpackage.exe`
- `8dbe753d7c98b388e4a999065d6fdf1aa630e58493791a06037b13ad877defbf`  `bin/generalization/jdk-21.0.12.1+1/bin/jps.exe`
- `5e8b3d23c6852bd12b3f1e484cd41695404caaa1433bf9236a45f465da9067f4`  `bin/generalization/jdk-21.0.12.1+1/bin/jrunscript.exe`
- `5a16da65c3f217241fb3ca70726f593bc7be9c78127731413af6de57d1e6a932`  `bin/generalization/jdk-21.0.12.1+1/bin/jshell.exe`
- `a0fa7096c74f91b8213eecd457422f3a4e5ec8f8a6e3fccc9b1a0be1036fde5f`  `bin/generalization/jdk-21.0.12.1+1/bin/jsound.dll`
- `e0318ba73363917a44f466da804c9db80c594a26ed1bb4b90b36e47c2ac22e57`  `bin/generalization/jdk-21.0.12.1+1/bin/jstack.exe`
- `d569e956aee447b70a5276e9e44b72cecba70e1ac779b650e743e141778547f8`  `bin/generalization/jdk-21.0.12.1+1/bin/jstat.exe`
- `03b9736c3fd8a1609aa1897dd511a1774e70f9d10122ae1b9dc47a4f2e317106`  `bin/generalization/jdk-21.0.12.1+1/bin/jstatd.exe`
- `83c96f64abf06a065a33a0419ca43e413f166bddcbad713cbf526805c87fa107`  `bin/generalization/jdk-21.0.12.1+1/bin/jsvml.dll`
- `549cdc4f3e15f4e535e6d12cbb70489adb3596ef05e81a6dd62b5d95d7e949ca`  `bin/generalization/jdk-21.0.12.1+1/bin/jwebserver.exe`
- `3576ba983634afd753814ea089a98be965ac5da270b3b83deb1e9a5ac53fa3d7`  `bin/generalization/jdk-21.0.12.1+1/bin/keytool.exe`
- `6338e98bafc24247d838deb544acb37384fba2fd71dacd70eb693668849a8e2b`  `bin/generalization/jdk-21.0.12.1+1/bin/kinit.exe`
- `8b05722ec514487b3caf338b38f8c27f5010afac6ee389bf6f93ec1dc1a632ad`  `bin/generalization/jdk-21.0.12.1+1/bin/klist.exe`
- `1967793ed0979cda5803659ce25ccbe38242d178a5205e145203da33e22a0537`  `bin/generalization/jdk-21.0.12.1+1/bin/ktab.exe`
- `ece80974504b25cfabd0d3a1860db0f17935d83a6010511dd47b21f0f0353d46`  `bin/generalization/jdk-21.0.12.1+1/bin/lcms.dll`
- `b8429d14467ee0337b20f9059eadb034e2f97fcbb881e8a3c0ab59a36ff04cd8`  `bin/generalization/jdk-21.0.12.1+1/bin/le.dll`
- `06c6f86f3e731f88361d7e670f84a80761a8fc80c6eebac914e8072e706c4385`  `bin/generalization/jdk-21.0.12.1+1/bin/management.dll`
- `2ac35d1345aaeb5db9baeb164b083261f1944494205c444260f6e5f659473c95`  `bin/generalization/jdk-21.0.12.1+1/bin/management_agent.dll`
- `61fcd7c911af730d6bca121d91673fb57c8db077a9e29b6cdb6fa2770c11d22a`  `bin/generalization/jdk-21.0.12.1+1/bin/management_ext.dll`
- `4dcd756b9d4405ada3786d69a1d2bdc9fc9ce770c8401d0a382d178fdcabc4e1`  `bin/generalization/jdk-21.0.12.1+1/bin/mlib_image.dll`
- `a4c2229bdc2a2a630acdc095b4d86008e5c3e3bc7773174354f3da4f5beb9cde`  `bin/generalization/jdk-21.0.12.1+1/bin/msvcp140.dll`
- `da8fe694d71e287cb1c74d478d8854f55d6ea26aba17e58050b772a0a7ef79d8`  `bin/generalization/jdk-21.0.12.1+1/bin/net.dll`
- `50cddbcea627390ed9dee80da7ca9d1942c4c7b1e3f138276693d487a6dd589c`  `bin/generalization/jdk-21.0.12.1+1/bin/nio.dll`
- `3c64fee48d8cf5d4ac97bbc10d335b2aae48ac539a1434d740d7a1d51e840e4c`  `bin/generalization/jdk-21.0.12.1+1/bin/prefs.dll`
- `0849b3bf75c35be042dff76ce530e2f153b649a1202f50d575238648f2bde4ae`  `bin/generalization/jdk-21.0.12.1+1/bin/rmi.dll`
- `95ba7eb6775feb0d49e59c4a39d6da9309809acfbcc97d131b1b0af88266379d`  `bin/generalization/jdk-21.0.12.1+1/bin/rmiregistry.exe`
- `20393cc4393866b3d2e334906ccb1ae40f9d33a6fda408720cde9b1a43bfb068`  `bin/generalization/jdk-21.0.12.1+1/bin/saproc.dll`
- `8b0a0122dcf2fef186706ae3f3762c922104f09becc1ce74d2c31ca8cdb7ec52`  `bin/generalization/jdk-21.0.12.1+1/bin/serialver.exe`
- `2ea07da8be0e6b89b2c56b349883df41353378a9c123b90cc38ebc57cc7955e6`  `bin/generalization/jdk-21.0.12.1+1/bin/server/classes.jsa`
- `f9ef414b5af50b5f3828d60ffef27910db0b8ecd16b89640af4d73a7f63b4f0b`  `bin/generalization/jdk-21.0.12.1+1/bin/server/classes_nocoops.jsa`
- `3df13bd73c7dbeef26693cef664b4ede84649720f7a12f0203215a65656d25f4`  `bin/generalization/jdk-21.0.12.1+1/bin/server/jvm.dll`
- `d5b0ccbc32429dbb1617d88bbd4adb471a4debd5a9dd3967b8b7484e6fc9214a`  `bin/generalization/jdk-21.0.12.1+1/bin/splashscreen.dll`
- `45ff75813743beda329b799961ade6244a4fd56365fa27582127327d01542a79`  `bin/generalization/jdk-21.0.12.1+1/bin/sspi_bridge.dll`
- `31f542d6ea0856fc2b3919aa76048d2e1f6e04f7bff6f70cbeda89faf5d931c7`  `bin/generalization/jdk-21.0.12.1+1/bin/sunmscapi.dll`
- `0702917a944d3b779881b3c5da4cf50a6c94903a60883eac868696723e551221`  `bin/generalization/jdk-21.0.12.1+1/bin/syslookup.dll`
- `2e5fb14b7bf8540278f3614a12f0226e56a7cc9e64b81cbd976c6fcf2f71cbfb`  `bin/generalization/jdk-21.0.12.1+1/bin/ucrtbase.dll`
- `02c6aa0e6e624411a9f19b0360a7865ab15908e26024510e5c38a9c08362c35a`  `bin/generalization/jdk-21.0.12.1+1/bin/vcruntime140.dll`
- `7dd9aa02e271c68ca6d5f18d651d23a15d7259715af43326578f7dde27f37637`  `bin/generalization/jdk-21.0.12.1+1/bin/vcruntime140_1.dll`
- `dd1d4af0d2c1348f29a143c358922be9d071addbf0d103d15910332cf3b74a58`  `bin/generalization/jdk-21.0.12.1+1/bin/verify.dll`
- `0977602efe64e68a6b1a5119795dad4f18f4e961441572fd015037686a8ea5f5`  `bin/generalization/jdk-21.0.12.1+1/bin/w2k_lsa_auth.dll`
- `e66506b4e3d4614ae3c9f9ee3c6b60cddc110a5439d80e5d4a58f4c5ed76fd95`  `bin/generalization/jdk-21.0.12.1+1/bin/windowsaccessbridge-64.dll`
- `a9ae352e10a098403f497ea69442818be1148a737792a21a7d568a4836d2dc06`  `bin/generalization/jdk-21.0.12.1+1/bin/zip.dll`
- `7d95c49465d0c836d608d02856d3b097934dfb5dc4bd2279affaf337d045b708`  `bin/generalization/jdk-21.0.12.1+1/conf/jaxp.properties`
- `b62d2733ab99556b108a1951d894c5a8d76b1ac7a00c02c388f9eb9be046c56f`  `bin/generalization/jdk-21.0.12.1+1/conf/logging.properties`
- `0c25d26ee212ca1e8c33f67c3c460d43fe849c3a1d23dbe341148517602b280c`  `bin/generalization/jdk-21.0.12.1+1/conf/management/jmxremote.access`
- `0273b6a6b9e20e6ce54c5aee70164028e0395063b2b7d39060a40b6495543dbf`  `bin/generalization/jdk-21.0.12.1+1/conf/management/jmxremote.password.template`
- `07dffdd85b01c19bf46ca320a699aba48dd6b01043eb0bd6a9528c7993312bad`  `bin/generalization/jdk-21.0.12.1+1/conf/management/management.properties`
- `56dd1f6095c189c1052f6baa32e457efc09de4832e19cdb82bb236dc8abfee9f`  `bin/generalization/jdk-21.0.12.1+1/conf/net.properties`
- `d51bcab7ed301caeff3779a5e777e6019864cecee5e2abc102ef991b0de77af2`  `bin/generalization/jdk-21.0.12.1+1/conf/security/java.policy`
- `7eff0eef66774d0c6a07f6c69fae02d8a7dff9b2ef3d7751af9af87a4dda33e6`  `bin/generalization/jdk-21.0.12.1+1/conf/security/java.security`
- `6da0747334b0fea7592fd92614b2bbc8b126535e129b1fee483774d914e98eb5`  `bin/generalization/jdk-21.0.12.1+1/conf/security/policy/README.txt`
- `758b930a526fc670ab7537f8c26321527050a31f5f42149a2dda623c56a0a1a9`  `bin/generalization/jdk-21.0.12.1+1/conf/security/policy/limited/default_US_export.policy`
- `2b2627548e61316150d47ffc3e6cad465ca05b3cccd4785eb7d21aa7baa0f441`  `bin/generalization/jdk-21.0.12.1+1/conf/security/policy/limited/default_local.policy`
- `8c3d7648abcd95a272ce12db870082937f4d7f6878d730d83cb7fbb31eb8b2c9`  `bin/generalization/jdk-21.0.12.1+1/conf/security/policy/limited/exempt_local.policy`
- `758b930a526fc670ab7537f8c26321527050a31f5f42149a2dda623c56a0a1a9`  `bin/generalization/jdk-21.0.12.1+1/conf/security/policy/unlimited/default_US_export.policy`
- `8d8a318e6d90dfd7e26612d2b6385aa704f686ca6134c551f8928418d92b851a`  `bin/generalization/jdk-21.0.12.1+1/conf/security/policy/unlimited/default_local.policy`
- `299c2360b6155eb28990ec49cd21753f97e43442fe8fab03e04f3e213df43a66`  `bin/generalization/jdk-21.0.12.1+1/conf/sound.properties`
- `7056263197c68eb8493f53d88020aa550985e64816afd776e509d6bf8cf0b4a0`  `bin/generalization/jdk-21.0.12.1+1/include/classfile_constants.h`
- `85101d07928a589accfef9d7c261850faa8d5afc8ef262af7ec9734008f6f2f5`  `bin/generalization/jdk-21.0.12.1+1/include/jawt.h`
- `c42256f8596cbf3b59aa25be54bbf2ece47a5dee75d4e6153791dc5620cff2c8`  `bin/generalization/jdk-21.0.12.1+1/include/jdwpTransport.h`
- `99e64ebbe749e6df284f852f11b3c73f6ea97baf15120428f40f887fe0616e61`  `bin/generalization/jdk-21.0.12.1+1/include/jni.h`
- `6b7891bc1ec282a10269598e73ea3571ec2e83f9d0ac7a29b77eacae1015070e`  `bin/generalization/jdk-21.0.12.1+1/include/jvmti.h`
- `6ee3e52d24bdb4f4d0312dfbab3d47bd524cbdac5540a4d790cac0620c59b3c8`  `bin/generalization/jdk-21.0.12.1+1/include/jvmticmlr.h`
- `92ecc9dc75d30ebdd6ba6da032f567586d258cdd69ccb04621327b9d388f814f`  `bin/generalization/jdk-21.0.12.1+1/include/win32/bridge/AccessBridgeCallbacks.h`
- `77c5684dbf00c074ce36c6ca0b5a89e82a503bd23e09f29ec8d57db9239a6565`  `bin/generalization/jdk-21.0.12.1+1/include/win32/bridge/AccessBridgeCalls.h`
- `08f29e6dfc01d32726605d29ff9111b3132dbed0ddecafe4480fcb2b8201b0af`  `bin/generalization/jdk-21.0.12.1+1/include/win32/bridge/AccessBridgePackages.h`
- `9c0f6287252019b77a1bac18b92f28153ad46709423fe2cc9e1fa5d16bca38e3`  `bin/generalization/jdk-21.0.12.1+1/include/win32/jawt_md.h`
- `3cacac1e4802ec246ea7c0c6772d4ac40c9f7255d4df095cfffe601137689771`  `bin/generalization/jdk-21.0.12.1+1/include/win32/jni_md.h`
- `a5fe55cb4b320db01a27253ef669f17dd565a6878abded0d1974ae7991c0bf71`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.base.jmod`
- `692def2db5f3088032453f022046edb440d3494965f487257e5e20af7ce02c1a`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.compiler.jmod`
- `5433957bd70f7310d6d9cacaaa5e628ed96deae30a5a91fe3e127801424a8d7f`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.datatransfer.jmod`
- `e83e7666c651e4aa6a8963cab5ac0949fc9653f6f1da4dcf7d35183afc527f8d`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.desktop.jmod`
- `82e1b2783ea02affd2af2d4efef12f89ab3135e668f935d48e6074031e81d964`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.instrument.jmod`
- `d5b5c495335b26405dfa143f6341b9bac4aa1e458ff380b5bff94722fc44d8ae`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.logging.jmod`
- `56251d069e46eb9c2f2f0bd529d2d105c90f83258bc3e3675f1b765e0884dabf`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.management.jmod`
- `7e810378c26f53bdce1b6bb1da1263958ab086a038ba0f9bc202a15cf6524ff8`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.management.rmi.jmod`
- `e5b0cfe4b4285363665fc745c1fb135a99a3eff7abb85b97f612473fe5114d80`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.naming.jmod`
- `8dbceeef4f22838105a845d4cc9b4361369caef5687e22a2707ddb6734200ae6`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.net.http.jmod`
- `0b4937260798aec963b955ad26c43b12e19b7354975f778600d75e1cd00765dc`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.prefs.jmod`
- `275f4a0aa82521c39142c499fc043f85b93d4ff9ab301b1e287d0d2812612839`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.rmi.jmod`
- `e36d4ee580482c4756e9006a9e70ac9a91921dfb14f2b7513b32de501d263528`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.scripting.jmod`
- `da46b485526dd6787729f01031d7ddd8b4157353d36b7fa1a8f56d8d15311086`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.se.jmod`
- `4846f15c553a79d1af36aee279b52e3a851db7e5fdf8fc7db19baef3562213c6`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.security.jgss.jmod`
- `5942e4ad2e86499f59d5dc6128e71685e56d3317a8c783a4c4efad8f97cdc833`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.security.sasl.jmod`
- `e98c016595e6c5b36129946ebf72ef846a67535f5a25a5c5ef80d43e836d858a`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.smartcardio.jmod`
- `d15e0fbd3eca4b0b8c0011f94585fe7902d5310cc5dd27dd2b81e544e1875372`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.sql.jmod`
- `d40991b09406101c01abec4246941e71e061eedc2b1547bc6471d62ffdecb1ea`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.sql.rowset.jmod`
- `47b9d14e189b74010361be9a87f19541bc0968629e50d0929ea7bb1a0dad0abb`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.transaction.xa.jmod`
- `bc1ea82b0f581fe4b922a6635f636ab15685bdd9469d8699e25c357a44a2f79b`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.xml.crypto.jmod`
- `1a395ae8faf3702161921ba50fd99890e7147964425954642a241f0be8f553c1`  `bin/generalization/jdk-21.0.12.1+1/jmods/java.xml.jmod`
- `fcfed4bf471a65f4e06f24d3d7722809a35aa07baa17bd8da7843e40e55d5e92`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.accessibility.jmod`
- `23fbbbb8e4f04f1196dc4b90af1f703ff774e4135cbda430b504d354106de1f4`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.attach.jmod`
- `368eba9169dc7cc383c1d107f5a8c5adf9baaf995310129d6c5c5b3795afb06d`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.charsets.jmod`
- `c39382ef070f43a12a7ea39da6186377c1f1065cfb1692b2acdd3d54b2016c2b`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.compiler.jmod`
- `ba746f37ffda0e6fbde59301f454b759318d76d1e520f8fdd76b9de403d17433`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.crypto.cryptoki.jmod`
- `edfe1f1d09d470d407a46cc790e45e60d613515836b8632ecc17794f28ac475a`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.crypto.ec.jmod`
- `240327d6341df5d983352aab754093ad27f5b054be76ea48d635b8e877209d19`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.crypto.mscapi.jmod`
- `a4c3b77f37f2ac75bf4e714cde552e32b7cafbfeaa255bf253f4dcc316edd69e`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.dynalink.jmod`
- `1fac2c338a3c96966cb3d9590cd69354c9088e880ce34c5c3994f561eb74d117`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.editpad.jmod`
- `2b01ad1a27af2ce8c087d0529d730015027d2d10657fa966364b87f4bf195b79`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.hotspot.agent.jmod`
- `85f3543f3e5e08a01c9c0ad4d1ad26507b2d72758bd1de5a4d9d8a564cadeabd`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.httpserver.jmod`
- `008f298f9f0c56d240000d389d5f48e4c2eb657a4b3b1cf86f9a9b142303322d`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.incubator.vector.jmod`
- `83febb69d06d1afaf46203ec192d7618fd81b97ebf292fd489770608b41947dc`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.internal.ed.jmod`
- `40ff522e56f9ae7642441fb4d00450d748e6303ce8ada5ab7f194acdecafb516`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.internal.jvmstat.jmod`
- `e0708d352fa67161b9be90d39dd807720a5e723f524f0997e729e771d84af1ea`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.internal.le.jmod`
- `e6cc6232aaa93b391991ad4cdb6d184f4b38369915d35ea4c5606ea648e4dc36`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.internal.opt.jmod`
- `ebc0e762e9d443e85bb1830952f71f8fa5dc6638da8d46844b8602bbff04a042`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.internal.vm.ci.jmod`
- `3c322e6441ee61af31fce3bbbc1d086a3a2a74add4478cc5dacd78ba1d7db16f`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.internal.vm.compiler.jmod`
- `8670242fb38105b7e023f7ab5112ce336b72f74c3b45906a80c798b25b9f5f19`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.internal.vm.compiler.management.jmod`
- `58b1ea259aa2c1e2c14c639c87fce05b17feb0b4e6208cfeca5ce8090feda818`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jartool.jmod`
- `b9fde43503a71df1cfd83cdb5a23884f69182792dcbd020797cb528e115bf0ce`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.javadoc.jmod`
- `c21cc151e355b467136e03ee7eb96d8ae17b530501730dcd0fac612b5aff0e18`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jcmd.jmod`
- `9af20a970dadb494c5ebad9c8da5c49d7e05b43b5d3def41752ffc0ef177abad`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jconsole.jmod`
- `ec5fed8ec98613a920902df8c1ae3efc3e2cb2abc1112ecb6070ebb339ea53f2`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jdeps.jmod`
- `9187d1ab36d84c042491adb19d7189b8c85149c45a1bbe2484f0b8a8ffdfb066`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jdi.jmod`
- `7aeebbdeded17d2748ff7feed8b97e25ec5fa55477b93d927118f8d40120f0e4`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jdwp.agent.jmod`
- `c0c2c1c71878f206b50d2f469e4c551d508ec3eda6a14e67d5bf94e5a8c28571`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jfr.jmod`
- `382ae37255a7be57c96f9550c8b5b0e67e8a84d59e35c3cb269b738ef998acc5`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jlink.jmod`
- `a0196c1e9642dfbf74f303be21b5b8dd04d2d91af0afd4e9488b3a97364b4ec0`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jpackage.jmod`
- `b9da807392283f1cac9765ef20eea63ada889e65e47caa044a09547eb12af7c7`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jshell.jmod`
- `8e2b3f3dcc0d96461777dcafa11f922ba74b35de00e60529b5b04153b211d39a`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jsobject.jmod`
- `8aef4e88f1218057e5817ecf994c398462d332d107f3c03a2d3516406893aafa`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.jstatd.jmod`
- `6123e28411dc55970e2e6402b7df1b7d50eb65ff6364e2e7391149d608af472d`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.localedata.jmod`
- `ddd6b68fd79d3fe8f763ca31b588425d900b52eee24f4e961d62a38de57551a8`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.management.agent.jmod`
- `6507ccd3a42cb3015b95ffb74dee040d609cc35b5a1c823c683ae662857b4e5b`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.management.jfr.jmod`
- `b8cc54b1ef54a3ee4f15032d687c60e99ca5b5ad636feff1915d7b8a432635a5`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.management.jmod`
- `1fb747cb6a172a6ccc0d41c78a0e374cbda1f773ac982a3aeb949e63c23dd8d0`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.naming.dns.jmod`
- `09fa7d2e9af2cbe309afec2a952e7a38befe5dc6dbeb444da34a92af094b2978`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.naming.rmi.jmod`
- `c5494179dec5ee5937e2c18ccfa924d1466c77a0203c27f51f87a7af67e64546`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.net.jmod`
- `a3642c2187590529c9d2ef880e8a81b5d42c41f0d9ee9e500c13274e9f41b10e`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.nio.mapmode.jmod`
- `f6f5524522884672e1ba65c2f40d137bc01bf47237f6afb7900308bbea14b4ae`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.random.jmod`
- `ffb07bde854d3f04ca443f107d75ff5f8446cf0e7df123fb3cd5159f3c7d5c7c`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.sctp.jmod`
- `30a8bdfebea72697f6d9e6a15e9dfdc8c14a6a4729f03d5921b34903bd802692`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.security.auth.jmod`
- `7c595cb6dd0429d4f180830e0e3d9d18f9207e0942a1746444e9ebe66ce2d063`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.security.jgss.jmod`
- `b0e124a43889e6191582116bd70033b6ea001d867137fa5fdb91f7c12b342ae9`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.unsupported.desktop.jmod`
- `de0f22833b662ac3af181a85c06ba397a8437857c306e6d0007d81e24f359d38`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.unsupported.jmod`
- `2b4017be396e9131e15bc9214c332435fc93ad062d0115133e344fdee1ea0e97`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.xml.dom.jmod`
- `a00519bb143baf19aaba37d6c9593c72c5dbb0dacc7d7462c249637c864b2bc5`  `bin/generalization/jdk-21.0.12.1+1/jmods/jdk.zipfs.jmod`
- `a69bce275ba7a3570af6579cb0f55682cd75fedfcd49e0e8e9022270c447c916`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/ADDITIONAL_LICENSE_INFO`
- `75292f03bf23d3db7c985aecc191029b93883200721ed23ed34a2e601463df33`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/ASSEMBLY_EXCEPTION`
- `4b9abebc4338048a7c2dc184e9f800deb349366bdf28eb23c2677a77b4c87726`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/LICENSE`
- `45c6d4da48325edfbff3dcf71c704e504c057904435ed23c6d57046d551eb69d`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/aes.md`
- `683be15695bd248272d60f5b7fbe5e126a935ea6bf231a624a9aa164733e1d1d`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/asm.md`
- `bef40679922d6fdfb7e4ddb223ad6722300f6054ba737bbf6188d60fcec517f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/c-libutl.md`
- `19515e14a240e022640e95b61b5095127fa9690755950b4a2b0a02e783e08163`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/cldr.md`
- `1bf28459c6e0af9f3429f4f8becd1668d6544055f8df240277456bc4b3d8a752`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/icu.md`
- `861de1e4992a7d28f1de25c73cd50d26a94779ebd749c0643fecfa56442c3429`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/public_suffix.md`
- `5a792b5a74ad2a5f3d6a7ad8b7a841116e58a772c18bc6e392320a365b222c76`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/siphash.md`
- `6f72f10d166b2c2e8a395e03e734c5afc852b59aeca73ced124f6b9c96268d53`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/unicode.md`
- `3ac2992770080453b98c42afa807ba4b2c1738ef756b92a55c645f55e7df48f0`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/wepoll.md`
- `c9c70c36a1f0325e8788771906202d42ba6ab4205caca44ec0f665707e83226b`  `bin/generalization/jdk-21.0.12.1+1/legal/java.base/zlib.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.compiler/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.compiler/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.compiler/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.datatransfer/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.datatransfer/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.datatransfer/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/LICENSE`
- `04d61e3e8e71dd452ebe52008af5378d9f6640d14578aeb515dc5375973b0189`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/colorimaging.md`
- `553e804baecb7de7129d77c7259a6b70037d1893f1c600b41b35201695fb7758`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/freetype.md`
- `206aab89ec75968e48a6a1ed6df7d8b9bfb7aea12cbe4c9345d93e5d97460a25`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/giflib.md`
- `5ec7cba7f8e7fc3a089213140aab6fa1b3bd5bf8a91bf8bddb3b8d315fc5f7d0`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/harfbuzz.md`
- `c1dfb9719a71ad9f861f8728550542d681e25c8ef40e6393606e6e2a0c1d653a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/jpeg.md`
- `843f9f6fa9c3f8109fcf4d5fe74caf7f2ae8e9bcd92238e4aff2d428c932b24b`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/lcms.md`
- `f73afb394792f3aeecd959e89487603677a430e56b44eba596d8b572accfd540`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/libpng.md`
- `63f4e6f75caebbccb95d903fb43e46ac7111b3624d0a34f146b276d7d9e7b152`  `bin/generalization/jdk-21.0.12.1+1/legal/java.desktop/mesa3d.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.instrument/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.instrument/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.instrument/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.logging/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.logging/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.logging/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.management.rmi/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.management.rmi/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.management.rmi/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.management/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.management/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.management/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.naming/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.naming/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.naming/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.net.http/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.net.http/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.net.http/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.prefs/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.prefs/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.prefs/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.rmi/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.rmi/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.rmi/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.scripting/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.scripting/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.scripting/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.se/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.se/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.se/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.security.jgss/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.security.jgss/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.security.jgss/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.security.sasl/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.security.sasl/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.security.sasl/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.smartcardio/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.smartcardio/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.smartcardio/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.sql.rowset/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.sql.rowset/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.sql.rowset/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.sql/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.sql/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.sql/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.transaction.xa/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.transaction.xa/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.transaction.xa/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml.crypto/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml.crypto/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml.crypto/LICENSE`
- `d08690d25f660f145c73365d260ed522cd0aace8a0e1396706551b7a1ae8c9a3`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml.crypto/santuario.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml/LICENSE`
- `cd578186ad93de46cca29ec8ace2b11f9da751987f3f140e6095c528596cc8c1`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml/bcel.md`
- `6686e8877667584a3a7c07344baadca1a03e29f677162d87c3c0811e990d1148`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml/dom.md`
- `8d5dcfdf50455a3c34c753a98f21e953248af200415a9084e3f102cb6c43b8bf`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml/jcup.md`
- `c27eb875da4be683d4d7422be986e5e30f636ede31958ff1d39f9cd6109e7a00`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml/xalan.md`
- `4a6bf6b367193ee68681cb2d9fed30ffc5d62dd2d477bd62e0271707d71b3244`  `bin/generalization/jdk-21.0.12.1+1/legal/java.xml/xerces.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.accessibility/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.accessibility/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.accessibility/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.attach/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.attach/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.attach/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.charsets/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.charsets/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.charsets/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.compiler/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.compiler/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.compiler/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.cryptoki/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.cryptoki/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.cryptoki/LICENSE`
- `1f36ff1342a581142c858f90064e20633d43529ac82adb85345bd902a14e18b2`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.cryptoki/pkcs11cryptotoken.md`
- `371974b1fca3744a3892c7ee1fcc593b8b4281fc218f4cafd2f709e9df5fd81d`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.cryptoki/pkcs11wrapper.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.ec/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.ec/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.ec/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.mscapi/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.mscapi/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.crypto.mscapi/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.dynalink/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.dynalink/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.dynalink/LICENSE`
- `17312591cabee3ef6c34ed8897d92e4e361ba9cea41ec00dcd61a322a8fc2cdb`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.dynalink/dynalink.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.editpad/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.editpad/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.editpad/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.hotspot.agent/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.hotspot.agent/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.hotspot.agent/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.httpserver/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.httpserver/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.httpserver/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.incubator.vector/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.incubator.vector/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.incubator.vector/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.ed/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.ed/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.ed/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.jvmstat/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.jvmstat/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.jvmstat/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.le/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.le/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.le/LICENSE`
- `a6fb63a226b77b03cbd7559cce6cdc3e1ea8563af960b1dce2330c8e1dce1abf`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.le/jline.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.opt/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.opt/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.opt/LICENSE`
- `99bc67f93cf57d6d20e6047731c93fbb267d70fbdd4115d119e0f85c6efe5c05`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.opt/jopt-simple.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.ci/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.ci/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.ci/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.compiler.management/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.compiler.management/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.compiler.management/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.compiler/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.compiler/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.internal.vm.compiler/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jartool/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jartool/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jartool/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.javadoc/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.javadoc/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.javadoc/LICENSE`
- `b68f454c2bd58959c862d94bf0f16c3f78a2d537388ca060d354344db80ee695`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.javadoc/jquery.md`
- `7854d2d568992ae25ff65867bd9021d655f70670142f0796b29a3b0621f19530`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.javadoc/jqueryUI.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jcmd/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jcmd/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jcmd/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jconsole/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jconsole/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jconsole/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdeps/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdeps/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdeps/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdi/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdi/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdi/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdwp.agent/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdwp.agent/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jdwp.agent/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jfr/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jfr/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jfr/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jlink/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jlink/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jlink/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jpackage/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jpackage/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jpackage/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jshell/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jshell/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jshell/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jsobject/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jsobject/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jsobject/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jstatd/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jstatd/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.jstatd/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.localedata/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.localedata/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.localedata/LICENSE`
- `09972449731a1d1a0863af0384aeb7839f84cac74983c96856e6c305e31ed8b2`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.localedata/cldr.md`
- `c326144a2351c9608fa708b5d7d3c5a3da03e82b66479b128e9db4969539824a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.localedata/thaidict.md`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management.agent/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management.agent/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management.agent/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management.jfr/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management.jfr/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management.jfr/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.management/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.naming.dns/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.naming.dns/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.naming.dns/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.naming.rmi/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.naming.rmi/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.naming.rmi/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.net/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.net/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.net/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.nio.mapmode/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.nio.mapmode/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.nio.mapmode/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.random/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.random/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.random/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.sctp/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.sctp/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.sctp/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.security.auth/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.security.auth/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.security.auth/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.security.jgss/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.security.jgss/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.security.jgss/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.unsupported.desktop/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.unsupported.desktop/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.unsupported.desktop/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.unsupported/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.unsupported/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.unsupported/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.xml.dom/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.xml.dom/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.xml.dom/LICENSE`
- `ebf9777bd307ed789ceabf282a9aca168c391c7f48e15a60939352efb3ea33f9`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.zipfs/ADDITIONAL_LICENSE_INFO`
- `b998cda101e5a1ebcfb5ff9cddd76ed43a2f2169676592d428b7c0d780665f2a`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.zipfs/ASSEMBLY_EXCEPTION`
- `86e0516b888276a492b19f9a84f5a866ed36925fae1510b3a94a0b6213e69192`  `bin/generalization/jdk-21.0.12.1+1/legal/jdk.zipfs/LICENSE`
- `bee5fb44a1db38097034c3e6f85af40c76df6da815f75d5fe782ff0d296081c0`  `bin/generalization/jdk-21.0.12.1+1/lib/classlist`
- `5f45ad761db042b220fd22ba538151f962ac747c8e1e2f25ebdd8b77f62aff04`  `bin/generalization/jdk-21.0.12.1+1/lib/ct.sym`
- `c7e2e76b908cb6330823e698889943c162e9861a4575501cbb59c9b830158ab0`  `bin/generalization/jdk-21.0.12.1+1/lib/fontconfig.bfc`
- `74e6c464ae1e63983ada241869fdc66ef8c28cef403ee2301e0a90db9555b00c`  `bin/generalization/jdk-21.0.12.1+1/lib/fontconfig.properties.src`
- `af64af138d14b9fd0849d7f66ad6b529a4e5ec9c25476557bf6b3d65a8ac6884`  `bin/generalization/jdk-21.0.12.1+1/lib/jawt.lib`
- `4fed4b508c5f1b69578293df84f94a63752f86b4259d97e12884e3b2ec56ef50`  `bin/generalization/jdk-21.0.12.1+1/lib/jfr/default.jfc`
- `485fb90dbecee9a950c45247464351162b1eb0c35387fbb929f002c600807251`  `bin/generalization/jdk-21.0.12.1+1/lib/jfr/profile.jfc`
- `45fc41e80103af6ac9e9dd1403c9228271b77a9719f262e96a800486b9646952`  `bin/generalization/jdk-21.0.12.1+1/lib/jrt-fs.jar`
- `aa9efb969444c1484e29adecab55a122458090616e766b2f1230ef05bc3867e0`  `bin/generalization/jdk-21.0.12.1+1/lib/jvm.cfg`
- `58fbee0f29d91056c2b251a11627d1c090f19a877ec254eb02ecb02d1477d50a`  `bin/generalization/jdk-21.0.12.1+1/lib/jvm.lib`
- `cbcbf551210912063c7cb8384474d127568ffc8b4eef1ed57572ae7150591ec7`  `bin/generalization/jdk-21.0.12.1+1/lib/modules`
- `5a4bd51b969bf187ff86d94f4a71fdfbfa602762975fa3c73d264b4575f7c78f`  `bin/generalization/jdk-21.0.12.1+1/lib/psfont.properties.ja`
- `780c565d5af3ee6f68b887b75c041cdf46a0592f67012f12eeb691283e92630a`  `bin/generalization/jdk-21.0.12.1+1/lib/psfontj2d.properties`
- `583500b76965eb54b03493372989ab4d3426f85462d1db232c5ae6706a4d6c58`  `bin/generalization/jdk-21.0.12.1+1/lib/security/blocked.certs`
- `98d34a90fca2688ef5674862d2a484e09e5ca25d2f07c5d654aa28f1581f3419`  `bin/generalization/jdk-21.0.12.1+1/lib/security/cacerts`
- `69790a79bb9d4bef6b544c1878410bfa0c6a92171834c188772a0ba1ca8c0d95`  `bin/generalization/jdk-21.0.12.1+1/lib/security/default.policy`
- `37e71e43c8605f29b9072f152d0ea4708735cdf335a5b68b2bc2f875760806c3`  `bin/generalization/jdk-21.0.12.1+1/lib/security/public_suffix_list.dat`
- `af5fc30b6bd9dd4510ea61cfff56cdc2f7a1dd847430984a8d0116eaa3c4e580`  `bin/generalization/jdk-21.0.12.1+1/lib/src.zip`
- `5906b44e25a8a730131d7ba1beb5d15af27043f6536f1a169ca8a5d8b8bed8f8`  `bin/generalization/jdk-21.0.12.1+1/lib/tzdb.dat`
- `b41575b332809b37ad423bdca30c7c48cdef3d82f82fa9d534781a6f15d6a2ab`  `bin/generalization/jdk-21.0.12.1+1/lib/tzmappings`
- `07117c72ce033949c14878e07fbf2fe23f59a1f8c90a6d1351b5c89099847ce7`  `bin/generalization/jdk-21.0.12.1+1/release`
- `8e1afc0ef0e128be8f4514c60e3d9119263c0584f1ac149a4e3719b5009556c2`  `bin/generalization/sbom-convert.exe`
- `10721b959185940f7913f7e57ed512a9909a2b280df60ee7400235177608a76c`  `bin/generalization/sbom-utility.exe`
- `dc71719e9995813f44115f87d6753456685efb0d4cd691373be165b0bb6efa07`  `bin/generalization/syft.exe`
- `6f4de1e3cc078ea59cb7dde8a3dab25917a96e2820b26cb50a150408da0e8362`  `contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`
- `e8f78876ffeba76f1875a3b9a01f2ceafa2dba140544c32ebaa09087406eb539`  `contracts/commitments.toml`
- `0152c46447091a8275a75763d678f1e06901fc2cd2a7abebceccee41aeca1cb7`  `contracts/schema.md`
- `f0882a8eca596ec5ec7fb5557a1d390844c33c2420187fe3b8041b78b4f63c60`  `contracts/sources.toml`
- `e629d4f9a75f8955f14be848056c91247feefa182fbb6423163eb465d1abcf3b`  `docs/en/run.md`
- `98cce570bb10168de347b28c64c5f282c1db2acf63229ac58f8eff2ee87ab4e3`  `freeze_02.ps1`
- `5c2b72ef3ce080f6703e90505a0eee4d104433ae2debfd0f8f46d8868b1ab685`  `generalization/01-sampling.toml`
- `1ba962e7f94a13dd1ea9b293f10aacb3ae83a467a064cc7e133f42635accb363`  `generalization/02-candidates.toml`
- `2873b3cd09a9e650682d62be060e8e3618f5e5879985e72b2ac75937e94410d2`  `generalization/03-corpus.toml`
- `89d6871dea674f0dd1a92ffd2cc9e73ed74a5662aaa6973064a07a743dc66491`  `generalization/04-sources.toml`
- `c7a46bdc72de53426e260f10c3b957ea4957c363fa6f42a33db629adcf677c65`  `generalization/05-transformations.toml`
- `47824ee60cc5efa90f129c775a7c9d7332ebcaacb7468379f03239951f1bab11`  `generalization/PREDICTIONS.md`
- `001a52237a6949a10fda48b55fec6bd6d55b7aca5f6e7797b221884ee7eabcb8`  `generalization/sources/gen-cyclonedx-001a52237a69.cdx.json`
- `0fc86e0249efec42b553d629776dd88f363212d78a9a4a58822441e372f537f1`  `generalization/sources/gen-cyclonedx-0fc86e0249ef.cdx.json`
- `2e4891eb09928d6c0418a2f619399cb859c3a4aa6b9f7a7d0db3db31e941687f`  `generalization/sources/gen-cyclonedx-2e4891eb0992.cdx.json`
- `445136956fe117254a3da0ed8d1a3fc176585a1c8ba0bd9144fcae916f4d3ba2`  `generalization/sources/gen-cyclonedx-445136956fe1.cdx.json`
- `9179c4025ab445b794c41465daca70f1a70a04d241811e5644879a5e5c0fc767`  `generalization/sources/gen-cyclonedx-9179c4025ab4.cdx.json`
- `9dcf635da297fbc9ce6c2d4d78c6998ac1b00ef44514d771ad8663510ef444be`  `generalization/sources/gen-cyclonedx-9dcf635da297.cdx.json`
- `a2e17be40185098cd40d162f18e2744652a8118cb807093796173114372b6baa`  `generalization/sources/gen-cyclonedx-a2e17be40185.cdx.json`
- `f1c2f23c46450eaacf9e15df80d0992a2ae298ca431d29f79d712250f5f713be`  `generalization/sources/gen-cyclonedx-f1c2f23c4645.cdx.json`
- `0d278129197b0d726802f1f82ee2ee11993f2c342696089dea6a6a0e00b21b52`  `generalization/sources/gen-spdx-0d278129197b.spdx.json`
- `e38ee905f9c006755e4facc4691af57d4e637a7ef97c3468887c94e0c0f46060`  `generalization/sources/gen-spdx-e38ee905f9c0.spdx.json`
- `932232631210955172e375b61bd9bac31a462184136397ed6e7c171b7ffcb31f`  `known/known_violations.toml`
- `7df827ff6561d9b408956ac5b1d5c41e5003878a72b3f947fe7ae1fad246462f`  `pyproject.toml`
- `ab5e018252ee08d88e7631d023e6ef0c9db13f34eb51001821dfbfac729fb1a8`  `src/preservation_test/__init__.py`
- `a9e2d8ef9383cf2bfd25e04e614c609f506776504ca880472cf09ac90efc5052`  `src/preservation_test/evaluator/__init__.py`
- `8f4c8893bcb45447baad016d18e10658f7d40b23101e4da1d79bb4316073984d`  `src/preservation_test/evaluator/evaluate.py`
- `6aac22257a25db0464588310af2dfd7e109bb6e31c31c644bee335febfc2a03a`  `src/preservation_test/evaluator/formats.py`
- `3ff56f45fafca7097cc73171c16b1f8dddf0487ffbffeee436cddc05c90ff427`  `src/preservation_test/evaluator/purl_canonical.py`
- `18f11f82440ac3bdc3622eb6eeb3dd8435c7d6cf9f691c3b944b473464cb0e4a`  `src/preservation_test/fixtures/__init__.py`
- `acf1a8551920a6d7bcb484b6c89427aeeafa9b5d10cdd9beeeb42e021050bab8`  `src/preservation_test/fixtures/build_and_selftest.py`
- `bd0c9d92eaaf019f9eba274e8d80f6e3f1daab0ebf57b53092ef2a937b61aea0`  `src/preservation_test/generalization/__init__.py`
- `b3cea5f1ce57818b276ce03fb7089c8b361a5cf1b70f9f5de76d98be47c7c50b`  `src/preservation_test/generalization/execute_generalization.py`
- `0b21809e5139595c50b70d81021cb66cdce33cba25f46b42cce21bfc1c690707`  `src/preservation_test/generalization/freeze_02.py`
- `c2c94a94afd7e14459fe6a233b2636b018fc62e690464674c2afe586049546cb`  `src/preservation_test/generalization/models/__init__.py`
- `3fcd8c8117ad41e45f3b330603f9a82e1c732a6256b2ca647b1cde5f885d388f`  `src/preservation_test/generalization/models/candidate.py`
- `f1c873deddf59a19bc5b785e09b8be7d43fffe39d7330a90ae87840472e68f1f`  `src/preservation_test/generalization/models/candidate_screening.py`
- `e126d03ef878c077d98441918907744fc470e6f2217e0f9c7db601ff7c7a066f`  `src/preservation_test/generalization/p01_build_candidates.py`
- `7e41f52442fd8bfcb1ed96b1067f9c0880abc74895d075f3deaec37bfdee210a`  `src/preservation_test/generalization/p01_prepare_sampling_frame.py`
- `ba165e26af2cc0a5dbe2bdef672100721b289b1d2efc03a292f5d6f3db30b433`  `src/preservation_test/generalization/p02_build_corpus.py`
- `ae1b48c8038651d21aeabe362e692ba116f15144e69b76988480fb5a252012f8`  `src/preservation_test/generalization/p03_preserve_sources.py`
- `ae117d0bcea7ac01dcb8dcde90d1e8e937339b1f69c2e50e1aeba1deb7556c1b`  `src/preservation_test/generalization/p04_build_transformations.py`
- `3274bc654e3ece1a6d7be3a46f18467570d5c823a945d47fb3fc67c70c604296`  `src/preservation_test/generalization/smoke_generalization.py`
- `63c4f60254d130b671b450548681bf48851ce26f21fc6dbdee5ccc903f27eef9`  `src/preservation_test/generalization/utils/__init__.py`
- `ed056f5085e51835ee3a65558fb2668bc519cf8d2e8240c353ea4666c7e6be8c`  `src/preservation_test/generalization/utils/candidate_enumeration.py`
- `5ae880401dd5189cad768574eb4b0b54a41878e9539537090bb806193ebe3af8`  `src/preservation_test/generalization/utils/candidate_ids.py`
- `562e60490bc5aae1363ed60019fe085edf7244cf211dca88fb4c1e092ae6ae81`  `src/preservation_test/generalization/utils/candidate_inspection.py`
- `c31cf7edc0c27706313bc5f8211db0b82aa211f898ca60394076ad8680a6f11a`  `src/preservation_test/generalization/utils/candidate_sorting.py`
- `323988486d29359a90633e40ce139fb04b7ef839b11b0ee54d6ec6b1a4b97e23`  `src/preservation_test/generalization/utils/candidates_record.py`
- `13888189c342c1fd5348c2c854e6a01ab0cb9563cb6311de7a47b95f14e9b774`  `src/preservation_test/generalization/utils/exclusions.py`
- `21dccd7489a6a5be40b5e324c56b8ea036c047b2e3f536f2ac01ab8ec24f4a8e`  `src/preservation_test/generalization/utils/freeze_integrity.py`
- `322d634acada10f3cf8ab697862fc313510f95fef2dc9e3ea50e3da8754ddff1`  `src/preservation_test/generalization/utils/git_blobs.py`
- `b722d1ba0d7b6edb2f8bac5de72d4e59883a93617437a82f221e5784076b7fc2`  `src/preservation_test/generalization/utils/git_clone.py`
- `8674b36d5e7a1783d591c7e21522a238d56e603bb2afa8023cc5b271d6b28660`  `src/preservation_test/generalization/utils/hashing.py`
- `71ba2195bf3e52ec98cff9e9ce7b2d7010854e5f9f671615c539f5cc10ae63d3`  `src/preservation_test/generalization/utils/purl_inspection.py`
- `9ff5ec7d77a7e6d5e9490b0b17e37467bb866a524811401da9be066052b1cc83`  `src/preservation_test/generalization/utils/sampling_config.py`
- `9432635488565cfbc0d6eaa38104b13a1bc7ebaed988bac92eca867d43cb7c49`  `src/preservation_test/generalization/utils/screening.py`
- `4da10f452624f937e21fc2e1993299d3020ad94bd7f766ad335fe8058f0dfab7`  `src/preservation_test/generalization/utils/source_detection.py`
- `b2c2c6c02570dd6f65f9eb4d938e6b5efebc3f0ee41def62e800293570468f60`  `src/preservation_test/generalization/utils/subject_resolution.py`
- `4d5738a657bc539444ca50199f748ad4716d63cf152e1e4e3eceb11b8ae424da`  `src/preservation_test/generalization/utils/toml_writer.py`
- `5a48808431cd39d47c576e380bf6ed2f67dfc922c7ba8d601d257977927af3f1`  `src/preservation_test/generalization/utils/validation_exclusions.py`
- `0f91247e9ecf9e75e376f03c2b842cf17a55d22d8c11b62444bb273354ec260f`  `src/preservation_test/generalization/verification/verify_01_freeze_01.py`
- `d24e0a7c9da08ee32900722554202fcd9b40d90dbe0873cf175a87200d2fa02f`  `src/preservation_test/generalization/verification/verify_02_corpus.py`
- `22efe25a23ceeb7aec4e930fd96b727c21398e63c46a180e34c48510f479f194`  `src/preservation_test/generalization/verification/verify_03_sources.py`
- `28654ebb75f4d1abcb3ac40b6b5ecdbcdd4ed30a171e9afb27f351a99cf7ce4a`  `src/preservation_test/generalization/verification/verify_04_transformations.py`
- `27efd87e48bf1fe8b1e80928f7b8da36ee034ffd14ea88ca5bec167950e19e50`  `src/preservation_test/generalization/verification/verify_04_transformations_utils.py`
- `6725eb54caeb360babc4ba35958802c3968be11af2b0f5b52beb7250166e8516`  `src/preservation_test/generalization/verification/verify_05_freeze_02.py`
- `78e43cde6662c026abfa417fcfd1f492f1edc4ee71ad889ccf74bb67555afe4e`  `src/preservation_test/generalization/verification/verify_06_freeze_02.py`
- `c85f68b7dbf350f558b80efd92d0a35151515cd7982e55a1065b7a63f2509e84`  `src/preservation_test/generalization/verification/verify_hashes.py`
- `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`  `src/preservation_test/validation/__init__.py`
- `720998a4d83fd4209ba97c6c7e9b3a32b43935a4bd8d9de03ee706146d34f902`  `src/preservation_test/validation/release_sweep.py`
- `06972f72fcb5d2b8ad1fde1da68c89b1496b7d807c9caf74fb97a4a5ed7d2a21`  `src/preservation_test/validation/reverse_sweep.py`
- `6c9bdd21d91b2534e213de626a60e6c26df13a80d3b6c3c0940bb720637047aa`  `uv.lock`
- `b9d1e0a5be9d87687cde396e9ef3f6a67fe9bd85540593bc3c0b6fe21556c024`  `validation/executor-smoke/plan.toml`
- `1458ff21a544c3e722db5c531bc548ca534e47b8a8db46fbfa4b8a45b0d1dc91`  `validation/executor-smoke/results/run.json`
- `f0935824df1af82ab62ad77b7f4989f76dd71724511ef3f7e207831ec72a0a7c`  `validation/executor-smoke/results/syft-config.log`
- `07b1ea4dea9f02d559d49a10fb9063553adbaa078e18b00baf8d45061e294be7`  `validation/executor-smoke/results/validation-cdx/cdx2spdx/evaluation.json`
- `32220d34806046e9a6ab07babc3f9d0eb07a91e7f0647bb56c576eadd51caee7`  `validation/executor-smoke/results/validation-cdx/cdx2spdx/evaluation.log`
- `f22a2028a5074fe20d9e818b1dd8da2a7aff08ed5f55683164deb84be1d10b9c`  `validation/executor-smoke/results/validation-cdx/cdx2spdx/execution.json`
- `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`  `validation/executor-smoke/results/validation-cdx/cdx2spdx/target-validation.json`
- `e886ff9093e4d8e02fe48a8c92a45859a0a3b4ac3cf3a6a7f5da61876530e246`  `validation/executor-smoke/results/validation-cdx/cdx2spdx/target.spdx.json`
- `e3562ff119a5231ce53b6fb9fd8dead497474605b4db7fe5b45344363e3c1ed0`  `validation/executor-smoke/results/validation-cdx/cdx2spdx/transform.log`
- `943539a7f234cfa39e0db7c9b72714e7a460400bc51612db16a0679f9114bab1`  `validation/executor-smoke/results/validation-cdx/cdx2spdx/validation.log`
- `2f397d0ab45db7e9ca270a00d715875c61fe12ef2aa66e0cd6d33717bedb6297`  `validation/executor-smoke/results/validation-cdx/syft/evaluation.json`
- `6a13774ea5717b29650f168d7f3b97c8127457b039b970eeda46ff67ecd5dfa3`  `validation/executor-smoke/results/validation-cdx/syft/evaluation.log`
- `e02e4efe6abc487d34409f6dac9d24355095500aa183c075caafc859b9fa4f0d`  `validation/executor-smoke/results/validation-cdx/syft/execution.json`
- `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`  `validation/executor-smoke/results/validation-cdx/syft/target-validation.json`
- `71793d5c4efa77b1ba25fea25f7de5ad86282874f300821bc2140391e937e0eb`  `validation/executor-smoke/results/validation-cdx/syft/target.spdx.json`
- `800739c26f37787384e458a94d5cae46e153968ab0aad79e5d1e534e56d8b189`  `validation/executor-smoke/results/validation-cdx/syft/transform.log`
- `943539a7f234cfa39e0db7c9b72714e7a460400bc51612db16a0679f9114bab1`  `validation/executor-smoke/results/validation-cdx/syft/validation.log`
- `e46eabb69998fdda558921ad5d69b2b6731da3a420d22e9b698f8678f6333f26`  `validation/executor-smoke/results/validation-spdx/protobom/evaluation.json`
- `5623066627f9b2b1e36652f69885bb387f36c8329243f1ebe8d9802eab5b4273`  `validation/executor-smoke/results/validation-spdx/protobom/evaluation.log`
- `94b94667c3776064943d0bb6a17196b08b465764afca64894fcb564c0e98e27d`  `validation/executor-smoke/results/validation-spdx/protobom/execution.json`
- `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`  `validation/executor-smoke/results/validation-spdx/protobom/target-validation.json`
- `2b8d910f983fb7da5ad04368c14398a8f64150a7ccc0e7fee7d9eba8541f2d9f`  `validation/executor-smoke/results/validation-spdx/protobom/target.cdx.json`
- `943539a7f234cfa39e0db7c9b72714e7a460400bc51612db16a0679f9114bab1`  `validation/executor-smoke/results/validation-spdx/protobom/transform.log`
- `943539a7f234cfa39e0db7c9b72714e7a460400bc51612db16a0679f9114bab1`  `validation/executor-smoke/results/validation-spdx/protobom/validation.log`
- `943028ac5a42e9dac33f225c8b779a6bd26373d16a8a19bec5b39c0c6b19ca32`  `validation/executor-smoke/results/validation-spdx/syft/evaluation.json`
- `4ae4226a8803862a08a601b108348b53e11c50849537180c03f4e28010dbd949`  `validation/executor-smoke/results/validation-spdx/syft/evaluation.log`
- `e944634d9da2cef85dbd845146566d469138ebd8224f906a2a13baf1e5a833f3`  `validation/executor-smoke/results/validation-spdx/syft/execution.json`
- `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`  `validation/executor-smoke/results/validation-spdx/syft/target-validation.json`
- `64da99355811f1e0fedb5822e3a90c401a276b584447671afea021b05c806139`  `validation/executor-smoke/results/validation-spdx/syft/target.cdx.json`
- `800739c26f37787384e458a94d5cae46e153968ab0aad79e5d1e534e56d8b189`  `validation/executor-smoke/results/validation-spdx/syft/transform.log`
- `943539a7f234cfa39e0db7c9b72714e7a460400bc51612db16a0679f9114bab1`  `validation/executor-smoke/results/validation-spdx/syft/validation.log`
