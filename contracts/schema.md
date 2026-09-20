# Typed Commitment Schema

Written from specifications and authoritative mapping sources.

This pilot was motivated in part by previously known preservation failures,
including the general failure shape reported in cyclonedx-cli #424.

Accordingly, the initial schema and commitment are not
a blind first test of that historical case.

Known examples available during design are engineering validation cases,
not held-out evidence of generalization.

The first generalization claim begins only after the commitment, evaluator,
and adjudication protocol have been frozen and the generalization corpus has
been defined and separately frozen.

Generalization evidence is limited to cases or corpus outputs not examined
before the applicable generalization freeze.

The initial commitment/evaluator freeze is recorded in
`contracts/FREEZE_01_COMMITMENT_EVALUATOR.md`
with a timestamp, Git commit, and content hashes.

## Commitment Kinds

A commitment has a `kind`.
The initial pilot defines exactly one implemented kind and
refuses to force other semantic relations into it.

- `representation_preservation`
  An identifier borne by a component in a SOURCE representation must survive,
  under a stated notion of sameness, to the canonical slot of that identifier
  in a TARGET representation produced by a transformation.
  Direction matters: source -> target. Each direction is a separate instance.

The Grype matching case is a DIFFERENT kind (`matching_conformance`,
directional applicability of a match relation).
It is NOT modeled here.
It may be added as kind 2, after we close this initial loop.

## Commitment Fields

For the `representation_preservation` commitment kind,
the commitment fields include:

- id stable name
- kind must be "representation_preservation"
- identifier the thing preserved (e.g. "purl")
- same_when interpretation rule for "the identifier is the same"
  (pinned to a source spec)
- canonical_slot per-format location that COUNTS as preserving
  (pinned to each format spec)
- noncanonical_slots per-format locations where the identifier may hide but
  does NOT count as preserved (relocation = a violation)
- representable_in formats whose spec can hold this identifier. If a target
  format is NOT here, loss is EXPECTED (refused), never a
  violation.
- anchor how a component is matched across the transformation
- cardinality the source-identifier cardinality accepted by this commitment.
  The initial commitment evaluates exactly one canonical source PURL per
  component. A component bearing multiple canonical source PURLs is
  `UNDERDETERMINED` under this commitment and is not classified by inspecting
  which PURLs happen to appear in the target.
- provenance source records (`sources.toml`) grounding normative commitment
  claims; protocol-defined evaluation rules are identified separately where
  the authoritative specifications do not prescribe cross-format behavior

## Verdict Vocabulary

The verdict vocabulary (per anchored component, per identifier)

- `PRESERVED` source identifier appears, same_when, in target canonical slot
- `VIOLATED_DROPPED` source identifier is absent from the anchored target component
- `VIOLATED_RELOCATED` source identifier appears in a declared target
  noncanonical slot but not in the canonical slot
- `VIOLATED_ALTERED` the anchored target component contains a canonical
  identifier with the same reduced coordinates but not the same canonical
  identifier
- `UNSUPPORTED` target format cannot represent it -> expected loss, refused
- `UNDERDETERMINED` the source component bears multiple canonical PURLs and
  the initial commitment does not define a source-grounded rule for selecting
  one of them for preservation evaluation
- `UNANCHORABLE` required source-to-target component correspondence
  could not be established under the anchoring rule
- `NOT_APPLICABLE` source bore no such identifier; nothing to preserve

Only `VIOLATED_*` outcomes count as identity-preservation violations.

`UNSUPPORTED`, `UNDERDETERMINED`, and `NOT_APPLICABLE` are refusal,
insufficient-determination, or non-applicability outcomes.

`UNANCHORABLE` is reported separately and never silently dropped. It indicates
that the preservation commitment could not be evaluated reliably for that
component under the declared anchoring rule.
An `UNANCHORABLE` outcome is not, by itself, an identity-preservation
violation. Loss or alteration of the anchor may be studied under a separate
preservation commitment.

The initial commitment deliberately does not infer a selection rule from the
observed target.
A target containing one, some, or all source PURLs does not resolve
an `UNDERDETERMINED` source case after the fact.
Multi-PURL preservation semantics require a
separately defined commitment revision before they are evaluated.
