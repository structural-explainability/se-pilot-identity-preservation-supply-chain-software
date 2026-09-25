# Glossary

Key terms used in the project.

## Experimental Design and Execution

### Source and Target

The source is the preserved input document of a transformation.
The target is the document the converter generates from that source.

Source and target refer to the two sides of one transformation route.
They do not refer to an instance selected for testing.

### Execution Failure

An attempted planned route in which the converter exits nonzero or produces no
target document.

A target document that exists but fails validation is not an execution failure.

### Adjudication

Confirmation or rejection of a candidate preservation violation against the
frozen commitment and its authoritative sources, following the procedure in
`docs/en/run.md`.

Adjudication applies only to evaluator results with a `VIOLATED_*` verdict.
It does not assign, change, or relabel an evaluator verdict.

A candidate violation is confirmed only when:

1. the source PURL occupies the semantic role required by the frozen
   commitment;
2. the target representation supports that role;
3. the source and target components are validly associated under the frozen
   anchoring procedure; and
4. the target fails the frozen preservation obligation by dropping,
   relocating, or altering the PURL.

A confirmed violation is classified as rediscovered or new confirmed.
A candidate violation that does not survive adjudication is a false positive.

### Anchoring

The process of establishing correspondence between a source component and a
target component under the frozen component-matching procedure.

Anchoring uses evidence independent of the identifier whose preservation is
being evaluated.

For the initial PURL-preservation commitment, a source component corresponds
to a target component when they share a declared content hash, after the
frozen normalization of hash-algorithm labels and hash-value casing.
The PURL under evaluation is not used to establish correspondence.

The evaluator reports `UNANCHORABLE` when the source component has no usable
content hash, when no target component shares one, or when shared content
hashes resolve to more than one target component.

### Candidate Set

The set of artifacts mechanically enumerated from the frozen sampling frame
and available for eligibility screening.

Membership in the candidate set does not imply that an artifact is eligible
for the experiment or that it will become part of the held-out corpus.

The progression is:

```text
Sampling frame
    |
    v
Candidate set
    |
    v
Eligible candidates
    |
    v
Corpus
```

### Corpus

The set of artifacts selected for experimental use after application of the
predeclared sampling, eligibility, exclusion, and selection rules.

For the generalization experiment, the corpus is the frozen collection of
held-out source artifacts to which the declared transformation protocol is
applied.

Corpus membership is distinct from candidate enumeration and eligibility.

A candidate may be eligible without ultimately becoming a corpus member.

### Eligibility Rule

A predeclared condition that a candidate artifact must satisfy before it may
participate in corpus selection.

Eligibility establishes permission to be selected.
It does not perform selection.

Conceptually:

```text
Eligibility
    =
MAY be selected

Selection
    =
IS selected
```

Eligibility rules may arise from scientific requirements, methodological
controls, or implementation constraints.

### Eligible Candidate

A member of the candidate set that satisfies the predeclared eligibility
criteria and is permitted to participate in corpus selection.

Eligibility does not guarantee corpus membership.

An eligible candidate has passed the source-side screening requirements but
remains distinct from an artifact actually selected into the corpus.

### Freeze

The point at which a declared part of the experimental design, apparatus, or
interpretation procedure becomes fixed for the relevant experimental phase.

After freeze, the frozen element is not changed in response to downstream
experimental outcomes.

Depending on the stage of the study, frozen elements may include:

- sampling rules;
- corpus membership;
- preserved source artifacts;
- transformation implementations;
- tool versions;
- transformation routes;
- evaluation rules;
- adjudication rules; and
- verdict definitions.

A freeze establishes a temporal boundary between experimental design decisions
and evidence subsequently produced under those decisions.

### Generalization

The evidentiary purpose of applying the predeclared method beyond the material
used during development, debugging, engineering validation, or demonstration.

Generalization asks whether the method produces informative evidence when
applied under newly declared experimental conditions beyond those used to
develop or initially validate it.

Generalization is distinct from held-out status.

`Held-out` describes the relationship of evidence to prior development and
observation.

`Generalization` describes the purpose for which that evidence is being used.

### Held-Out

Describes experimental material whose relevant downstream behavior was not
used during development, engineering validation, or selection for the
generalization experiment.

Held-out status concerns the relationship between the material and prior
knowledge used to construct the experiment.

