# TODO 2026-10-05

The files below are in the order to work through them.
Items 1–8 must be done before Freeze 02.
Item 9 is recommended.
The corpus, sources and Freeze 01 files need no changes.

## 1. DONE src/preservation_test/generalization/p04_build_transformations.py

Then regenerate generalization/05-transformations.toml with run.ps1. Do not edit it by hand.

## 2. DONE src/preservation_test/generalization/verification/verify_04_transformations.py

Completed.

Refactored the pre-freeze transformation verifier into a small orchestrator plus
`verify_04_transformations_utils.py`.

Verification requirements are grouped into families A-J so the implementation
can be maintained without global check numbering.

Added verification that:

- every route declares target, validation, evaluation, transform-log,
  validation-log, evaluation-log, and execution-record paths;
- every route evidence path is non-empty, under `results_directory`, and unique
  across the transformation matrix;
- `run_manifest_path` is exactly `results_directory/run.json`;
- `timeout_seconds` is a positive integer;
- `retry_directory_pattern` is non-empty and contains `{n}`;
- the declared execution state remains `not_started`;
- transformation outputs remain unexamined; and
- `generalization/results/` is empty before Freeze 02.

Existing provenance, artifact-hash, converter/runtime, validator, route,
command, unsupported-route, and complete-matrix checks were preserved.

## 3. tests/generalization/test_p04_build_transformations.py and tests/generalization/test_verify_04_transformations.py

- test_p04: assert that \_target_paths returns seven distinct paths inside the route
  directory, and that the [transformations] table contains the three new keys.
- test_verify_04: one failing test for each new check (a missing path field, a duplicate
  path, a path outside results_directory,
  bad values for each of the three new keys,
  a non-empty results directory),
  plus one passing case with an empty results directory.

## 6. contracts/FREEZE_02_GENERALIZATION.md

Evaluator Environment: replace the three bullets that begin "Evaluation is performed using:" with:

```markdown
The executor is launched with `uv run --frozen`, so `uv.lock` is the dependency
source of truth and is not updated during execution.

The executor invokes the frozen evaluator with the same interpreter
(`sys.executable -m preservation_test.evaluator.evaluate --json`), so the
python version recorded in the run manifest is the interpreter that performed
evaluation.

The frozen evaluator reads documents with `encoding="utf-8"`.
A target document beginning with a UTF-8 byte-order mark therefore produces
`evaluation_error`.
```

New section after Transformation Execution: "Evidence Layout".

````markdown
## Evidence Layout

Every evidence path is predeclared in `05-transformations.toml`.
The executor does not choose evidence locations.

For each planned route, the route record declares the target document, the
target validation result, the evaluator output, the converter log, the
validator log, the evaluator log, and an `execution.json` record.

`execution.json` records route identity, attempt number, start and end times,
source SHA-256, converter identity and version, exact command arguments,
working directory, effective environment, each exit code, timeout status,
target SHA-256, validation outcome, and evaluation outcome.
It is written with status `started` before the converter is launched.
A route found in status `started` is an interrupted execution; the executor
stops and does not resume that route.

The run manifest at `run_manifest_path` records the repository commit, the
SHA-256 of this Freeze 02 record, start and end times, ```python version,
operating system and architecture, the Syft configuration-location check, and
the effective Syft configuration.
````

Transformation Execution: replace the paragraph that begins "A route is not silently re-executed" with:

```markdown
The first formal execution of each planned route is the evidence of record.
A route may be executed again only after an infrastructure failure: the
converter process could not be started, or the host failed during execution.
A repeated execution is written under the route's `retry_directory_pattern`
directory, and the first attempt is retained.
A later execution never replaces the first as the evidence of record.

Each converter, validator, and evaluator invocation is subject to
`timeout_seconds`.
A converter timeout is an execution failure; a validator timeout is
`validation_error`; an evaluator timeout is `evaluation_error`.

The executor builds each converter environment from an explicit allowlist and
does not inherit the invoking shell's environment.
Before the first route, it confirms that no Syft configuration file exists in
the locations Syft 1.52.0 searches (`./.syft.<ext>`, `./.syft/config.<ext>`,
`~/.syft.<ext>`, and `syft/config.<ext>` in the XDG configuration
directories) and records the result.

