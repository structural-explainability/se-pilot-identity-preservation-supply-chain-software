# Generalization Experimental Design Provenance

<!-- markdownlint-disable MD024 -->

This document explains how the generalization experiment was designed, why its
boundaries were selected, and how those decisions became machine-readable and
executable study artifacts.

The purpose is not merely to document how to run the experiment.
It is to make the reasoning behind the experiment inspectable, teachable, reproducible, and extensible.

This document answers four questions:

1. Why was the experiment designed this way?
2. Which decisions are scientific, methodological, operational, or merely
   representational?
3. How were those decisions codified and executed?
4. How can another researcher reproduce or deliberately extend the experiment?

The central principle is:

> The configuration files did not design the experiment.
> Experimental decisions were developed first and then codified as structured data
> so that the same specification could be inspected by humans and applied
> deterministically by software.

## From Research Reasoning to Experimental Evidence

Earlier exploratory and engineering-validation work established that
security-relevant identity preservation could be investigated through
controlled transformations and evaluation.

That work also created an experimental-design problem.

Artifacts already used to develop, debug, validate, or demonstrate the method
could not provide strong evidence that the method generalized beyond the
material on which it had been developed.

The generalization experiment therefore required additional artifacts selected
without knowledge of their downstream transformation or evaluation outcomes.

At a high level:

```text
Prior exploratory and engineering-validation work
                         |
                         v
       Need evidence beyond development artifacts
                         |
                         v
              Need held-out material
                         |
                         v
      Need outcome-independent corpus construction
                         |
                         v
           Human experimental-design decisions
                         |
                         v
                 01-sampling.toml
              AUTHORED SPECIFICATION
                         |
                         v
          Deterministic Python processing
                         |
                         v
              Generated study artifacts
                         |
                         v
        Frozen transformation apparatus
                         |
                         v
                    Execution
                         |
                         v
              Observations and evidence
                         |
                         v
             Evaluation and adjudication
                         |
                         v
                     Verdicts
```

The distinction between authored and generated artifacts is fundamental.

The authored specifications record experimental commitments.

The software applies those commitments.

Generated artifacts record the consequences of applying them.

This separation makes it possible to distinguish decisions made during study
design from observations produced by the experimental machinery.

## Four Kinds of Design Choices

Not every declaration in an experimental specification has the same
methodological status.
The study distinguishes among four broad kinds of choices.

### Scientific or Semantic Requirements

Scientific or semantic requirements arise from what the experiment is trying
to investigate.

For example, the experiment concerns preservation of security-relevant package
identity information. A source artifact must therefore contain the kinds of
identity information necessary to perform the intended comparison.

A requirement for a usable PURL is an example.

The requirement for an independent content-hash anchor similarly supports
correspondence between components without relying exclusively on the identity
field whose preservation is under investigation.

Changing these requirements may change the scientific experiment itself.

### Methodological Controls

Methodological controls constrain how evidence enters and moves through the
experiment.

Examples include:

- fixing the sampling frame before generalization execution;
- fixing repository revisions;
- mechanically enumerating candidates;
- using predeclared eligibility rules;
- excluding material previously used during validation;
- prohibiting transformation outcomes from influencing corpus selection;
- prohibiting evaluator results from influencing corpus selection; and
- using deterministic selection procedures.

These controls do not define package identity.

They define how evidence about package identity is obtained and handled.

### Implementation Constraints

Implementation constraints arise from the capabilities of the frozen
experimental machinery.

The JSON-only boundary is an example.

The scientific question does not imply that XML or another SBOM serialization
is uninteresting. The current implementation operates on JSON, so JSON defines
the serialization scope of this experiment.

Supported SPDX and CycloneDX versions similarly reflect the formats and
versions the frozen machinery is prepared to interpret.

These boundaries should not be mistaken for claims that unsupported
representations are scientifically irrelevant.

### Representation Choices

Representation choices concern how experimental commitments are recorded.

Using TOML for the authored sampling specification is a representation choice.

The experiment could, in principle, have been represented using another
sufficiently precise structured format.

The representation does not determine the scientific result.

It determines how experimental commitments are stored, inspected, and consumed.

## Designing the Sampling Frame

The first corpus-construction problem was not simply:

> Where can we find some SBOMs?

Searching broadly for useful-looking SBOMs would leave substantial room for
researcher discretion.

Search terms, repositories examined, artifacts noticed, and decisions about
when enough examples had been collected could all influence the resulting
corpus.

Instead, the study required a bounded population from which candidates could
be obtained without first knowing their experimental outcomes.

### Problem

The experiment needed independently existing SBOM artifacts beyond those
already involved in development and engineering validation.

The population from which those artifacts could be selected needed to be
defined before downstream transformation behavior was examined.

### Decision

Official example repositories maintained by the CycloneDX and SPDX projects
were selected as the sampling frame.

Each repository was fixed at an exact Git revision.

### Rationale

