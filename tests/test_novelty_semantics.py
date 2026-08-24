"""Contract tests for evidence-calibrated novelty adjudication."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "skills"

NOVELTY_VARIANTS = (
    SKILLS / "novelty-check" / "SKILL.md",
    SKILLS / "skills-codex" / "novelty-check" / "SKILL.md",
    SKILLS / "skills-codex-claude-review" / "novelty-check" / "SKILL.md",
    SKILLS / "skills-codex-gemini-review" / "novelty-check" / "SKILL.md",
)

IDEA_CREATORS = (
    SKILLS / "idea-creator" / "SKILL.md",
    SKILLS / "skills-codex" / "idea-creator" / "SKILL.md",
    SKILLS / "skills-codex-gemini-review" / "idea-creator" / "SKILL.md",
)

IDEA_DISCOVERY_VARIANTS = (
    SKILLS / "idea-discovery" / "SKILL.md",
    SKILLS / "skills-codex" / "idea-discovery" / "SKILL.md",
    SKILLS / "skills-codex-gemini-review" / "idea-discovery" / "SKILL.md",
)

ROBOT_VARIANTS = (
    SKILLS / "idea-discovery-robot" / "SKILL.md",
    SKILLS / "skills-codex" / "idea-discovery-robot" / "SKILL.md",
    SKILLS / "skills-codex-gemini-review" / "idea-discovery-robot" / "SKILL.md",
)

PIPELINE_VARIANTS = (
    SKILLS / "research-pipeline" / "SKILL.md",
    SKILLS / "skills-codex" / "research-pipeline" / "SKILL.md",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_novelty_variants_use_one_primary_subsumption_claim() -> None:
    required = (
        "exactly ONE primary contribution claim",
        "one-sentence primary contribution",
        "CONCEPTUAL",
        "IMPLEMENTATION",
        "DIRECT COLLISION",
        "PARTIAL OVERLAP",
        "ENABLING PRIOR",
        "ANALOGOUS WORK",
        "substantially subsumes",
        "prior-art composition fallacy",
        "ordered passes",
        "reviewer response",
        "Prosecutor",
        "Defender",
        "Judge",
        "KEEP / REFRAME / KILL",
        "do not mutate it into a more complicated idea",
        "[UNVERIFIED]",
        "can never support `KILL`",
        "no substantial subsumption found under the recorded search",
    )
    forbidden = (
        "Identify 3-5 core technical claims",
        "HIGH/MEDIUM/LOW",
        "PROCEED WITH CAUTION",
        "ABANDON",
        "Score: X/10",
        "maximize novelty perception",
    )

    for path in NOVELTY_VARIANTS:
        text = read(path)
        for needle in required:
            assert needle in text, f"{path.relative_to(REPO_ROOT)}: missing {needle!r}"
        for needle in forbidden:
            assert needle not in text, f"{path.relative_to(REPO_ROOT)}: stale novelty contract {needle!r}"


def test_mainline_novelty_skill_can_execute_its_documented_artifacts() -> None:
    text = read(NOVELTY_VARIANTS[0])
    frontmatter = text.split("---", 2)[1]

    assert "Write" in frontmatter
    assert "Bash" in frontmatter
    assert "NOVELTY_DOSSIER.md" in text
    assert "verify_papers.py" in text
    assert "save_trace.sh" in text


def test_idea_creator_routes_keep_reframe_kill_without_novelty_scores() -> None:
    for path in IDEA_CREATORS:
        text = read(path)
        for needle in (
            "`KEEP` — advance the idea unchanged",
            "`REFRAME` — advance the same method",
            "`KILL` — eliminate",
            "subsumes the primary contribution",
            "Novelty decision",
        ):
            assert needle in text, f"{path.relative_to(REPO_ROOT)}: missing {needle!r}"
        assert "**Novelty**: X/10" not in text
        assert "Already done by [paper]" not in text


def test_idea_discovery_treats_keep_and_reframe_as_positive() -> None:
    for path in IDEA_DISCOVERY_VARIANTS:
        text = read(path)
        for needle in (
            "`KEEP` is a positive novelty verdict",
            "`REFRAME` is a positive novelty verdict",
            "`KILL` is negative",
            "If every selected idea receives `KILL`",
            "KEEP/REFRAME decision + checked primary claim",
            "Novelty decision: KEEP / REFRAME",
        ):
            assert needle in text, f"{path.relative_to(REPO_ROOT)}: missing {needle!r}"
        assert "Novelty: CONFIRMED" not in text
        assert "turns out to be already published" not in text


def test_robotics_uses_context_without_component_novelty_gates() -> None:
    for path in ROBOT_VARIANTS:
        text = read(path)
        for needle in (
            "search context for one primary contribution",
            "`KEEP` — advance the idea unchanged",
            "`REFRAME` — advance the same method",
            "`KILL` — eliminate for novelty only",
            "do not add a new module to manufacture novelty",
            "Novelty decision: KEEP / REFRAME",
        ):
            assert needle in text, f"{path.relative_to(REPO_ROOT)}: missing {needle!r}"
        assert "novelty weak" not in text


def test_research_pipeline_preserves_actual_novelty_disposition() -> None:
    for path in PIPELINE_VARIANTS:
        text = read(path)
        assert "Novelty decision: KEEP" in text
        assert "Novelty decision: REFRAME" in text
        assert "Novelty: CONFIRMED" not in text