The executor refuses to run formally unless Freeze 02 verifies, Freeze 01
verifies, and the results directory is empty.
Before Freeze 02, the executor is exercised only in engineering mode, on
engineering-validation sources, with results written outside
`generalization/results/`.
```

Target Document Validation: replace the sentence
"For SPDX 2.3 targets, sbom-utility uses its applicable SPDX 2.3 schema variant for validation." with:

```markdown
Validator exit code 0 is `valid`, exit code 2 (`ERROR_VALIDATION`) is
`invalid`, and any other exit code or a missing validation result is
`validation_error`.

For SPDX 2.3 targets, sbom-utility 0.19.2 validates against its default
embedded SPDX v2.3 schema variant, not v2.3.1.
```

Adjudication and Interpretation: add after
"It does not change or relabel the evaluator's violation subtype."
Replace <K> with your chosen number.

```markdown
Adjudication inspects the raw source and target documents and does not reuse
evaluator output as evidence.
For each adjudicated finding, the adjudication record contains:

- the source component's JSON as it appears in the source document;
- the anchored target component's JSON as it appears in the target document;
- every location in the target document where the source PURL string or its
  canonical form occurs; and
- the decision for each of the four criteria, with a reason.

Every candidate violation is adjudicated when a route has at most <K>
candidate violations.
Otherwise, <K> are adjudicated per route and verdict, selected by ascending
SHA-256 of `route_id + "|" + component ref + "|" + purl`.
```

Result classes: change - underdetermined: an underdetermined result where applicable; to:

```markdown
- `underdetermined`: evaluator verdict `UNDERDETERMINED`;
```

Delete the evaluation_error bullet from the list. Add after the list:

```markdown
Result classes apply to individual source PURLs within evaluated routes.
Route-level outcomes (execution failure, validation outcome, and
`evaluation_error`) are reported per route.

`known/known_violations.toml` declares converter-agnostic defect shapes.
Because `VIOLATED_RELOCATED` cannot occur for SPDX targets, every confirmed
CycloneDX-to-SPDX `VIOLATED_DROPPED` result matches a predeclared shape, and
only `VIOLATED_ALTERED` can be `new confirmed` in that direction.
```

Artifact Hashes: delete - this Freeze 02 record.,
since a record cannot contain its own hash.
Change the following line from "the Freeze 02 verification implementation;" to:

```markdown
- the Freeze 02 pre-freeze and post-freeze verification implementations;
```

Then add after the list:

```markdown
The SHA-256 of this record is captured in the run manifest at execution time
and in the Git commit that establishes Freeze 02.