The official example repositories provide public, independently maintained,
bounded collections of artifacts associated with the standards under
investigation.

Fixing exact Git revisions converts changing upstream repositories into a
reproducible sampling frame.

A later researcher can recover the repository contents available to this
experiment rather than obtaining whatever happens to exist upstream at a later
date.

### Limitation

The sampling frame is not claimed to be statistically representative of all
SBOMs used in production software supply chains.

The purpose is narrower.

The frame provides a bounded and reproducible source of additional artifacts
for determining whether the predeclared method can be applied beyond material
used during development and engineering validation.

The experiment therefore should not be interpreted as estimating the
prevalence of an observed behavior across all real-world SBOMs.

## Mechanical Candidate Enumeration

Defining the repositories is not sufficient.

A researcher could still browse those repositories manually and choose files
that appeared useful or interesting.

The experiment therefore separates definition of the sampling frame from
enumeration of the candidate set.

### Problem

Manual browsing would allow candidate discovery to depend on researcher
attention and judgment.

Even without deliberate outcome selection, researchers could preferentially
notice artifacts that appeared promising.

### Decision

Artifacts are enumerated mechanically from the fixed repository revisions.

Declared path and format rules are then applied to that enumeration.

### Rationale

Mechanical enumeration reduces researcher discretion.

The principle is:

> Human judgment designs the rule; deterministic computation applies the rule.

The progression is:

```text
Sampling frame
      |
      v
Mechanical enumeration
      |
      v
Candidate set
      |
      v
Eligibility screening
      |
      v
Eligible candidates
      |
      v
Predeclared selection
      |
      v
Held-out corpus
```

Membership in the candidate set does not imply eligibility or final corpus
membership.

It means only that the artifact was obtained from the predeclared sampling
frame according to the enumeration rules and is available for screening.

## Why JSON Is Required

The JSON requirement is an implementation boundary rather than a claim about
the scientific superiority of JSON.

### Scientific Requirement

The experiment requires structured SBOM artifacts containing identity
information capable of supporting the intended transformations and
comparisons.

### Implementation Constraint

The frozen experimental machinery operates on JSON representations.

### Consequence

Only JSON artifacts are eligible for this experiment.

This does not imply that XML or other SBOM serializations are unsuitable for
studying identity preservation.

A subsequent experiment could extend and validate equivalent machinery for
another serialization and repeat the protocol under a newly declared scope.

## Why Particular SPDX and CycloneDX Versions Are Accepted

The same distinction applies to supported specification versions.

The experiment requires SBOM identity information that the frozen source
adapter can interpret according to the declared protocol.

Accepted SPDX and CycloneDX versions therefore define the supported operational
scope of the frozen implementation.

They should not be interpreted as a claim that other versions are
scientifically unimportant.

```text
Scientific requirement
    |
    | Need interpretable SBOM identity information
    v
Frozen implementation
    |
    | Adapter supports declared formats and versions
    v
Eligibility rule
    |
    | Candidate must fall within that supported scope
    v
Eligible source artifact
```

## Why a PURL Is Required

The experiment does not investigate arbitrary textual preservation.

It investigates security-relevant identity semantics.

A Package URL (PURL) provides structured package identity information that can
include elements such as package type, namespace, name, version, qualifiers,
and subpath.

The experiment therefore requires source artifacts containing PURL information
suitable for the intended identity-preservation comparison.

This is primarily a semantic requirement.

An artifact can be a valid SBOM and still be unsuitable for this particular
experiment because it lacks the semantic target required by the experiment.

Eligibility for the study should therefore not be confused with general SBOM
quality or validity.

## Why an Independent Content-Hash Anchor Is Required

The experiment also requires an independent way to maintain correspondence to
the component whose identity information is being examined.

This matters because the PURL itself participates in the identity semantics
under investigation.

Reasoning that two components correspond merely because their PURLs correspond
could become circular when PURL preservation is itself being tested.

Conceptually:

```text
PURL
    |
    +-- identity information under investigation

Content hash
    |
    +-- independent evidence supporting component correspondence
```

Requiring both provides a stronger basis for controlled comparison than
relying solely on the field whose preservation is being examined.

The precise role of the content-hash anchor is defined by the frozen
transformation and evaluation protocol rather than by a universal claim that
content hashes establish every form of software identity.

## Why Selection Uses Source-Only Information

One of the most important controls in the generalization design is the
separation between corpus construction and downstream experimental outcomes.

Suppose candidates were transformed and evaluated before corpus membership was
decided.

The researcher could then know which artifacts:

- preserve identity information;
- fail to preserve it;
- produce unusual behavior;
- reproduce a previously observed defect shape; or
- produce otherwise interesting results.

Selecting the corpus with that information available would compromise the
interpretation of the generalization experiment.

The sampling specification therefore establishes an information boundary.

### Permitted Information

Corpus construction may use predeclared source-side information required by the
sampling and eligibility rules.

Examples include:

