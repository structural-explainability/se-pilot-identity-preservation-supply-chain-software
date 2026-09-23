# Generalization Directory README.md

## Background

Software can contain vulnerabilities.

A vulnerability may originate in application code, in a directly imported package,
or in one of the many transitive dependencies brought into a system indirectly.
Modern software therefore inherits part of its security risk from the larger software
ecosystem on which it depends.

This becomes particularly important when a vulnerable component is widely reused.
A security-relevant defect introduced into a popular package can propagate into many
applications, services, containers, and products that depend on it.
The affected software may be distributed further, incorporated into other systems,
and remain in use long after the original package has changed.

As software systems and dependency graphs grew, manually identifying every component
and determining whether it was affected by a known vulnerability became impractical.
The software ecosystem needed machine-processable ways to answer questions such as:

- What software components are present?
- Which versions are present?
- Where did those components come from?
- Which other components do they depend on?
- Are any of those components associated with known vulnerabilities?
- Does a reported vulnerability actually apply to the component in this particular
  software artifact?

### Software Bills of Materials

A Software Bill of Materials, or **SBOM**, provides a machine-readable inventory of
software components and related metadata.

An SBOM is often described as an ingredient list for software.
Depending on the format, producer, and purpose, it may record information such as:

- package or component names
- versions
- package URLs (PURLs)
- cryptographic hashes
- suppliers or authors
- licenses
- dependency relationships
- external references
- provenance information

SBOM standards such as **CycloneDX** and **SPDX** provide structured representations
for recording this information.

The standards overlap substantially, but they are not identical.
They use different data models, fields, relationships, conventions,
and ways of expressing some forms of component identity.

For this study, those **identity-bearing elements** are especially important.

A package name, version, PURL, digest, qualifier, repository reference,
or related attribute may help determine whether two records refer to
the same software entity for a particular downstream security operation.

This study focuses on preserving the information needed to maintain
the **relevant software identity** across representations.

### Vulnerability Identification and Matching

Known software vulnerabilities are commonly assigned identifiers such as
**Common Vulnerabilities and Exposures (CVE)** identifiers.

Vulnerability databases and security advisories associate these vulnerability records
with information intended to describe the affected software.
Vulnerability-scanning tools then attempt to determine
whether components found in an application, container, SBOM, or
other software artifact correspond to software affected by those records.

This is not as easy as a text search for a component name.
A scanner may need to reason about combinations of information such as:

- package ecosystem
- package name
- namespace
- version
- package URL
- qualifiers
- repository location
- distribution or operating-system information
- cryptographic digest
- dependency context
- vulnerability-specific applicability constraints

The result depends on how the tool determines
**which software entity a piece of metadata refers to**.

### Different Tools, Different Representations

Different tools also build and interpret software inventories in different ways.

An SBOM generator may inspect package-manager metadata, source repositories, build
artifacts, installed files, container images, lock files, or combinations of those
sources.

A vulnerability scanner may emphasize somewhat different information because its
primary objective is not merely to describe the software but to determine whether
known vulnerabilities apply to it.

Consequently, two tools examining the same software may produce representations that
are both useful and standards-conformant while differing in:

- which components are included
- how components are named
- which identifiers are recorded
- which hashes or qualifiers are retained
- how dependency relationships are represented
- how package ecosystems are encoded
- which identity attributes are considered relevant for downstream matching

Differences are not necessarily errors.
Different tools and standards can be designed for
different operational purposes.

The security concern arises when **identity-relevant information** crosses
those boundaries and the receiving tool depends on that information
to **recognize the same software entity**.

The question is whether the information required for the relevant
**downstream identity decision** survives the transition.

### Translation and Identity Preservation

Software supply-chain information is frequently converted between formats and tools.

For example, an SPDX SBOM may be translated into CycloneDX, or a CycloneDX document
may be converted into SPDX so that it can be consumed by another tool or workflow.

A translated document can remain completely valid according to its destination
schema while nevertheless changing, omitting, relocating, normalizing, or
reinterpreting information that another security process relies upon.

This creates an important distinction:
**syntactic validity does not guarantee preservation of security-relevant identity.**

If an identifier, qualifier, digest, repository reference, or other identity-bearing
attribute changes during translation, a downstream vulnerability scanner may no
longer interpret the translated component as the same software entity represented
by the source artifact.

The resulting failure may not appear as a malformed file or conversion error.
Instead, it may appear later as a missed vulnerability match, an incorrect
applicability decision, or disagreement between security tools.

That is the problem setting driving this pilot study.

## Project Goals

The broader project examines whether software supply-chain translation programs
preserve the information needed to maintain **security-relevant operational identity**
as artifacts move between formats, representations, and tools.