An artifact is not held out merely because it appears in a newly created
corpus.

If its relevant downstream behavior was already used to develop, debug,
validate, demonstrate, or select the method, it cannot serve the same
held-out evidentiary role.

### Rediscovery

Detection in held-out experimental material of a predeclared defect shape or
behavioral pattern that was established before execution of the
generalization experiment.

Rediscovery requires the relevant pattern to have been defined independently
of the held-out result.

An interesting behavior first recognized after examining held-out outcomes
must not be retroactively labeled a rediscovery.

Conceptually:

```text
Pattern established before held-out execution
        +
Pattern detected in held-out evidence
        =
Rediscovery
```

Rediscovery differs from post hoc discovery.
Any defect shape used to classify a held-out finding as rediscovered must be
recorded in `known/known_violations.toml` before Freeze 02.

### Result Classes

After evaluation and, for `VIOLATED_*` verdicts, adjudication, each evaluator
result belongs to exactly one result class:

- rediscovered: a confirmed violation matching a predeclared defect shape;
- new confirmed: a confirmed violation matching no predeclared defect shape;
- false positive: a `VIOLATED_*` verdict that does not survive adjudication;
- preserved: a `PRESERVED` verdict;
- expected or refused: an `UNSUPPORTED` or `NOT_APPLICABLE` verdict;
- underdetermined: an `UNDERDETERMINED` verdict; and
- unanchorable: an `UNANCHORABLE` verdict.

All result classes are reported explicitly; none are silently discarded.

### Sampling Frame

The bounded population from which candidate artifacts are permitted to be
enumerated for the experiment.

The sampling frame is defined before candidate selection and is part of the
experimental design.

For a repository-based frame, the repository identity alone is insufficient
for exact reproducibility when the repository can change over time.

The frame includes the fixed repository state required by the
sampling specification, including the declared revision.

The sampling frame should not be interpreted as necessarily statistically
representative of a broader real-world population unless such
representativeness is separately established.

### Semantic Target

The kind of identity information or semantic role required for the experiment
to apply.

The semantic target answers:

> What kind of information must be present for this experiment to test the
> declared preservation commitment?

For the initial pilot, the semantic target is PURL identity information in the
representation-specific semantic role required by the frozen commitment.

A valid SBOM may lack that information and be unsuitable for this
particular experiment without being invalid or defective as an SBOM.

The semantic target should not be confused with the independent evidence used
to establish correspondence between source and target components.

### Target Document Validation

The determination of whether a converter-generated target document conforms to
the declared target representation, using the declared target validator.

Target document validation is recorded separately from transformation
execution and from identity-preservation evaluation.

When the frozen evaluator can process the target document, evaluation proceeds
regardless of the validation result.

Validation never overrides, relabels, or modifies an evaluator verdict.
Validation result and evaluator verdict are reported as separate dimensions.

```text
Did the converter execute and produce a target document?
        |
        v
EXECUTION STATUS

Is the target document valid under its declared representation?
        |
        v
TARGET DOCUMENT VALIDATION

What happened to each source PURL?
        |
        v
EVALUATOR VERDICT

Does a VIOLATED_* verdict survive the frozen adjudication criteria?
        |
        v
ADJUDICATION
```

### Transformation Execution

The controlled invocation of a frozen transformation implementation on a
preserved source artifact according to a declared executable route.

Transformation execution occurs only after the relevant source material,
toolchain, versions, and transformation matrix have been fixed for the
experiment.

Execution produces experimental output and execution evidence.

Installation or acquisition of a transformation tool is not transformation
execution.
Similarly, a matrix row declared `unsupported_pre_execution` is not an
executed transformation and should not be interpreted as a transformation
failure.

### UNANCHORABLE

A verdict indicating that the evaluator cannot establish the required
source-to-target component correspondence under the frozen anchoring
procedure using the required independent evidence.

`UNANCHORABLE` does not mean that the source artifact is defective,
that the transformation implementation failed, or that the
identity-preservation commitment was violated.

Conceptually:

```text
Source component
        |
        v
Apply frozen anchoring procedure
        |
        +---------------------------+
        |                           |
        v                           v
Correspondence established    Correspondence not established
        |                           |
        v                           v
Continue evaluation              UNANCHORABLE
```

## Important Controlled Distinctions