- source repository and path;
- source format and version;
- presence of required source identity information;
- content required for source-side eligibility determination;
- predeclared validation exclusions; and
- other information explicitly permitted by the frozen sampling procedure.

### Prohibited Information

Corpus construction must not depend on downstream experimental outcomes such
as:

- transformation output;
- evaluator output;
- observed preservation behavior;
- observed non-preservation behavior;
- whether a candidate reproduces a known defect shape; or
- whether a candidate produces an otherwise interesting result.

The principle is:

> The experiment should not choose its evidence because the researcher already
> knows what that evidence will say.

## Why Previous Validation Material Is Excluded

Artifacts or subjects already involved in development, debugging, engineering
validation, or demonstration have a different evidentiary status from genuinely
held-out material.

Once their behavior has been observed, they cannot become unseen again.

The sampling specification therefore records exclusions for previously used
material according to the frozen protocol.

```text
Development / engineering-validation evidence
                    |
                    | helped establish or test the method
                    v
            NOT HELD OUT

Held-out generalization evidence
                    |
                    | selected without downstream outcome knowledge
                    v
              GENERALIZATION
```

An excluded artifact may still provide valuable engineering or validation
evidence.

Its exclusion does not mean that the artifact is defective or scientifically
uninteresting.

It means that it cannot serve the specific evidentiary role assigned to
held-out generalization material.

## Prior Feasibility Inspection

The history of the experiment includes source-side feasibility inspection
performed before the generalization specification was frozen.

That history should be disclosed rather than erased from the methodological
record.

The relevant question is not whether researchers had literally seen the
repositories before.

The relevant question is:

> What information was available when the sampling design was established?

A bounded source-only feasibility inspection can answer questions such as:

- Are there artifacts in supported formats?
- Which declared specification versions occur?
- Are source documents present that contain the information required by the
  proposed experiment?
- Is the proposed experiment operationally feasible on this sampling frame?

That differs materially from examining:

- transformed artifacts;
- evaluator outcomes;
- preservation results; or
- candidate-specific evidence of the phenomenon under investigation.

The provenance record should therefore state both what prior inspection
occurred and what information that inspection did not expose.

## Why Fixed Git Revisions Matter

A repository URL alone does not identify a reproducible sampling frame.

Repositories change.

Files can be added, removed, renamed, corrected, or replaced.

If the study specified only a repository name, a later replication could
enumerate a different population.

Fixing the Git revision makes the sampling frame temporal as well as
structural:

```text
Repository
+
Exact revision
=
Recoverable sampling-frame state
```

The revision is therefore a reproducibility control.

## Why the Specification Is TOML

TOML is used as the representation for the authored sampling specification.

TOML organizes data primarily through:

- key/value pairs;
- tables;
- arrays; and
- arrays of tables.

A key/value pair records a value:

```toml
format = "json"
enabled = true
```

A table groups related values:

```toml
[sampling]
format = "json"
deterministic = true
```

A dotted table name expresses hierarchy:

```toml
[sampling.eligibility]
requires_purl = true
requires_hash = true
```

An array contains multiple simple values:

```toml
formats = ["spdx", "cyclonedx"]
```

An array of tables represents repeated structured objects:

```toml
[[sampling.repositories]]
name = "repository-a"
revision = "abc123"

[[sampling.repositories]]
name = "repository-b"
revision = "def456"
```

The double brackets are important.

A single-bracket table:

```toml
[thing]
```

describes one structured table or namespace.

A repeated double-bracket declaration:

```toml
[[thing]]
```

adds another structured object to an array.

Conceptually:

```text
[repository]
    ONE repository-like structure

[[repositories]]
    AN ITEM in a collection of repository structures
```

This makes arrays of tables useful for experimental objects such as
repositories, exclusions, transformations, or other repeated records whose
members have several properties.

## TOML and YAML

TOML and YAML can represent many of the same hierarchical data structures, but
they use different surface syntax.

A YAML representation might look like:

```yaml
sampling:
  repositories:
    - name: repository-a
      revision: abc123
    - name: repository-b
      revision: def456
```

A comparable TOML representation is:

```toml
[[sampling.repositories]]
name = "repository-a"
revision = "abc123"

[[sampling.repositories]]
name = "repository-b"
revision = "def456"
```

Both represent approximately:

```text
sampling
└── repositories
    ├── repository
    │   ├── name
    │   └── revision
    └── repository
        ├── name
        └── revision
```

YAML commonly represents hierarchy through indentation.

TOML commonly represents hierarchy through explicit table names and dotted
paths.

Neither representation is inherently more scientific.

For this study, TOML provides an explicit configuration-oriented syntax for an
artifact intended to be read by both researchers and Python.

## Why the Specification Is Data Rather Than Python

The sampling specification could have been embedded directly in Python code.

That would make the experimental commitments harder to distinguish from the
implementation responsible for applying them.

Instead, the architecture separates declaration from execution:

