# cyclonedx-cli Issue #424 Engineering Validation

This directory records the engineering-validation investigation for
CycloneDX/cyclonedx-cli issue #424.

The issue was known during study design and therefore does not constitute
held-out generalization evidence.

## Historical Report

Issue:

- CycloneDX/cyclonedx-cli #424
- opened 2025-04-03
- reported SPDX-to-CycloneDX conversion in which a package PURL remained in a
  CycloneDX `properties` entry rather than being placed in `component.purl`

The reported example used the
Google Distroless SPDX SBOM and identified the
`tzdata` component as an example of the behavior.

## Prerequisite 1: Install Cosign for the Validation Workflow

Create the repository-local binary directory if it does not already exist
and add the directory to `PATH` for the current PowerShell session.

```powershell
New-Item -ItemType Directory -Force ".\bin"

$env:Path = "$(Resolve-Path .\bin);$env:Path"
```

Download the pinned Cosign executable and verify the installed version.

```powershell
$CosignVersion = "v3.0.2"

Invoke-WebRequest `
  -Uri "https://github.com/sigstore/cosign/releases/download/$CosignVersion/cosign-windows-amd64.exe" `
  -OutFile ".\bin\cosign.exe"

cosign version
```

Record the reported version in `metadata.toml`.

```toml
[source.attestation]
cosign_version = "v3.0.2"
```

## Prerequisite 2: Initialize the Validation Record

Create:

- `validation/cyclonedx-cli-424/metadata.toml`;

And three empty files:

- `validation/cyclonedx-cli-424/source.spdx.json`;
- `validation/cyclonedx-cli-424/target.cdx.json`; and
- `validation/cyclonedx-cli-424/result.json`.

## Prerequisite 3: Recover and Verify the Historical Source

Then retrieve and preserve the attestation
by running the `acquisition_command` provided in `metadata.toml`.

Review `validation/cyclonedx-cli-424/attestation.jsonl`.

Then extract the historical SPDX source document
by running the `extraction_command` provided in `metadata.toml`.

Review `validation/cyclonedx-cli-424/source.spdx.json`.

Calculate the SHA-256 hashes for `attestation.jsonl` and `source.spdx.json`
using the commands documented in `metadata.toml`, and record the observed
values in `metadata.toml`.

Use PowerShell to read and parse the SPDX JSON file to get the source format
and record it in `metadata.toml` using the commands provided in `metadata.toml`.

Then complete the `[source.example_component]` entries in `metadata.toml`.

At completion of this prerequisite, the preserved source evidence and its
provenance should be sufficient to reproduce the input independently of the
free-form example shown in GitHub issue #424.

## Investigation Procedure

The validation investigation follows the implementation path from the CLI to
the conversion library.

### 1. Confirm the historical issue context

Review the associated GitHub issue:

- <https://github.com/CycloneDX/cyclonedx-cli/issues/424>

Confirm that `validation/cyclonedx-cli-424/metadata.toml` records:

- issue number and date opened;
- reported conversion command;
- reported target representation; and
- linked implementation work.

The source artifact, source format, source PURL, and example-component
information were established and verified during the prerequisites.

Do not use the free-form issue example as the preserved experimental input.
The verified artifact produced during Prerequisite 3 is the source of record
for the validation run.

### 2. Identify the PURL conversion change

Do not infer the PURL fix from an adjacent CPE change.

The relevant CycloneDX .NET library change is:

- CycloneDX/cyclonedx-dotnet-library PR #394
- "Convert a SPDX purl externalReference into the item level purl field"

PR #410 concerns CPE conversion and is not the PURL change used for this
validation case.

### 3. Identify the library release containing the change

Inspect the CycloneDX .NET library release history and determine the first
released library version containing PR #394.

Start on the GitHub repository for the CycloneDX .NET library:

<https://github.com/CycloneDX/cyclonedx-dotnet-library>

Then do this:

1. Open Pull requests.
2. Search for PR #394.
3. Open PR #394, titled Convert a SPDX purl externalReference into the item level purl field.
4. From that PR, note the merge date and relevant commits if shown.
   PR #394 was merged on 2026-02-27.

Then go to the repository's Releases page and inspect releases after that merge.
Find the first release whose release notes explicitly include PR #394.

