# Freeze 02 Executor and Integrity Verification

The executor runs the fixed plan once and retains separate execution,
validation, and preservation-evaluation evidence.
It does not adjudicate findings.
Freeze 01 files remain unchanged.

## Prepare and exercise the apparatus on Windows x64

Restore the repository-local tools at the exact paths and hashes already
recorded in `generalization/05-transformations.toml`.
An installed tool with a different hash is refused.
Do not upgrade dependencies or rerun `run.ps1`.
Use the existing locked environment:

```powershell
uv sync --locked
uv run --frozen python -m preservation_test.generalization.smoke_generalization --refresh-plan
uv run --frozen python -m preservation_test.generalization.smoke_generalization --prepare
uv run --frozen python -m preservation_test.generalization.smoke_generalization --run
uv run --frozen python -m preservation_test.generalization.smoke_generalization --verify
```

`--refresh-plan` regenerates only `05-transformations.toml` using the current
p04 generator.
It checks the preserved-source provenance and the existing tool
hashes, requires identical route/source/status membership and tool identities,
and refuses an established freeze or existing formal results.

The smoke plan uses only the previously examined SPDX and CycloneDX validation sources.
It exercises the real Syft, Protobom, cdx2spdx, Java runtime, and
sbom-utility artifacts.
Everything is written under `validation/executor-smoke/`.

Inspect the recorded commands, target filenames, effective Syft configuration,
step durations, target validation results, and evaluator outputs.
Validation may report `invalid`: that is distinct from an infrastructure failure.
Every planned smoke route must complete conversion and evaluation, and
return a completed validator decision.
Each converter must be exercised at least once.

The formal timeout must be at least four times the largest observed smoke-step
duration plus 30 seconds, with a 60 second minimum.
The current plan generator uses 300 seconds;
verification refuses an inadequate margin.
If the timeout or apparatus needs correction,
preserve the first smoke plan and results in a
separately named evidence directory before preparing another smoke attempt.
Do not overwrite or silently rerun the first evidence.
Repeat the smoke check with the corrected apparatus before freezing.

A smoke failure is evidence of unfinished apparatus.
The Linux subprocess tests do not substitute for this Windows check.

## Establish Freeze 02

After smoke verification and the prerequisite gate pass, review and commit
all preparation code, the refreshed plan, and smoke evidence.
Dependency versions and sampling inputs remain fixed.

```powershell
uv run --frozen python -m preservation_test.generalization.verification.verify_05_freeze_02
# Review and commit the complete pre-freeze state before proceeding.
.\freeze_02.ps1
```

The script requires a clean committed state.
It adds status, UTC time, pre-freeze commit, and
exact SHA-256 inventory to the existing draft record.
It refuses an already established freeze.
Review and commit `contracts/FREEZE_02_GENERALIZATION.md` before execution.

The inventory covers the environment declarations, sampling and generated
records, all preserved sources, converter and validator artifacts, every file
in the repository-local JDK, all Python apparatus modules except generated
`_version.py`, known defect shapes, smoke plan and evidence, and freeze wrapper.
The freeze record excludes itself.
Its Git commit fixes its contents;
its SHA-256 is captured in the formal run manifest.

```powershell
uv run --frozen python -m preservation_test.generalization.verification.verify_06_freeze_02
uv run --frozen python -m preservation_test.generalization.execute_generalization
```

The first command only reads and verifies.
The second begins the formal experiment and
requires Windows x64, the declared Python minor version, the
committed freeze record, matching frozen artifacts, and empty formal results.
Do not run the pre-freeze preparation scripts after this point.

## Evidence and interruption policy

Each route has predeclared target, validation JSON, evaluator JSON,
converter log, validator log, evaluator log, and execution JSON paths.
The execution JSON is created with `status = started` before launching the
converter, then updated after each step.
The run manifest identifies mode, commit, interpreter, platform,
plan digest, freeze-record digest, effective environment,
Syft configuration check, route progression, and completion state.

The converter environment comes from an explicit allowlist, with minimal PATH,
`SYFT_CHECK_FOR_APP_UPDATE=false`, and pinned JAVA_HOME when needed.
Undeclared SYFT variables, Java options, Python options,
and proxy variables are not inherited.
Local and standard user/XDG Syft configuration files cause refusal.
Effective Syft configuration is captured before any route runs.

Every subprocess has the plan timeout.
Timeout handling terminates its process tree and retains available stdout/stderr.
Converter timeout/nonzero exit/missing target is `execution_failure`;
validator timeout/launch error/unexpected exit or missing result is `validation_error`;
evaluator failure is `evaluation_error`.
Validator exits 0 and 2 mean `valid` and `invalid`,
respectively, when a result file exists.
Evaluator execution continues after an invalid target.
The frozen evaluator rejects a UTF-8 BOM;
such a case remains `evaluation_error`.

No formal retry or resume is implemented in this freeze.
All repeat invocations against populated results are refused.
`retry_directory_pattern` remains a reserved plan field
and authorizes no re-execution.
A host interruption leaves its evidence in place;
completing a revised execution procedure requires an
explicit amendment/new freeze and separately located evidence.
No attempt is silently replaced or selected for a better outcome.

Post-freeze verification accepts populated results, checks inventory
completeness as well as each digest, and always rechecks Freeze 01.
It verifies the apparatus, not the correctness or completeness of generated results.