```text
01-sampling.toml
DECLARATION

"What has the experiment committed to?"

             |
             v

Python implementation
APPLICATION OF THE SPECIFICATION

"How are those commitments applied?"

             |
             v

Generated artifacts
OBSERVATION

"What resulted when those rules were applied?"
```

This separation improves auditability.

A reviewer can inspect the experimental specification without first
interpreting the implementation.

A developer can separately inspect the implementation and ask whether it
faithfully applies the specification.

A replication can preserve the experimental design while independently
reimplementing the machinery.

## Classification of Major Sampling Decisions

The major decisions can be understood according to their primary roles.

| Decision | Primary role |
| --- | --- |
| Use a held-out generalization corpus | Experimental-design decision |
| Use official example repositories | Sampling/design decision |
| Fix exact Git revisions | Reproducibility control |
| Mechanically enumerate repository contents | Methodological control |
| Apply predeclared eligibility criteria | Methodological control |
| Require suitable PURL information | Scientific/semantic requirement |
| Require a content-hash anchor | Experimental identification requirement |
| Exclude previously used validation material | Methodological control |
| Prohibit downstream outcomes during selection | Methodological control |
| Use deterministic selection | Methodological control |
| Restrict the frozen experiment to JSON | Implementation constraint |
| Restrict eligibility to supported specification versions | Implementation constraint |
| Represent the specification as TOML | Representation choice |
| Apply the specification using Python | Implementation choice |

These categories are explanatory rather than mutually exclusive.

A decision may serve more than one purpose.

## Why Converter Support Is Not a Corpus Eligibility Criterion

Compatibility with the selected transformation implementations is deliberately
not used to determine membership in the held-out corpus.

Corpus eligibility is determined from source-side properties under the frozen
sampling specification.

The transformation implementations are selected independently.

Only after both populations have been fixed are they crossed to construct the
transformation matrix.

```text
Eligible source population             Selected tool population
          |                                      |
          v                                      v
    Held-out corpus                      Frozen converters
          |                                      |
          +------------------+-------------------+
                             |
                             v
                    Complete cross-product
                             |
                             v
                Pre-execution capability check
                             |
                    +--------+--------+
                    |                 |
                    v                 v
             Supported route    Unsupported route
                    |                 |
                    v                 v
                 Execute        Record rationale
```

An unsupported route does not make the source artifact ineligible.

Likewise, it does not constitute a failed identity-preservation test.

It means only that the particular source/tool combination falls outside the
declared capabilities of that frozen implementation.

Had converter compatibility been imposed during corpus construction, the
selected corpus would have depended partly on the capabilities of the chosen
tools.

The study deliberately avoids that coupling.

This preserves two independently authored experimental choices:

1. what source evidence is eligible for the held-out corpus; and
2. what practically relevant transformation implementations are included.

Their interaction is observed only after both have been fixed.

# Transformation Toolchain

The Python code in the repository does not itself perform every software
supply-chain representation transformation examined by the experiment.

Some transformations require external software.

The external tools are therefore part of the experimental apparatus rather
than incidental software installed on the researcher's computer.

## Why External Tools Are Needed

The study asks what happens to identity-bearing information when an SBOM moves
between software supply-chain representations.

For example, a source artifact may begin as SPDX and be transformed to
CycloneDX, or begin as CycloneDX and be transformed to SPDX.

The Python code controls the experiment, preserves provenance, constructs
experimental records, and evaluates results.

It does not replace the independently developed transformation implementations
being examined.

```text
Source SBOM
    |
    v
External transformation implementation
    |
    v
Transformed SBOM
    |
    v
Study evaluator
    |
    v
Observation
    |
    v
Evaluation / adjudication
```

The study is not asking whether a converter written specifically for the study
can translate SPDX and CycloneDX.

It is examining identity preservation when existing SBOM tooling performs the
declared transformations.

## Selection of Transformation Implementations

The source SBOMs do not determine which transformation implementations must be
used.

An SPDX or CycloneDX document specifies its representation and content. It
does not prescribe the particular software implementation that must transform
it into another representation.

Selection of the transformation tools is therefore an independent experimental
design decision.

### Selection Objective

The pilot required a bounded set of practically relevant implementations with
which to construct an initial transformation matrix.

The objective was not to enumerate every SBOM transformation implementation in
existence.

Instead, the study selected established, frequently used tools that are put
into service for the kinds of SBOM operations being evaluated.

This provides a practically relevant starting population while keeping the
experimental matrix small enough to execute, inspect, and understand as a
pilot study.

The tool population is therefore:

- deliberately bounded;
- practically motivated;
- composed of independently developed implementations;
- large enough to exercise multiple transformation routes; and
- not claimed to be exhaustive or statistically representative of all SBOM
  tooling.

### Why Practical Use Matters

The experiment is intended to investigate behavior that can matter in actual
software supply-chain workflows.

For that reason, implementations already used for SBOM generation, conversion,
or related processing provide a practically relevant starting point.

Practical use is a reason for including an implementation in the experimental
population.

It is not evidence that the implementation is correct.

