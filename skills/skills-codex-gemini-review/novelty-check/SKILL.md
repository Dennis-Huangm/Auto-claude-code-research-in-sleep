---
name: "novelty-check"
description: "Verify research idea novelty against recent literature. Use when user says \"查新\", \"novelty check\", \"有没有人做过\", \"check novelty\", or wants to verify a research idea is novel before implementing."
---

> Override for Codex users who want **Gemini**, not a second Codex agent, to act as the reviewer. Install this package **after** `skills/skills-codex/*`.

# Novelty Check Skill

> **Gemini overlay assurance:** `review_independence: cross-family` and `acceptance_status: accepted`.

Check whether a proposed method/idea has already been done in the literature: **$ARGUMENTS**

The goal is not to find any reason to reject the idea. The goal is to determine
whether a concrete prior work **substantially subsumes its simple central
contribution**.

## Constants

- **REVIEWER_MODEL = `gemini-review`** — Gemini reviewer invoked through the local `gemini-review` MCP bridge. Set `GEMINI_REVIEW_MODEL` if you need a specific Gemini model override.

## Instructions

### Phase A: Compress the Primary Contribution

1. Read the user's complete method description.
2. Identify **exactly ONE primary contribution claim**: the contribution whose
   removal would collapse the paper's thesis.
3. Express it in one sentence containing the central insight or mechanism, the
   problem or setting, and the claimed technical effect.
4. Label its primary novelty locus:
   - `CONCEPTUAL` — the central insight, problem formulation, mechanism-effect
     relationship, finding, or use of a representation is the contribution.
   - `IMPLEMENTATION` — the concrete non-routine realization is itself the
     contribution.
5. List remaining modules, backbones, datasets, objectives, benchmarks, and
   experiments as **supporting elements, not separate novelty claims**. They may
   be standard, borrowed, adapted, or previously known.

If the input appears to contain several contributions, choose the simplest
single claim that best explains why the work matters. Do not require every
technical component to be novel.

### Phase B: Search for Substantial Subsumption

Search the primary contribution as a whole with these query families:

1. The one-sentence contribution in near-natural language.
2. The central mechanism or insight plus the target problem.
3. The claimed technical effect plus the setting or application.
4. Synonyms for the central insight and its closest method family.

Search arXiv, Google Scholar, Semantic Scholar, recent top-venue papers, and the
most recent six months of preprints. Read abstracts and, when needed, method or
related-work sections.

Component-level queries may retrieve candidates, but a component hit is not a
separate novelty failure. Classify every candidate paper as exactly one of:

- `DIRECT COLLISION` — substantially the same primary contribution in materially
  the same technical role.
- `PARTIAL OVERLAP` — a material shared element that does not subsume the central
  mechanism-effect claim.
- `ENABLING PRIOR` — a reusable component, backbone, dataset, objective,
  benchmark, or tool.
- `ANALOGOUS WORK` — a similar idea in another problem or setting that does not
  implement the primary contribution.

A paper substantially subsumes the primary contribution only when verified
evidence covers its essential conceptual core or claimed non-routine
implementation and leaves only routine engineering, parameter, benchmark, or
presentation differences.

Do not commit the **prior-art composition fallacy**: separate papers A, B, and C
showing separate ingredients do not establish that any paper has already made
the proposed central contribution. Record apparent obviousness as an
**obviousness / incrementality risk**, not as `already done`.

### Phase C: Symmetric Cross-Model Verification

Call REVIEWER_MODEL via `mcp__gemini-review__review_start` with high-rigor review.
When the method and paper list are substantial, write a dossier such as
`NOVELTY_DOSSIER.md` and send only its path:

```
mcp__gemini-review__review_start:
  prompt: |
    Read the novelty dossier at <absolute path to NOVELTY_DOSSIER.md> and
    follow all instructions in it.
```

Immediately save the returned `jobId` and poll
`mcp__gemini-review__review_status` with a bounded `waitSeconds` until
`done=true`. Treat the completed payload's `response` as reviewer output and
save the completed `threadId` for follow-up.

The dossier must contain:

