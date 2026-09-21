# cyclonedx-cli Issue #424 Engineering Validation: First Post-Fix-Library Candidate

This directory records the engineering-validation investigation for
CycloneDX/cyclonedx-cli issue #424.

This directory records execution of the first identified `cyclonedx-cli`
release using a library version that postdates the PURL conversion change.

## Historical Report

Issue:

- CycloneDX/cyclonedx-cli #424
- opened 2025-04-03
- reported SPDX-to-CycloneDX conversion in which a package PURL remained in a
  CycloneDX `properties` entry rather than being placed in `component.purl`

The reported example used the Google Distroless SPDX SBOM and identified the
`tzdata` component as an example of the behavior.

## Investigation Procedure

The validation investigation follows the implementation path from the CLI to
the conversion library.

### 1. Evaluate the first post-fix-library candidate

Evaluate the first CLI candidate established previously as using a post-fix
library version as a separate engineering-validation execution.

Do not overwrite any artifact from the known-bad validation case.

Create a separate validation record:

`validation/cyclonedx-cli-424-first-post/`

Create at a minimum:

- `metadata.toml`;
- `README.md`;
- `target.cdx.json`; and
- `result.json`.

Use the same preserved historical SPDX source used for the known-bad case:

`validation/cyclonedx-cli-424/source.spdx.json`

The candidate established previously is the first identified CLI release
using a post-fix library version:

- `cyclonedx-cli` `0.32.0`; using
- `CycloneDX.Spdx.Interop` `12.1.1`.

Record the executable acquisition, version-check, transformation,
target-verification, hashing, and evaluator commands in `metadata.toml`.

Run the `first_post_fix_library_acquisition_command`.

Run the `first_post_fix_library_version_command` and confirm that the
executable reports the expected CLI version.

Run the same SPDX-to-CycloneDX transformation used for the known-bad case,
changing only the executable and the output location for this validation
record.

Do not modify the preserved source artifact.

After transformation:

1. confirm that the first-post target exists and parses as JSON;
2. confirm that it reports CycloneDX as the target format;
3. calculate and record the target SHA-256;
4. run the same frozen evaluator used for the known-bad case;
5. preserve the complete machine-readable evaluator result; and
6. adjudicate the first-post result separately.

Evaluate this execution under the same frozen commitment:

`purl_preservation_v1`

and with the same frozen evaluator identified by:

`contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`.

Do not change the commitment, evaluator, or source artifact between the
known-bad and first-post executions.

The purpose of this execution is to determine whether the previously observed
PURL relocation behavior is absent when the same source is transformed by the
first identified CLI release using a post-fix library version.

This remains **engineering-validation** evidence.
It does not constitute held-out evidence of generalization.