### Why Multiple Implementations Are Included

A single implementation would provide only one realization of the
transformation behavior under study.

Including several independently developed tools allows the same general
identity-preservation question to be examined across different
implementations and transformation routes.

The purpose is not to rank the tools.

The purpose is to determine whether the experimental method can produce useful
evidence across a sufficiently varied initial set of real implementations to
justify broader investigation.

## Why This Is a Pilot Matrix

The transformation matrix is intentionally finite.

Every additional tool increases the number of experimental units, provenance
records, transformation routes, outputs, and results that must be controlled
and interpreted.

A pilot therefore benefits from beginning with a bounded matrix that is large
enough to expose the method to implementation variation without attempting an
exhaustive survey.

The pilot asks whether the approach is promising enough to justify broader
replication.

It does not attempt to answer every possible question about every available
SBOM implementation.

## Selection of Tool Versions

After selecting the transformation implementations, the study also had to
select which versions would participate.

The pilot uses recent versions available during experimental preparation.

The study did not search backward through historical releases to identify
versions producing particular preservation behaviors.

This creates two separate selection decisions:

```text
Tool selection
    |
    | Which practically relevant implementations should be included?
    v
Selected tool population
    |
    | Which release of each should be tested?
    v
Recent available versions
    |
    v
Frozen toolchain
```

The version-selection objective is practical relevance rather than historical
coverage.

The pilot asks how the selected implementations behave in recent frozen
versions, not how their behavior evolved across their complete release
histories.

## Why Historical Versions Are Not Included

A historical version study would answer a different question.

It could investigate:

- when a particular behavior first appeared;
- when a defect was corrected;
- whether identity-preservation behavior changed between releases; or
- whether a regression occurred.

Those are useful questions, but they are outside the scope of this
generalization pilot.

Searching backward through releases after observing current behavior could
also introduce additional researcher discretion.

The pilot therefore does not perform retrospective version hunting.

Instead:

```text
Select practically relevant implementation
        |
        v
Select recent available release
        |
        v
Freeze exact version
        |
        v
Record executable provenance
        |
        v
Execute the declared experiment
```

A result obtained from a frozen tool version directly establishes evidence
only for that tested version under the declared experimental conditions.

It should not automatically be generalized to every historical or future
release of the project.

## Construction of the Transformation Matrix

The held-out corpus and the selected converter population are chosen
independently.

They are then crossed to form the declared transformation matrix.

The current design contains:

```text
10 held-out corpus members
        ×
3 converter implementations
        =
30 declared matrix rows
```

The two primary crossed dimensions are therefore:

1. source corpus member; and
2. converter implementation.

Transformation direction is not a third fully independent factorial dimension.

The source representation determines the required direction:

```text
SPDX source
    |
    v
SPDX -> CycloneDX

CycloneDX source
    |
    v
CycloneDX -> SPDX
```

Converter capabilities then determine whether each resulting matrix cell is
executable.

## Supported and Unsupported Matrix Routes

The complete 10 × 3 cross-product contains 30 declared rows.

Of these:

```text
30 total matrix rows
20 planned executable routes
10 unsupported_pre_execution routes
```

The unsupported rows remain part of the matrix.

They are not silently deleted.

### Eight Unsupported Protobom Routes

Eight held-out source artifacts are CycloneDX documents whose versions fall
outside the declared JSON input-version support of the frozen Protobom
implementation.

For those artifacts:

```text
8 CycloneDX sources
    ×
Protobom
    =
8 unsupported_pre_execution rows
```

These rows are unsupported because of the declared source-version capability
of the frozen converter.

They are not transformation failures.

The transformation is not executed.

### Two Unsupported `cdx2spdx` Routes

Two held-out source artifacts are SPDX documents.

The selected `cdx2spdx` implementation performs the CycloneDX-to-SPDX
direction.

Applying it to an SPDX source would require the opposite transformation
direction.

Therefore:

```text
2 SPDX sources
    ×
cdx2spdx
    =
2 unsupported_pre_execution rows
```

Again, these are not failed preservation tests.

They are source/tool combinations outside the declared direction supported by
the frozen implementation.

### Complete Arithmetic

```text
CycloneDX sources:

8 sources × 3 converters = 24 matrix rows
8 × 2 supported routes   = 16 executable
8 × 1 unsupported route  =  8 unsupported


SPDX sources:

2 sources × 3 converters = 6 matrix rows
2 × 2 supported routes   = 4 executable
2 × 1 unsupported route  = 2 unsupported


TOTAL:

30 matrix rows
20 planned executable routes
10 unsupported_pre_execution routes
```

The structure can be summarized as:

```text
SOURCE ARTIFACT
    |
    +-- source standard
    +-- source specification version

CONVERTER
    |
    +-- supported input standards
    +-- supported input versions
    +-- supported transformation direction

             |
             v

       ROUTE FEASIBILITY
```

A matrix cell exists because the complete cross-product is declared.

