"""Verification stage 04: verify the frozen transformation execution plan.

Purpose
-------
05-transformations.toml is the pre-outcome execution plan that crosses the
preserved held-out corpus with the independently selected transformation
implementations.

This verifier establishes that the plan still refers to the exact source
records, converter artifacts, runtime artifacts, target validator, and complete
source/converter matrix declared before generalization execution.

The verified provenance chain is:

    04-sources.toml
        |
        +----------------------+
        |                      |
        v                      v
preserved sources       frozen tool artifacts
        |                      |
        +----------+-----------+
                   |
                   v
        05-transformations.toml

The verification requirements are grouped by responsibility.

A. Preserved-source prerequisite
--------------------------------
A1. The preserved-source verification stage succeeds before
    05-transformations.toml is verified.

B. Input records
----------------
B1. 05-transformations.toml exists.
B2. 05-transformations.toml and the verified 04-sources.toml parse successfully.
B3. 05-transformations.toml contains the required [transformations] table.

C. Record provenance
--------------------
C1. The recorded 04-sources.toml path is the expected source-record path.
C2. The recorded 03-corpus.toml path is the expected corpus-record path.
C3. The recorded 04-sources.toml SHA-256 matches the current source record.
C4. The recorded 03-corpus.toml SHA-256 matches the current corpus record.
C5. The recorded transformation-definition code hashes match the current files.

D. Preserved-source registry
----------------------------
D1. 04-sources.toml contains source records.
D2. Every source record is a table with a non-empty study ID, preserved path,
    and preserved SHA-256.
D3. Every study ID is unique.

E. Converter artifacts
----------------------
E1. 05-transformations.toml contains converter records.
E2. Every converter record declares a non-empty converter ID, artifact path,
    and artifact SHA-256.
E3. Every converter ID is unique.
E4. Every converter artifact exists and matches its recorded SHA-256.
E5. Runtime path, version, and SHA-256 are recorded together when a converter
    requires a runtime.
E6. Every recorded converter runtime artifact exists and matches its recorded
    SHA-256.

F. Target validator
-------------------
F1. 05-transformations.toml contains a target-validator record.
F2. The target validator declares a non-empty artifact path and SHA-256.
F3. The target-validator artifact exists and matches its recorded SHA-256.

G. Execution configuration
--------------------------
G1. [transformations].results_directory is a non-empty string.
G2. [transformations].run_manifest_path equals
    results_directory followed by /run.json.
G3. [transformations].timeout_seconds is a positive integer.
G4. [transformations].retry_directory_pattern is a non-empty string
    containing {n}.

H. Route declarations
---------------------
H1. 05-transformations.toml contains route records.
H2. Every route is a table with the required route, source, converter,
    source-provenance, and status fields.
H3. Every route ID is unique.
H4. Every route refers to a preserved source and declared converter.
H5. Every route carries the exact source path and SHA-256 recorded in
    04-sources.toml.
H6. Every route declares non-empty target, validation, evaluation,
    transformation-log, validation-log, evaluator-log, and execution-record
    paths under the declared results directory.
H7. Every declared route evidence path is unique across the complete matrix.
H8. Every route ID is uniquely determined by its study ID and converter ID.
H9. A source/converter pair occurs at most once in the declared routes.
H10. Every route status is either planned or unsupported_pre_execution.
H11. Every planned route declares a transformation command.
H12. Every planned transformation command invokes the exact recorded converter
     artifact or recorded converter runtime.
H13. Every runtime-based converter command references the exact recorded
     converter artifact.
H14. Every planned route requires target validation.
H15. Every planned route declares a target-validation command that invokes the
     exact recorded target validator.
H16. Unsupported routes contain no transformation command.
H17. Unsupported routes contain no target-validation command.
H18. Unsupported routes do not require target validation.
H19. Unsupported routes record a non-empty pre-execution reason.

I. Matrix invariants
--------------------
I1. The observed source/converter pairs equal the complete cross-product of
    frozen sources and converters.
I2. Together with route-pair uniqueness, every source/converter pair therefore
    occurs exactly once.
I3. [transformations].members matches the number of preserved sources.
I4. [transformations].converters matches the number of declared converters.
I5. [transformations].matrix_rows matches the complete cross-product size.
I6. [transformations].planned_routes matches the planned route records.
I7. [transformations].unsupported_routes matches the unsupported route records.
I8. Planned and unsupported route counts together equal the complete matrix.

J. Pre-execution state
----------------------
J1. [transformations].execution_state is not_started.
J2. [transformations].transformation_outputs_examined is false.
J3. The declared generalization results directory is empty before Freeze 02.

An unsupported route remains part of the matrix. It is verified as a declared
pre-execution capability boundary rather than treated as a transformation
failure.

The central matrix invariant is:

    number of preserved sources
        x
    number of frozen converters
        ==
    number of declared transformation routes

Every converter, runtime, validator, and source byte sequence required by the
plan must still be the exact artifact whose SHA-256 was recorded before
generalization execution.

This verifier runs no converter, validator, or evaluator and performs no
writes.
"""

