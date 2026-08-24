---
name: novelty-check
description: Verify research idea novelty against recent literature. Use when user says "查新", "novelty check", "有没有人做过", "check novelty", or wants to verify a research idea is novel before implementing.
argument-hint: "[method-or-idea-description]"
allowed-tools: WebSearch, WebFetch, Grep, Read, Glob, Write, Bash, mcp__codex__codex
---

# Novelty Check Skill

Check whether a proposed method/idea has already been done in the literature: **$ARGUMENTS**

The goal is not to find any reason to reject the idea. The goal is to determine
whether a concrete prior work **substantially subsumes its simple central
contribution**.

## Constants

- REVIEWER_MODEL = `gpt-5.6-sol` — Model used via Codex MCP. Must be an OpenAI model (e.g., `gpt-5.6-sol`, `o3`, `gpt-4o`)

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
5. List the remaining modules, backbones, datasets, objectives, benchmarks, and
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

Component-level queries are useful for finding candidate papers, but a hit on a
component is not a separate novelty failure. For every candidate paper, assign
exactly one relationship:

- `DIRECT COLLISION` — the paper teaches substantially the same primary
  contribution in materially the same technical role.
- `PARTIAL OVERLAP` — it shares a material element but does not subsume the
  central mechanism-effect claim.
- `ENABLING PRIOR` — it supplies a reusable component, backbone, dataset,
  objective, benchmark, or tool.
- `ANALOGOUS WORK` — it uses a similar idea in another problem or setting but
  does not implement the primary contribution.

A paper substantially subsumes the primary contribution only when verified
evidence covers its essential conceptual core or claimed non-routine
implementation and leaves only routine engineering, parameter, benchmark, or
presentation differences.

Do not commit the **prior-art composition fallacy**: separate papers A, B, and C
showing separate ingredients do not establish that any paper has already made
the proposed central contribution. If the combination appears obvious, record
that as an **obviousness / incrementality risk**, not as evidence that the idea
is already done.

### Phase C: Symmetric Cross-Model Verification

Call REVIEWER_MODEL via Codex MCP (`mcp__codex__codex`) with xhigh reasoning.
When the method description plus the Phase-B paper list is more than a short
note, avoid pasting it inline into the MCP prompt. Write `NOVELTY_DOSSIER.md` (or
a project-local equivalent), then send only its absolute path:

```
mcp__codex__codex:
  model: gpt-5.6-sol
  config: {"model_reasoning_effort": "xhigh"}
  prompt: |
    Read the novelty dossier at <absolute path to NOVELTY_DOSSIER.md> and
    follow all instructions in it.
```

The dossier must contain:

- the full proposed method;
- the one-sentence primary contribution and novelty locus;
- supporting elements explicitly marked as non-claims;
- the verified candidate-paper set and relationship evidence;
- the four prior-work relationship definitions;
- the `KEEP / REFRAME / KILL` decision rules below;
- these three ordered passes in a **single reviewer response**:
  1. **Prosecutor** — construct the strongest evidence-grounded case that a
     concrete paper substantially subsumes the primary contribution.
  2. **Defender** — test whether that case is only terminology, component,
     benchmark, enabling-prior, analogous, or multi-paper overlap; give the
     strongest honest defense of the idea as supplied.
  3. **Judge** — after considering both arguments, classify the papers and issue
     the decision.

The Defender may clarify or narrow an existing contribution, but must not add a
module, loss, objective, training stage, constraint, dataset, benchmark, task
setting, or mechanism that was not already part of the checked idea.

### Phase D: Decision

Use exactly one disposition:

- `KEEP` — no verified paper substantially subsumes the primary contribution.
  Partial overlap, enabling prior, and analogous work are compatible with KEEP.
- `REFRAME` — the method can remain unchanged, but the contribution wording is
  too broad. Return one honest 1–2 sentence replacement claim using only ideas
  already present in the proposal.
- `KILL` — allowed only when one concrete, verified paper is a `DIRECT
  COLLISION`, substantially subsumes the primary contribution, and no honest
  narrower contribution already present in the idea remains.

`KILL` requires claim-to-paper evidence. “The ingredients are known,” “many
related papers exist,” “the novelty seems weak,” or a combination of separate
papers is not sufficient.

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

- Evaluate the proposed idea; do not mutate it into a more complicated idea to
  escape prior work.
- Prefer a simple meaningful delta stated in 1–2 sentences over a narrower,
  mechanism-heavy gap.
- If differentiation requires a new architecture, module, objective,
  regularizer, stage, dataset, benchmark, or setting, label it as a possible
  **new idea**, not a reframe of the checked idea.
- If the existing difference cannot be stated clearly in 1–2 sentences, report
  `weak or unclear delta`; do not manufacture specificity.
- “Applying X to Y” is not automatically novel, but neither is it automatically
  non-novel: judge whether the primary contribution is a meaningful new insight,
  mechanism-effect relationship, finding, or non-routine implementation.
- If the method is not novel but an already-present finding or evaluation
  contribution is, use `REFRAME` and state that contribution plainly.
- Say “no substantial subsumption found under the recorded search,” not
  “novelty confirmed.”

### Paper Verification

Every paper in the relationship matrix must pass pre-search verification via
`verify_papers.py` (canonical name resolved per
[`shared-references/integration-contract.md`](../shared-references/integration-contract.md)
§2; 3-layer arXiv / CrossRef / Semantic Scholar fallback inside the helper).
Policy D1 applies: if the helper is unresolved or its invocation fails, tag the
entry `[UNVERIFIED]` and surface the uncertainty rather than dropping it. An
`[UNVERIFIED]` paper can never support `KILL`. Never fabricate arXiv IDs, DOIs,
or titles from memory. Full protocol:
[`shared-references/citation-discipline.md`](../shared-references/citation-discipline.md)
§ Pre-Search Verification Protocol.

## Review Tracing

After each `mcp__codex__codex` or `mcp__codex__codex-reply` reviewer call, save
the trace following `shared-references/review-tracing.md` (Policy C — forensic;
never silently skip). Use `save_trace.sh` (resolved per the chain in
`shared-references/integration-contract.md` §2) or write files directly to
`.aris/traces/<skill>/<date>_run<NN>/`. Record the primary claim, candidate-paper
relationships, Prosecutor/Defender/Judge response, and final disposition. Respect
the `--- trace:` parameter (default: `full`).