The following terms describe different stages or properties and should not be
used interchangeably.

### Sampling Frame vs. Candidate Set

The sampling frame defines the bounded population the experiment is permitted
to consider.

The candidate set contains the artifacts actually enumerated from that frame
under the declared enumeration procedure.

```text
Sampling frame
    |
    | mechanical enumeration
    v
Candidate set
```

### Candidate vs. Eligible Candidate

A candidate has been enumerated.

An eligible candidate has additionally satisfied the predeclared eligibility
rules.

```text
Candidate
    |
    | eligibility screening
    v
Eligible candidate
```

### Eligible Candidate vs. Corpus Member

Eligibility means an artifact may be selected.

Corpus membership means it was selected.

```text
Eligible
    =
MAY be selected

Corpus member
    =
IS selected
```

### Held-Out vs. Generalization

`Held-out` describes the relationship of experimental material to prior
development and relevant prior observation.

`Generalization` describes the evidentiary purpose of applying the method to
that material.

An artifact can be described as held out because of how it was
treated before execution and as generalization evidence because of the role it
plays in the study.

### Semantic Target vs. Content-Hash Anchor

The semantic target is the kind of identity information or semantic role
required for the experiment.

A content-hash anchor is independent evidence used to establish correspondence
between source and target components.

```text
Semantic target
    =
WHAT identity information is under investigation

Content-hash anchor
    =
WHAT independent evidence supports component correspondence
```

For the initial pilot, PURL is the identity information under investigation.

The PURL under evaluation is not used to establish source-to-target component
correspondence.

### Anchoring vs. Target-Document Validation

Anchoring establishes correspondence between a source component and a target
component under the frozen component-matching procedure.

Target document validation determines whether the generated target SBOM
conforms to the declared target representation.

These are independent questions.

```text
Source component
    |
    | independent content-hash evidence
    v
ANCHORING
    |
    v
Corresponding target component

Generated target SBOM
    |
    | standards-aware validation
    v
TARGET DOCUMENT VALIDATION
```

Failure to establish source-to-target component correspondence may produce
`UNANCHORABLE`.

Failure of target document validation records that the generated SBOM is
invalid under the applicable target representation.

Neither condition should be confused with converter execution failure.

### Target Document Validation vs. Execution Success

Target document validation concerns whether a generated transformation output
conforms to the declared target representation.

Execution success concerns whether the declared transformation operation
completed and produced the expected output artifact.

A converter may execute successfully and still produce a target document that
fails validation.

A target document validation failure must not be classified as a converter
execution failure.

### Unsupported Route vs. Execution Failure

An unsupported route is identified before execution from the declared
capabilities of the transformation implementation.

An execution failure is an attempted planned route in which the converter
does not complete according to the execution-success criteria.

```text
unsupported_pre_execution
    =
route not attempted because declared capability does not support it

execution failure
    =
planned route was attempted but did not complete successfully
```

The distinction prevents known tool capability boundaries from being
misrepresented as execution failures.

### Unsupported Route vs. `UNSUPPORTED` Verdict

`unsupported_pre_execution` is a route status.
The converter's declared capability does not cover the source,
so the route is not executed.

`UNSUPPORTED` is an evaluator verdict.
The target format does not support the required PURL representation,
so loss is expected rather than counted as a violation.

The first concerns whether a transformation runs.
The second concerns a component within a transformation that did run.

### Execution vs. Evaluation vs. Adjudication

These terms describe distinct stages for each planned route that executes
successfully.
Adjudication applies only to `VIOLATED_*` evaluator verdicts.

```text
EXECUTION
Did the converter run and produce a target document?

        |
        v

TARGET DOCUMENT VALIDATION
Is the target document valid?
(recorded; does not gate evaluation when the evaluator can process the target)

        |
        v

EVALUATION
The frozen evaluator assigns a verdict to each source PURL.

        |
        v

ADJUDICATION
Does each VIOLATED_* verdict survive the frozen criteria?

        |
        v

RESULT CLASS
Rediscovered, new confirmed, false positive, or a
non-violation class.
```

Keeping these stages separate prevents execution status, target document
validity, anchoring limitations, evaluator verdicts, and adjudication outcomes
from being conflated.
Target document validation remains independent evidence,
and adjudication does not rewrite evaluator verdicts.

---

[◄ Back to Home](index.md)