from pathlib import Path

from preservation_test.generalization.verification.verify_04_transformations_utils import (
    load_transformation_records,
    load_verified_sources,
    verify_converters,
    verify_execution_config,
    verify_matrix,
    verify_pre_execution_state,
    verify_record_provenance,
    verify_routes,
    verify_source_provenance,
    verify_target_validator,
    verify_transformations_table,
)


def verify_04_transformations(repository_root: Path) -> Path:
    """Verify the frozen transformation execution plan."""
    # A. Preserved-source prerequisite
    # A1. Verify the preserved-source stage before checking 05.
    sources_path = verify_source_provenance(repository_root)

    # B. Input records
    # B1-B2. Require and parse the transformation and source records.
    path, data, sources_data = load_transformation_records(
        repository_root,
        sources_path,
    )

    # B3. Require the [transformations] table.
    transformations = verify_transformations_table(data)

    # C. Record provenance
    # C1-C5. Verify record paths, record hashes, and code hashes.
    verify_record_provenance(
        repository_root,
        data,
        transformations,
    )

    # D. Preserved-source registry
    # D1-D3. Load and validate source identities, paths, and hashes.
    sources_by_study_id = load_verified_sources(sources_data)

    # E. Converter artifacts
    # E1-E6. Verify converter identities, artifacts, and runtimes.
    converter_execution = verify_converters(
        repository_root,
        data,
    )

    # F. Target validator
    # F1-F3. Verify the target-validator identity and artifact.
    validator_path = verify_target_validator(
        repository_root,
        data,
    )

    # G. Execution configuration
    # G1-G4. Verify run-level paths, timeout, and retry configuration.
    execution_config = verify_execution_config(
        transformations,
    )

    # H. Route declarations
    # H1-H19. Verify route provenance, paths, identities, commands,
    # validation requirements, and unsupported-route declarations.
    route_summary = verify_routes(
        repository_root=repository_root,
        routes=data.get("route"),
        sources_by_study_id=sources_by_study_id,
        converter_execution=converter_execution,
        validator_path=validator_path,
        results_directory=execution_config.results_directory,
    )

    # I. Matrix invariants
    # I1-I8. Verify cross-product completeness, exact pair occurrence,
    # matrix dimensions, and route-status counts.
    verify_matrix(
        transformations=transformations,
        sources_by_study_id=sources_by_study_id,
        converter_ids=set(converter_execution),
        route_summary=route_summary,
    )

    # J. Pre-execution state
    # J1-J3. Verify declared and observed pre-execution state.
    verify_pre_execution_state(
        repository_root=repository_root,
        transformations=transformations,
        results_directory=execution_config.results_directory,
    )

    return path