GitHub's
[repo release page](https://github.com/CycloneDX/cyclonedx-dotnet-library/releases#release-v12.0.0)
already shows that 12.0.0 contains:
**Convert a SPDX purl externalReference into the item level purl field … #394**
and the release is tagged v12.0.0 at commit 5194c90.

The first release containing the PURL conversion change is:

- CycloneDX .NET library `12.0.0`;
- released 2026-03-04; and
- includes PR #394, "Convert a SPDX purl externalReference
  into the item level purl field by @dgl in #394"

The immediately preceding released library version is `11.0.0`, released
2026-02-10.

Record the release versions, dates, relevant PR, and release tags or commits
in `metadata.toml` in the `[library_change]` section.

### 4. Map library versions to cyclonedx-cli releases

Inspect the **cyclonedx-cli release history** and the **project dependencies** at
each release tag to identify the CLI release boundary
corresponding to the library change established in Step 3.

Start on the cyclonedx-cli releases page:
<https://github.com/CycloneDX/cyclonedx-cli/releases>

Identify the adjacent CLI releases spanning the relevant library dependency
transition.

For each candidate release:

1. Open the release tag in GitHub.
2. Navigate to: `src/cyclonedx/cyclonedx.csproj`
3. Locate the `CycloneDX.Spdx.Interop` package reference.
4. Record the CLI release version, release date, tag or commit, and referenced
   `CycloneDX.Spdx.Interop` version.

For `v0.31.0`, the tagged project file references:

- `CycloneDX.Spdx.Interop` `11.0.0`.

For `v0.32.0`, the tagged project file references:

- `CycloneDX.Spdx.Interop` `12.1.1`.

Step 3 established that:

- `11.0.0` is the immediately preceding library release before the PURL fix;
  and
- `12.0.0` is the first released library version containing PR #394.

Therefore the adjacent CLI releases establish the engineering-validation
boundary:

- known-bad candidate: `cyclonedx-cli` `0.31.0`, using
  `CycloneDX.Spdx.Interop` `11.0.0`; and
- first-post-fix-library candidate: `cyclonedx-cli` `0.32.0`, using
  `CycloneDX.Spdx.Interop` `12.1.1`.

Record the CLI release versions, release dates, tags or commits, and
corresponding library versions in `metadata.toml`.

These candidate versions are selected from repository and release history
before executing the frozen evaluator. Their selection therefore does not
depend on evaluator output.

### 5. Reproduce the known-bad transformation

Reproduce the transformation using the known-bad
CLI candidate established in Step 4.

The executable acquisition, version-check, conversion, and hashing commands
for this step are recorded in `metadata.toml`.
Run the commands provided there.

First, acquire the Windows x64 binary for the known-bad candidate identified
in `[cli_release_boundary]`.

The CycloneDX CLI publishes platform-specific binaries as release assets.
For Windows x64, use the `cyclonedx-win-x64.exe` asset associated with the
recorded release tag.

Run the `known_bad_acquisition_command` recorded for the known-bad CLI in
`metadata.toml`.

Then run the recorded `known_bad_version_command` and confirm that the
executable reports the expected CLI version before performing the
transformation.

Record the confirmed version in: `[transformation].version`

Do not populate this field solely from the release metadata. It is
execution-derived and should reflect the executable actually used for the
reproduction.

Run the transformation using the `command` recorded in `[transformation]`.

The command must use the preserved historical source:
`validation/cyclonedx-cli-424/source.spdx.json`

and write the complete generated CycloneDX document to:
`validation/cyclonedx-cli-424/target.cdx.json`

Do not modify the source document or manually alter the generated target
before evaluation.

After the transformation completes:

1. confirm that `target.cdx.json` exists and can be parsed as JSON;
2. confirm that the generated document is a CycloneDX document;
3. run the target SHA-256 command recorded in `metadata.toml`;
4. record the observed digest in `[target].sha256`; and
5. record any execution-environment information required for independent
   reproduction.

At completion of this step, the validation record should preserve:

- the exact CLI release selected independently in Step 4;
- the executable actually used;
- the version reported by that executable;
- the exact transformation command;
- the preserved historical source SBOM;
- the complete generated target SBOM; and
- the SHA-256 digest of the generated target.

Do not run the frozen evaluator during this step.

The purpose of Step 5 is to reproduce and preserve the known-bad
transformation.
Evaluation begins in Step 6.

### 6. Run the frozen evaluator

Evaluate the reproduced known-bad transformation using the scientific
apparatus identified by:
`contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`

Before execution, confirm that the applicable freeze remains:

- status: `FROZEN`;
- frozen content commit:
  `ef3a5dacdf1a483f41d87ee955d365376e63a220`; and
- freeze-break log: `None`.

The freeze identifies the authoritative commitment, provenance,
interpretation rules, evaluator implementation, and adjudication protocol
used for this engineering-validation case.

Do not modify any frozen scientific artifact in response to the reproduced
target before running the evaluator.

Run the evaluator using the `command` recorded in the `[evaluator]` section
of `metadata.toml`.

The evaluator must compare:

- `validation/cyclonedx-cli-424/source.spdx.json`; and
- `validation/cyclonedx-cli-424/target.cdx.json`

under the frozen commitment identified by:
`[evaluator].commitment_id`

Preserve the complete machine-readable evaluator output in the file recorded
by:
`[evaluator].result_file`.

For this validation case, that file is:
`validation/cyclonedx-cli-424/result.json`

Do not manually edit or reduce the evaluator output before preservation.

After execution:

1. confirm that `result.json` exists and parses as JSON;
2. preserve the complete evaluator result;
3. record any execution-derived evaluator information required by
   `metadata.toml`; and
4. do not change the frozen evaluator or commitment in response to the result.

If execution reveals a defect in any frozen scientific artifact, stop the
generalization path and follow the freeze-break procedure defined in
`contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`.

Verify the result parses with:

```pwsh
Get-Content validation/cyclonedx-cli-424/result.json -Raw |
   ConvertFrom-Json |
   Out-Null
```

For this case, successful reproduction remains engineering-validation
evidence because the relevant failure shape was known during study design.
It does not constitute held-out evidence of generalization.

Step 6 here establishes:

```text
source format:  spdx-2.3
target format:  cyclonedx
commitment:     purl_preservation_v1

tzdata:
    VIOLATED_RELOCATED

base-files:
    VIOLATED_RELOCATED

netbase:
    VIOLATED_RELOCATED
```

Notice especially this **tzdata** part of `result.json`:

```json
    {
      "ref": "SPDXRef--at-rules-underscore-distroless~~apt~bookworm-underscore-tzdata-underscore-2025b-0-p-deb12u1-underscore-amd64",
      "verdict": "VIOLATED_RELOCATED",
      "purl": "pkg:deb/debian/tzdata@2025b-0%2Bdeb12u1?arch=all",
      "detail": "purl is present in the target but not in its canonical slot"
    },
```

That matches the predeclared expected verdict documented in `metadata.toml`.

### 7. Adjudicate the engineering-validation result

Adjudicate the preserved evaluator result against the evidence fixed for this
validation case.

Do not modify the source artifact, generated target, frozen commitment, or
frozen evaluator during adjudication.

Review:

- the frozen commitment identified by `[evaluator].commitment_id`;
- the preserved historical SPDX source;
- the generated CycloneDX target;
- the complete machine-readable evaluator result; and
- the behavior originally reported in cyclonedx-cli issue #424.

For the historical example component `tzdata`,
confirm the following evidence chain.

In the preserved SPDX source:

- the component is `tzdata`;
- the component version is `2025b-0+deb12u1`; and
- the PACKAGE-MANAGER PURL external reference is
  `pkg:deb/debian/tzdata@2025b-0+deb12u1?arch=all`.

In the generated CycloneDX target:

- the corresponding `tzdata` component is present;
- the PURL value is preserved;
- the PURL is represented as the property
  `spdx:external-reference:package-manager:purl`; and
- the PURL is not represented in the canonical CycloneDX `component.purl`
  slot.

In the preserved evaluator result,
confirm that the corresponding component receives:

`VIOLATED_RELOCATED`

with the detail:

`purl is present in the target but not in its canonical slot`

Compare this observed verdict with the predeclared value recorded in:

`[expected].expected_verdict`

For this case, the observed `VIOLATED_RELOCATED` verdict matches the
predeclared expected verdict.

Also note that the evaluator independently reports the same relocation
behavior for `base-files` and `netbase`.
These additional observations may support the engineering interpretation
of the reproduced behavior, but they are not required to
establish reproduction of the historical `tzdata`
example from issue #424.

Record the adjudication in the existing `[adjudication]` section of
`metadata.toml`.

The adjudication should state that:

- the preserved source contains the expected `tzdata` PURL;
- the known-bad CLI transformation preserves that PURL outside the canonical
  CycloneDX `component.purl` slot;
- the frozen evaluator classifies that behavior as `VIOLATED_RELOCATED`;
- the observed verdict matches the predeclared expected verdict; and
- the known historical behavior reported in issue #424 has therefore been
  reproduced by the frozen evaluator.

This establishes successful engineering validation of the frozen evaluator
against a previously known case.

It does not constitute held-out evidence of generalization.
