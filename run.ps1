$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

uv run python -m preservation_test.generalization.p01_prepare_sampling_frame

# Build the complete source-only candidate inventory
uv run python -m preservation_test.generalization.p01_build_candidates

# Build the deterministic held-out corpus from eligible candidate units
uv run python -m preservation_test.generalization.p02_build_corpus

# Verify sampling, candidate, and corpus provenance
uv run python -m preservation_test.generalization.verification.verify_02_corpus

# Preserve the exact selected source bytes and provenance
uv run python -m preservation_test.generalization.p03_preserve_sources

# Verify the preserved source bytes against the frozen corpus
uv run python -m preservation_test.generalization.verification.verify_03_sources

# Install the exact repository-local transformation toolchain
# .\install_generalization_tools.ps1

# Construct the complete pre-outcome transformation plan
uv run python -m preservation_test.generalization.p04_build_transformations `
    --syft bin/generalization/syft.exe `
    --syft-version "1.52.0" `
    --sbom-convert bin/generalization/sbom-convert.exe `
    --sbom-convert-version "0.0.8" `
    --cdx2spdx-jar bin/generalization/cdx2spdx.jar `
    --cdx2spdx-version "0.1.5" `
    --java "bin/generalization/jdk-21.0.12.1+1/bin/java.exe" `
    --java-version "21.0.12.1+1" `
    --sbom-utility bin/generalization/sbom-utility.exe `
    --sbom-utility-version "0.19.2"

# Verify sources, tool artifacts, runtime hashes, validator, and matrix
uv run python -m preservation_test.generalization.verification.verify_04_transformations

# Final pre-freeze integrity gate
uv run python -m preservation_test.generalization.verification.verify_05_freeze_02
