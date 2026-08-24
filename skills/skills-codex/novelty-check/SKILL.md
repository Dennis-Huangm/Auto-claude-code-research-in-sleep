---
name: "novelty-check"
description: "Verify research idea novelty against recent literature. Use when user says \"查新\", \"novelty check\", \"有没有人做过\", \"check novelty\", or wants to verify a research idea is novel before implementing."
---

# Novelty Check Skill

Check whether a proposed method/idea has already been done in the literature: **$ARGUMENTS**

The goal is not to find any reason to reject the idea. The goal is to determine
whether a concrete prior work **substantially subsumes its simple central
contribution**.

## Constants

- REVIEWER_MODEL = `gpt-5.6-sol` — Model used via a secondary Codex agent. Must be an OpenAI model (e.g., `gpt-5.6-sol`, `o3`, `gpt-4o`)
- **REVIEWER_BACKEND = `codex`** — Default: Codex xhigh reviewer. Use `--reviewer: oracle-pro` only when explicitly requested; if Oracle is unavailable, warn and fall back to Codex xhigh.

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

Search the primary contribution as a whole. Use at least these query families:

1. The one-sentence contribution in near-natural language.
2. The central mechanism or insight plus the target problem.
3. The claimed technical effect plus the setting or application.
4. Synonyms for the central insight and its closest method family.

Search arXiv, Google Scholar, Semantic Scholar, recent top-venue papers, and the
most recent six months of preprints. Read the abstract and, when needed, the
method or related-work sections of potentially overlapping papers.

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

### Phase C: Fresh-Agent Verification (same-family provisional by default)

Call REVIEWER_MODEL via a fresh `spawn_agent` with xhigh reasoning. When the
method and paper list are substantial, write a dossier such as
`NOVELTY_DOSSIER.md` and instruct the reviewer to read it rather than duplicating
large content inline.

```
spawn_agent:
  model: gpt-5.6-sol
  reasoning_effort: xhigh
  message: |
    Read the novelty dossier at <absolute path to NOVELTY_DOSSIER.md> and
    follow all instructions in it.
```

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
setting, or mechanism that was not already part of the checked idea.

This base Codex review is same-family evidence. Record
`review_independence: same-family` and `acceptance_status: provisional`; do not
describe it as cross-family acceptance.

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
- “Applying X to Y” is not automatically novel, but neither is it automatically
  non-novel. Judge the primary contribution.
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

After each `spawn_agent` or optional `oracle-pro` reviewer call, save the trace
following `../shared-references/review-tracing.md`. Write files to
`.aris/traces/novelty-check/<date>_run<NN>/` and record the primary claim,
candidate-paper relationships, reviewer route, raw Prosecutor/Defender/Judge
response, final disposition, and same-family provisional status. Respect the
`--- trace:` parameter when present (default: `full`).