Whether the cell is executable is then determined from pre-execution
capability information rather than from observed preservation behavior.

The term `unsupported` is preferred to `impossible`.

A different tool version or implementation might support the route in another
experiment.

The statement is only that the route is unsupported under the frozen
conditions of this experiment.

## Why Unsupported Routes Were Not Removed During Sampling

It would have been possible to require every source artifact to be compatible
with every selected converter.

That would have changed the meaning of the held-out corpus.

The capabilities of the selected tools would have reached backward into source
selection and shaped the evidence population.

Instead:

```text
SAMPLING

Fixed sampling frame
        |
        v
Mechanical enumeration
        |
        v
Source-side eligibility
        |
        v
Held-out corpus

NO CONVERTER CAPABILITY USED TO SELECT THE CORPUS


TRANSFORMATION DESIGN

Held-out corpus
        ×
Preselected converter population
        |
        v
Complete matrix
        |
        v
Pre-execution capability determination
        |
        +---------------------+
        |                     |
        v                     v
Supported route        Unsupported route
        |                     |
        v                     v
Execute                Record reason
```

This keeps source selection and tool selection independent until the matrix is
constructed.

## Acquisition of the External Toolchain

The external experimental apparatus must itself be reproducible.

A command such as:

```text
convert this SBOM
```

does not completely specify an experiment.

Different tools can implement the same nominal conversion differently.

Different releases of the same tool can also behave differently.

The relevant experimental condition therefore includes:

```text
source representation
        +
target representation
        +
transformation implementation
        +
exact implementation version
        +
required runtime
        +
executable identity
```

## Why PowerShell Is Used

The repository uses PowerShell to acquire and prepare the external
experimental toolchain.

This responsibility differs from the role of the Python study logic.

Tool acquisition requires operating-system-oriented operations such as:

- downloading release artifacts;
- selecting appropriate Windows release assets;
- expanding archives;
- locating executables;
- placing them into controlled local paths;
- obtaining required runtimes;
- cleaning temporary installation files; and
- computing cryptographic hashes.

The language boundary therefore corresponds to a responsibility boundary:

```text
TOML
    declares experimental data and commitments

Python
    derives study artifacts and executes/evaluates the protocol

PowerShell
    constructs the pinned external executable environment

External tools
    perform their declared experimental or supporting operations
```

PowerShell does not determine preservation verdicts.

It prepares the apparatus used later in the experiment.

## Why the Tools Are Repository-Local

The tools are placed in a controlled repository-local location rather than
obtained opportunistically from the operating-system `PATH`.

Without that boundary:

```text
Python
   |
   v
"tool-name"
   |
   v
Operating-system PATH lookup
   |
   v
unknown installation
```

With a repository-local toolchain:

```text
Python
   |
   v
declared repository-local executable
   |
   v
known version
   |
   v
known executable bytes
```

This reduces dependence on ambient machine state.

## Why Exact Versions Are Pinned

A tool name without a version would make the experiment unstable over time.

A later release could contain:

- bug fixes;
- parser changes;
- serialization changes;
- dependency changes;
- identity-handling changes; or
- new transformation behavior.

A replication using whatever version happened to be current would therefore
not necessarily use the same experimental apparatus.

Each external tool is consequently pinned to an explicit release.

## Why Cryptographic Digests Are Recorded

A version string identifies a named release.

A cryptographic digest identifies the bytes of a particular acquired artifact
with substantially greater specificity.

Conceptually:

```text
Version
    "Which declared software release is this?"

Digest
    "Which exact bytes were used?"
```

Both forms of identity are useful.

The version communicates software-release identity to a human reader.

The digest supports verification of the actual experimental artifact.

## Java Is a Runtime Dependency

Java has a different status from the independently selected SBOM tools.

It was not selected as another transformation implementation.

It enters the experiment because a selected implementation requires it.

The causal chain is:

```text
Select transformation implementation
        |
        v
Implementation requires Java
        |
        v
Java becomes part of the executable environment
        |
        v
Select and freeze an exact Java distribution and version
```

Java therefore requires a reproducibility rationale rather than an independent
tool-population rationale.

The runtime must be controlled because it participates in execution of the
selected converter.

## `sbom-utility`: Target-Document Validation

CycloneDX `sbom-utility` is part of the frozen generalization apparatus as the
independent validator applied to generated target SBOMs before preservation
evaluation.

It is not one of the three converter implementations defining the 10 × 3
transformation matrix.

Its role is therefore distinct from transformation:

```text
Source SBOM
    |
    v
Selected converter
    |
    v
Generated target SBOM
    |
    v
sbom-utility validation
    |
    +-- valid ------> study evaluation
    |
    +-- invalid ----> retain validation evidence;
                      no preservation verdict
```

This separation prevents a structurally invalid generated document from being
interpreted as evidence that an identity-preservation commitment was violated.

The study therefore distinguishes three questions:

```text
Did the declared transformation execute?
        |
        v
EXECUTION STATUS

Is the generated target valid under its declared representation?
        |
        v
TARGET-DOCUMENT VALIDATION

What happened to the declared identity relation?
        |
        v
PRESERVATION EVALUATION
```

`sbom-utility` belongs to the validation apparatus rather than the converter
population.

Its exact version and executable digest are recorded as part of the
pre-execution transformation plan and verified before Freeze 02.

## Installation Is Not Experimental Execution

Acquiring the external toolchain does not itself test identity preservation.

It prepares the apparatus required for later execution.

The study therefore prepares two independently controlled inputs:

```text
WHAT WILL BE TRANSFORMED
        +
WHAT WILL TRANSFORM IT
```

The sampling and source-preservation stages establish the first.

The external-tool acquisition procedure establishes the second.

Only later are they joined in the transformation matrix.

# Reading the Experimental Artifacts as a Provenance Chain

The numbered artifacts should not be understood merely as a sequence of files.

They form a provenance chain.

At a high level:

```text
RESEARCH REASONING
Why should the experiment be designed this way?

        |
        v

01-sampling.toml
AUTHORED SAMPLING SPECIFICATION
What sampling rules have been declared?

        |
        v

PYTHON
DETERMINISTIC APPLICATION
Apply the declared sampling rules.

        |
        v

02-candidates.toml
CANDIDATE SCREENING
What candidates were encountered and what happened during screening?

        |
        v

03-corpus.toml
CORPUS MEMBERSHIP
Which eligible artifacts became members of the held-out corpus?

        |
        v

04-sources.toml
SOURCE PROVENANCE
What exact source artifacts constitute the preserved experimental material?

        |
        v

05-transformations.toml
TRANSFORMATION MATRIX
Which source/tool combinations constitute the declared transformation space,
and which routes are supported before execution?

        |
        v

TRANSFORMATION EXECUTION
What happened when each executable route was run?

        |
        v

OBSERVATION
What evidence was produced?

        |
        v

EVALUATION
What does the evidence show relative to the declared identity commitment?

        |
        v

ADJUDICATION
Which predeclared decision rule applies?

        |
        v

VERDICT
What formal classification follows?
```

The exact derivation of each artifact should be documented against the Python
module or other implementation responsible for producing it.

The design-provenance document explains why each stage exists.

Module docstrings explain exactly how each stage is implemented.

## The Role of AI in Creating the Specification

AI assistance may contribute to drafting, critique, implementation, checking,
or explanation of an experimental specification.

AI-generated text or code does not itself establish an experimental
commitment.

The substantive commitments in the authored specification remain research
decisions requiring human review and acceptance.

The relevant provenance distinction is therefore not simply:

```text
human-written
versus
AI-written
```

A more useful model is:

```text
Proposed or drafted
        |
        v
Examined against the research question,
prior evidence, sources, and methodology
        |
        v
Accepted as an experimental commitment
        |
        v
Codified in the authored specification
```

AI can assist at several points in that process.

It does not replace the need to identify why a declaration exists, what
evidence supports it, what assumptions it introduces, or what consequences it
has for interpretation.

This is especially important for a frozen experiment because an apparently
minor configuration value can become a methodological commitment once accepted
into the frozen specification.

# Intended Replication and Extension

The boundaries of this pilot define the experiment that was performed.

They do not define the limits of the underlying phenomenon.

The study deliberately uses a finite:

- sampling frame;
- held-out corpus;
- serialization;
- set of SBOM specification versions;
- transformation-tool population; and
- set of frozen tool versions.

These boundaries make the experiment reproducible and interpretable.

They should not be interpreted as claims that other artifacts, formats, tools,
or versions are unimportant.

If the pilot produces promising results, additional experiments are explicitly
encouraged.

## Replicate With Different Source Populations

A subsequent study could construct a new sampling frame from different sources
of independently existing SBOMs.

This would test whether the findings persist beyond the official example
repositories used by the present pilot.

## Replicate With Different Tools

A subsequent study could repeat the experiment with a different population of
SBOM transformation implementations.

This would test whether observed identity-preservation behavior extends beyond
the implementations selected for the initial matrix.

A larger study could also substantially increase the number of implementations
and transformation routes.

## Replicate With Different Serializations

The present implementation is restricted to JSON.

A subsequent experiment could implement and validate equivalent procedures for
XML or another supported SBOM serialization.

This would test whether the findings persist when representation syntax
changes while the relevant identity semantics remain under examination.

## Replicate Across Tool Versions

The present pilot uses recent frozen versions rather than constructing a
historical version matrix.

A subsequent study could pre-declare a range of releases for one or more tools
and apply the same cases across those releases.

Such an experiment could investigate:

- when particular behaviors appeared;
- when they disappeared;
- whether corrections persisted;
- whether regressions occurred; and
- how identity-preservation behavior evolved over time.

## Replicate With Broader Specification-Version Coverage

The present experiment operates within explicitly supported SPDX and
CycloneDX versions.