- the full proposed method;
- the one-sentence primary contribution and novelty locus;
- supporting elements explicitly marked as non-claims;
- the verified candidate-paper set and relationship evidence;
- the four relationship definitions and `KEEP / REFRAME / KILL` rules;
- three ordered passes in one reviewer response:
  1. **Prosecutor** — construct the strongest evidence-grounded subsumption case.
  2. **Defender** — test whether the case is only terminology, component,
     benchmark, enabling-prior, analogous, or multi-paper overlap; defend the
     supplied idea honestly.
  3. **Judge** — after both arguments, classify the papers and issue the decision.

The Defender may clarify or narrow an existing contribution, but must not add a
module, loss, objective, training stage, constraint, dataset, benchmark, task
setting, or mechanism not already part of the checked idea.

### Phase D: Decision

- `KEEP` — no verified paper substantially subsumes the primary contribution.
  Partial overlap, enabling prior, and analogous work are compatible with KEEP.
- `REFRAME` — the method remains unchanged but the claim is too broad. Return one
  honest 1–2 sentence replacement claim using only ideas already present.
- `KILL` — allowed only when one concrete, verified paper is a `DIRECT
  COLLISION`, substantially subsumes the primary contribution, and no honest
  narrower contribution already present remains.

`KILL` requires claim-to-paper evidence. Known ingredients, many related papers,
a weak-novelty impression, or a combination of separate papers is insufficient.

### Phase E: Novelty Report

```markdown
## Novelty Check Report

### One-Sentence Idea
[Exactly one compressed sentence]

### Primary Contribution
- Claim: [exactly one]
- Novelty locus: CONCEPTUAL / IMPLEMENTATION
- Supporting elements that are not separate novelty claims: [list]

### Prior-Work Relationship Matrix
| Paper | Verified? | Relationship | Evidence of overlap | What remains distinct |
|-------|-----------|--------------|---------------------|-----------------------|

### Adversarial Review
#### Prosecutor
[Strongest concrete subsumption argument]

#### Defender
[Strongest honest defense of the supplied idea; no added mechanisms]

#### Judge
[Resolve the arguments and explain the relationship classification]

### Decision
- Decision: KEEP / REFRAME / KILL
- Subsumption finding: [what one concrete paper does or does not cover]
- Closest concrete paper: [paper or "none found under the recorded search"]
- Rationale: [evidence-calibrated explanation]
- Honest one-sentence reframe: [required only for REFRAME]
- Obviousness / incrementality risk: [separate from already-done evidence]
- Evidence limitations: [coverage gaps and unverified candidates]
```

### Simplicity Preservation Rules

- Evaluate the supplied idea; do not mutate it into a more complicated idea to
  escape prior work.
- Prefer a simple meaningful delta stated in 1–2 sentences over a narrower,
  mechanism-heavy gap.
- If differentiation requires a new architecture, module, objective,
  regularizer, stage, dataset, benchmark, or setting, label it as a possible
  **new idea**, not a reframe.
- If the existing difference cannot be stated clearly in 1–2 sentences, report
  `weak or unclear delta`; do not manufacture specificity.
- If an already-present finding or evaluation contribution survives when the
  method does not, use `REFRAME` and state it plainly.
- Say “no substantial subsumption found under the recorded search,” not
  “novelty confirmed.”

### Paper Verification

Every paper in the relationship matrix must pass pre-search verification via
`verify_papers.py`, resolved per `../shared-references/integration-contract.md`.
If the helper is unavailable or fails, retain the entry as `[UNVERIFIED]` and
surface the uncertainty. An `[UNVERIFIED]` paper can never support `KILL`. Never
fabricate identifiers or titles from memory.

## Review Tracing

After each Gemini reviewer call, save the trace following
`../shared-references/review-tracing.md`. Write files to
`.aris/traces/novelty-check/<date>_run<NN>/` and record the primary claim,
candidate-paper relationships, raw Prosecutor/Defender/Judge response, final
disposition, completed `threadId`, and cross-family accepted status. Respect the
`--- trace:` parameter when present (default: `full`).