Software supply-chain artifacts such as SBOMs may be translated
from one representation to another while remaining syntactically valid.
A successful parse, however, does not necessarily mean that all
security-relevant meaning has been preserved.

A translation may change, omit, relocate, normalize, or reinterpret
information used to identify software.

That matters when downstream tools rely on that information for functions such as:

- vulnerability matching
- vulnerability applicability decisions
- package and component identification
- provenance
- dependency interpretation
- other security-relevant decisions

The project asks whether the translated artifact
still provides the information required to identify
the **same relevant software entity**
for the downstream security operation.

The experiment applies the operational-identity commitments
and evaluator defined earlier in the study to test that preservation directly.

## Engineering Validation and Generalization

The study separates **engineering validation**
from the formal **generalization experiment**.

Engineering validation was used to determine
whether the experimental machinery behaved as intended.
This included checking the commitments, evaluator, source adapters,
transformation procedures, and supporting implementation
against known or deliberately examined examples.

Those materials were therefore visible during development and validation.

They are useful for establishing that the method works mechanically, but they are not held-out evidence of generalization.

The generalization experiment asks a different question:

> What happens when the already-defined method is applied to
> software supply-chain artifacts that were not used to develop or validate it?

The generalization corpus is selected
from previously unused material
and is fixed **before transformation outcomes are examined**.

This creates a clear separation between constructing the method
and testing how it behaves on new material.

## Generalization Experiment Objectives

The generalization experiment addresses three related questions:

1. Can the method represent and evaluate
   **security-relevant identity preservation**
   on previously unused software supply-chain artifacts?

2. Does the method reveal the same or new
   **identity-preservation behavior**
   when applied to held-out artifacts?

3. Is the method specified **clearly and concisely enough**
   to be applied reproducibly without relying on
   **unstated investigator judgment**?

The experiment may provide evidence about both the behavior
of the translation programs and the usability and reproducibility
of the experimental method itself.

## Experimental Intent

The generalization experiment is designed to reduce opportunities
for investigator discretion after outcomes become visible.

Before any generalization transformations are run:

- the sampling frame is fixed
- eligibility and exclusion rules are fixed
- the held-out corpus is selected mechanically
- exact source bytes are preserved
- transformation routes are defined
- the evaluator remains fixed
- the relevant identity commitments remain fixed

This ordering is important.
The corpus is selected first.
Transformation behavior is observed only afterward.

## Source-Only Selection

Corpus selection uses **source-side information only**.
Source-side information is information
available in the original artifact
**before** any experimental transformation has been performed.

Examples include:

- source standard
- source specification version
- subject identity
- canonical package identifiers
- available content-hash anchors
- declared package ecosystem
- source provenance
- predeclared engineering-validation exclusions

These properties may be used to determine
whether an artifact belongs in the sampling frame,
satisfies the eligibility requirements,
or belongs to the same predeclared selection unit as another candidate.

Selection does **not** use information
produced by the generalization experiment.

In particular, corpus selection does not use:

- transformation outputs
- evaluator outputs
- observed preservation behavior
- known transformation-specific failure behavior
- whether an artifact appears likely to produce a violation
- whether a candidate would make the experimental results appear stronger or weaker

This separation helps prevent outcome-aware selection.
The corpus is fixed first, and only then are
the declared transformations executed and evaluated.

## Interpreting Generalization Results

The experiment is not designed to search for examples that make the method appear successful.
Once the corpus and experimental procedure are fixed, several outcomes are possible.

The experiment may show:

- preservation of the required identity information
- nonconformance with a declared identity-preservation commitment
- rediscovery of behavior already observed during engineering validation
- previously unobserved identity-preservation behavior
- limitations in a transformation route
- limitations in the evaluator or experimental method
- cases in which the available information is insufficient for a determination

Previously known behavior is not presented as new evidence merely
because it appears again in the held-out corpus.
Such cases are treated as **rediscovery**.

The purpose of the generalization experiment is to give the fixed method
a fair opportunity to succeed, fail, reproduce known behavior,
or reveal limitations when applied to held-out material.

## Organization

The numbered TOML files record the generalization preparation in execution order.

The files and preserved artifacts in this directory
are the **authoritative source of truth** for sampling, selection, provenance, transformations, and experimental results.

This README explains the purpose and structure of the experiment.
It does not duplicate the detailed scientific records maintained in those files.

```text
01-sampling.toml
02-candidates.toml
03-corpus.toml
04-sources.toml
05-transformations.toml
sources/
results/
```

The preparation stages establish the sampling rules, candidate inventory,
selected corpus, preserved source artifacts, and declared transformation routes.

The `sources/` directory contains the exact preserved input bytes
used by the formal experiment.

The `results/` directory is reserved for generated targets,
evaluator outputs, logs, and other experimental evidence produced only
after the generalization preparation has been frozen and execution begins.