Future implementations could broaden that support and repeat the experiment
across additional specification versions.

## Change Experimental Boundaries Deliberately

Where practical, subsequent experiments can preserve most of the existing
protocol while deliberately changing a specific experimental dimension.

For example:

```text
CURRENT PILOT

official example repositories
        +
JSON
        +
bounded practical tool population
        +
recent frozen tool versions
        +
current supported specification versions
        |
        v
RESULT
```

A subsequent experiment might change the source population:

```text
SAME GENERAL METHOD

DIFFERENT source population
same serialization
same tools
same tool versions
        |
        v
REPLICATION RESULT
```

Another might change serialization:

```text
SAME GENERAL METHOD

comparable source-selection procedure
XML instead of JSON
same conceptual identity question
        |
        v
SERIALIZATION REPLICATION
```

Another might change the implementation population:

```text
SAME GENERAL METHOD

comparable held-out corpus
same serialization
DIFFERENT tool population
        |
        v
IMPLEMENTATION REPLICATION
```

Changing one boundary at a time is not an absolute requirement for all future
work, but it can make the source of additional evidence easier to interpret.

## Unsupported Routes Suggest Follow-Up Experiments

The unsupported cells in the present matrix are not failed experiments.

They identify boundaries of the frozen implementations.

Those boundaries can themselves motivate subsequent work.

For example, another experiment could select implementations with broader
version or directional support and determine whether the expanded matrix
produces consistent identity-preservation evidence.

The appropriate response to an interesting boundary is not to alter the frozen
pilot after observing it.

It is to formulate that boundary as a question for another experiment.

## A Pilot Is Not Intended to Finish the Question

The objective of the pilot is not to demonstrate that its findings hold for
every SBOM, converter, serialization, specification version, and software
release.

Such a claim would require evidence far beyond the scope of this study.

Instead, the pilot asks whether a finite, predeclared, reproducible experiment
can produce sufficiently informative evidence to justify broader testing.

If it does:

```text
Bounded pilot
      |
      v
Promising evidence?
      |
      +---- no ----> Document the result and its limits
      |
     yes
      |
      v
Additional experiments
      |
      +-- different artifacts
      +-- different tools
      +-- different serializations
      +-- different versions
      +-- broader environments
      |
      v
Does the finding persist?
```

The strength of the research should grow through additional predeclared
experiments rather than by continuously enlarging the original experiment
after observing its results.

# Reproducibility Before Universality

The guiding principle is:

> First make one bounded experiment understandable, reproducible, and
> auditable. Then test how far its findings extend.

The present pilot establishes that bounded experimental unit.

Its finite boundaries are a feature of the design, not an assertion that the
phenomenon stops at those boundaries.

If the results warrant further investigation, the study is intended to provide
enough specification, provenance, terminology, and executable machinery for
other researchers to reproduce the experiment and deliberately challenge its
boundaries.

# Documentation Architecture

The repository should preserve complementary levels of documentation.

## README

The README provides the operational entry point.

It should answer:

> How do I run this study?

## Experimental Design Provenance

This document explains the reasoning that produced the experimental
specifications and the provenance chain connecting authored decisions to
generated evidence.

It should answer:

> Why was the study constructed this way?

## Glossary

The glossary defines the controlled terminology used throughout the study.

It should answer:

> What does this term mean in this study?

## Module and Script Documentation

Python module docstrings and PowerShell documentation describe the
implementation responsible for each derivation, acquisition, or execution
stage.

They should answer:

> How does the software perform this particular step?

Together, these layers allow another researcher to do more than rerun the
existing experiment.

They make it possible to understand, critique, replicate, modify, and extend
the experimental design.

# Core Provenance Principle

The most important relationship in the generalization experiment is not merely:

```text
01 -> 02 -> 03 -> 04 -> 05 -> ...
```

It begins one level earlier:

```text
Research reasoning
        |
        v
Explicit experimental decisions
        |
        v
Authored machine-readable specifications
        |
        v
Deterministic computation
        |
        v
Generated artifacts
        |
        v
Frozen experimental apparatus
        |
        v
Experimental evidence
        |
        v
Predeclared interpretation
```

Every important transition should be explainable.

For every important value in an authored specification, the study should be
able to answer:

> Why is this here?

For every generated value downstream, the study should be able to answer:

> What upstream information and deterministic procedure produced this?

For every external tool, the study should be able to answer:

> Why was this implementation selected, what exact version was used, and what
> role does it have in the experiment?

For every unsupported matrix cell, the study should be able to answer:

> What pre-execution capability rule makes this route unsupported?

For every boundary, the study should be able to answer:

> Is this boundary scientific, methodological, operational, or merely a
> representation choice?

And for every important boundary left unexplored, the study should make it
possible to ask:

> What new experiment would test whether the finding persists when this
> boundary changes?

That provenance is what allows the experiment to be inspected rather than
merely trusted.

<!-- markdownlint-enable MD024 -->

---

[◄ Back to Home](index.md)