Hash lines in this section use the same format as Freeze 01 so that they can
be verified mechanically.
```

## 7. New files

`src/preservation_test/generalization/execute_generalization.py`

- Modes. Formal mode takes only the real 05-transformations.toml and generalization/
  results/. Engineering mode refuses any plan or results root that resolves to either of those.
- Formal preconditions. Before running anything, it verifies:
  Freeze 01 (verify_01_freeze_01);
  Freeze 02 (verify_06_freeze_02, below);
  that the results directory is empty.
- Before each route:
  re-hash the source, converter, runtime and validator;
  refuse to run if any declared output path already exists.
- Environment. Build it from an allowlist: SystemRoot, a minimal PATH, TEMP/TMP,
  SYFT_CHECK_FOR_APP_UPDATE=false, and JAVA_HOME set to the pinned JDK directory.
- Execution order for each route:
  Write execution.json with status started.
  Run command_argv from the repository root with timeout_seconds. Send stdout and stderr to transform.log in labeled sections.
  If a target exists, hash it.
  Run validation_command_argv,
  log to validation.log, and map exit codes 0 / 2 / other to valid / invalid / validation_error.
  Run
  sys.executable -m preservation_test.evaluator.evaluate --json --commitment-file contracts/commitments.toml
  --commitment-id purl_preservation_v1 <source> <target>.
  Send stdout to evaluation.json and stderr to evaluation.log.
  A nonzero exit or a timeout is evaluation_error.
  Update execution.json after each step.
- Evidence encoding. Write evidence files in binary mode or with newline="\n".
- Run manifest.
  Write run.json at the start and update it at the end,
  including the Freeze 02 record's hash and the captured syft config output.
- Scope. No adjudication, no retries without an explicit retry argument, and no discovery of sources or converters.

src/preservation_test/generalization/verification/verify_06_freeze_02.py
This is the gate after the freeze.
Parse the Artifact Hashes section of contracts/FREEZE_02_GENERALIZATION.md using the same line format as Freeze 01.
The simplest way is to give read_frozen_hashes a path parameter and reuse it.
Then re-hash every listed file and require verify_01_freeze_01 to pass.
Unlike verify_05, it must not require an empty results directory.

tests/generalization/test_execute_generalization.py (runs in CI on Linux)
Use a synthetic plan in tmp_path with fake converters and a fake validator, all small python scripts.

Cover these cases:

- a converter that exits 0 and writes a valid target, and one that exits nonzero;
- a converter that exits 0 but writes no target, and one that sleeps past the timeout;
- a validator that exits 0, 2, or 1;
- an evaluator failure, using a target that isn't JSON;
- refusal when an output path already exists, and the stop on a started execution.json;
- the environment allowlist actually applied;
- engineering mode refusing the real plan path and anything under generalization/results/.

tests/generalization/test_verify_06_freeze_02.py
Build a synthetic Freeze 02 record in the same style
as test_verify_01_freeze_01.py.
Cover a pass, a modified artifact, a missing artifact, and a failing Freeze 01.

validation/executor-smoke/plan.toml and validation/executor-smoke/README.md

- Hand-write a plan using the same schema as 05,
  over validation/cyclonedx-cli-424/source.spdx.json and validation/cyclonedx-cli-reverse-sweep/source.cdx.json,
  with all three converters and the real bin/ tools.
- Results go to validation/executor-smoke/results/.
- Run it in engineering mode on Windows.
- Record in the README:
  protobom's actual handling of the -o filename;
  that Syft runs with an empty configuration;
  the maximum duration observed for each step. Set TIMEOUT_SECONDS in item 1 from these, with a stated margin.

## 8. freeze_02.ps1

Replace the placeholder comments with working steps:

1. Fail if git status --porcelain is not empty.
2. Fail if FREEZE_02_GENERALIZATION.md already says **Status:** FROZEN.
3. Run verify_05_freeze_02 and fail on a nonzero exit.
4. Hash every artifact in the Artifact Hashes list, including the executor and both
   verification modules.
5. Write status, UTC timestamp, HEAD commit and the hash lines into the record, using the Freeze 01 line format.
6. Commit that change alone.
7. Run verify_06_freeze_02 against the new commit.

## 9. install_generalization_tools.ps1 (recommended)

- Enforce pinned hashes.
  Add an $ExpectedSha256 table for all five artifacts and throw on any mismatch before Cleanup.
  Take the values from the current 05-transformations.toml.
- Hash the whole JDK runtime, not just the launcher.
  Also hash jdk-$JavaVersion\release and jdk-$JavaVersion\lib\modules.
  Add both to the cdx2spdx converter record in p04
  (for example runtime_release_sha256 and runtime_modules_sha256)
  and have verify_04 check them.
- Rename $Matches. It is a PowerShell automatic variable; rename it to $Found.

## Steps

1. Fix known/known_violations.toml with narrowly defined pre-existing defect shapes.
2. Fix the Freeze 02 self-hash issue and establish generalization/06-freeze.toml as the external freeze manifest.
3. Finalize the raw-evidence, all-candidate adjudication rule.
4. Tighten the re-execution and outcome-level wording.
5. Add the empty-results check to the pre-freeze verifier.
6. Implement freeze_02.ps1 plus verify_freeze_02_integrity.py.
7. Smoke-test the three converter command templates and choose the timeout.
8. Then write the executor against those settled rules.
