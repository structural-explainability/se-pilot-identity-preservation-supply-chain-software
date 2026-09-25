# Glossary

Key terms used in the project.

## Experimental Design and Execution

### Adjudication

Application of predeclared decision rules to experimental evidence to assign a
formal verdict or classification.

Adjudication may be performed automatically when the decision rules are
sufficiently explicit and machine-executable.

Adjudication is distinct from observation and evaluation.

The intended sequence is:

```text
Observation
    |
    v
Evaluation
    |
    v
Adjudication
    |
    v
Verdict
```

An observation records what occurred.

Evaluation determines how the observation relates to the declared experimental
commitment or criterion.

Adjudication applies the predeclared decision rules.

The verdict is the resulting formal classification.

### Anchoring

The process of locating and selecting a target anchor within an artifact under
the predeclared eligibility and target-selection rules.

Anchoring identifies the particular instance on which the experiment will
operate.

Anchoring should not be confused with the semantic target itself.

The semantic target defines what kind of information or structure is required.

Anchoring determines which specific instance of that target is selected in a
particular artifact.

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

A predeclared condition that a candidate artifact or potential target instance
must satisfy before it may participate in the corresponding stage of the
experiment.

Eligibility establishes permission to be selected.

It does not itself perform selection.

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
criteria and is therefore permitted to participate in corpus selection.

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
- target-selection rules;
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

### One-Term Transformation

A controlled transformation in which one declared identity-relevant term is
changed while the relevant counterpart and other controlled features are held
fixed according to the experimental protocol.

A `term` is a semantic element of the identity relation under examination.

It is not necessarily a single textual token, character sequence, field, or
syntactic unit.

The purpose of a one-term transformation is to isolate the effect of a
declared identity-relevant difference sufficiently to support interpretation
under the corresponding commitment.

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

Rediscovery therefore differs from post hoc discovery.

### Sampling Frame

The bounded population from which candidate artifacts are permitted to be
enumerated for the experiment.

The sampling frame is defined before candidate selection and is part of the
experimental design.

For a repository-based frame, the repository identity alone is insufficient
for exact reproducibility when the repository can change over time.

The frame therefore includes the fixed repository state required by the
sampling specification, including the declared revision.

The sampling frame should not be interpreted as necessarily statistically
representative of a broader real-world population unless such
representativeness is separately established.

### Semantic Target

The kind of information, relation, or structure required by the experiment.

The semantic target answers:

> What kind of thing must be present for this experiment to operate?

It does not identify the particular instance within a specific artifact.

For example, an experiment may require identity-bearing package information of
a declared kind.

That requirement describes the semantic target.

The particular component selected from a particular SBOM is the target anchor.

Thus:

```text
Semantic target
    =
WHAT kind of information or structure is required

Target anchor
    =
WHICH specific instance is selected
```

### Target Anchor

The specific instance of the semantic target selected within an experimental
artifact according to the predeclared anchoring rules.

A target anchor must satisfy the applicable eligibility and target-selection
requirements.

The target anchor provides the concrete experimental subject on which the
declared transformation and evaluation operate.

The term should not be confused with other uses of `anchor`, such as an
independent content-hash anchor used to establish component correspondence.

### Target Validity

Whether a selected target anchor actually satisfies the requirements declared
for a valid experimental target.

Target validity is evaluated separately from transformation execution success
and separately from the eventual preservation verdict.

This distinction prevents an invalidly selected target from being interpreted
as evidence about the identity-preservation hypothesis.

Conceptually:

```text
Was a legitimate target selected?
        |
        v
TARGET VALIDITY

Did the transformation execute?
        |
        v
EXECUTION STATUS

What happened to the declared identity relation?
        |
        v
EVALUATION / ADJUDICATION
```

These are separate questions.

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

A classification indicating that no target anchor can legitimately be selected
from an artifact under the frozen anchoring and target-validity rules.

`UNANCHORABLE` does not mean that the source artifact is defective.

It does not mean that the transformation implementation failed.

It does not establish failure of the identity-preservation hypothesis.

It means that the experiment cannot legitimately instantiate the required
target on that artifact under the predeclared rules.

This distinction is important because the absence of a valid experimental
target is different from an implementation failure.

Conceptually:

```text
Artifact available
        |
        v
Apply frozen anchoring rules
        |
        +----------------------+
        |                      |
        v                      v
Valid target found      No legitimate target
        |                      |
        v                      v
Continue experiment        UNANCHORABLE
```

`UNANCHORABLE` therefore represents a limitation on experimental
applicability for that artifact, not an adverse preservation verdict.

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

An artifact can therefore be described as held out because of how it was
treated before execution and as generalization evidence because of the role it
plays in the study.

### Semantic Target vs. Target Anchor

The semantic target is the required kind of experimental information or
structure.

The target anchor is the particular instance selected from a particular
artifact.

```text
Semantic target
    =
WHAT

Target anchor
    =
WHICH ONE
```

### Target Anchor vs. Content-Hash Anchor

A target anchor is the specific experimental instance selected for the
declared identity-preservation test.

A content-hash anchor is independent information used by the protocol to
support component correspondence.

The two uses of `anchor` serve different purposes and should remain explicitly
distinguished.

### Anchoring vs. Target Validity

Anchoring is the process of locating and selecting a proposed target anchor.

Target validity asks whether that selected anchor actually satisfies the
requirements for a legitimate experimental target.

```text
Anchoring
    |
    | selects proposed target
    v
Target-validity determination
    |
    +-- valid ------> continue
    |
    +-- no legitimate target --> UNANCHORABLE
```

### Target Validity vs. Execution Success

Target validity concerns whether the experiment has a legitimate subject.

Execution success concerns whether the declared transformation operation
successfully ran.

A target-validity problem must not be classified as a converter execution
failure.

### Unsupported Route vs. Failed Transformation

An unsupported route is identified before execution from the declared
capabilities of the frozen transformation implementation.

A failed transformation is an attempted executable route that does not
complete according to the execution-success criteria.

```text
unsupported_pre_execution
    =
route not attempted because declared capability does not support it

execution failure
    =
declared executable route was attempted but did not complete successfully
```

The distinction prevents known tool capability boundaries from being
misrepresented as experimental failures.

### Observation vs. Evaluation vs. Adjudication vs. Verdict

These terms describe successive conceptual stages.

```text
OBSERVATION
What happened?

        |
        v

EVALUATION
How does what happened relate to the declared criterion or commitment?

        |
        v

ADJUDICATION
Which predeclared decision rule applies?

        |
        v

VERDICT
What formal classification follows?
```

Keeping these stages separate prevents raw observations from being treated as

---

[◄ Back to Home](index.md)
