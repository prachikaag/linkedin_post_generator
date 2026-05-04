"""
Loads personal AI experiments from config/experiments.yaml and matches
them to article clusters so the post generator can weave firsthand
observations into posts.
"""

from pathlib import Path

import yaml


class ExperimentLoader:
    def __init__(self, config_dir: Path):
        self._experiments = self._load(config_dir / "experiments.yaml")

    # ── Public API ─────────────────────────────────────────────────────────────

    def find_relevant(
        self,
        matched_keywords: list[str],
        matched_companies: list[str],
        max_results: int = 2,
    ) -> list[dict]:
        """
        Return up to max_results unpublished experiments most relevant
        to the given article cluster (matched by keyword overlap).
        Returns an empty list if no experiments.yaml is configured.
        """
        if not self._experiments:
            return []

        search_terms = {t.lower() for t in matched_keywords + matched_companies}
        scored: list[tuple[int, dict]] = []

        for exp in self._experiments:
            if exp.get("published", False):
                continue

            exp_terms: set[str] = set()
            for kw in exp.get("keywords", []):
                exp_terms.add(kw.lower())
            if exp.get("tool"):
                exp_terms.add(exp["tool"].lower())
            if exp.get("use_case"):
                exp_terms.update(exp["use_case"].lower().split())

            overlap = len(search_terms & exp_terms)
            if overlap > 0:
                scored.append((overlap, exp))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored[:max_results]]

    def format_for_prompt(self, experiments: list[dict]) -> str:
        """
        Format a list of experiments as a prompt block for post_generator.
        Returns an empty string if the list is empty.
        """
        if not experiments:
            return ""

        lines = [
            "## Personal Experiments & Observations",
            "The following are firsthand AI experiments the author has run.",
            "If one is directly relevant to the news story, weave ONE insight",
            "naturally into the post as a brief first-person observation —",
            "paraphrase in the author's voice, do NOT quote verbatim, and only",
            "include it where it adds genuine value. Skip if there is no natural fit.",
            "",
        ]

        for i, exp in enumerate(experiments, 1):
            lines.append(f"### Experiment {i}")
            if exp.get("tool"):
                lines.append(f"Tool: {exp['tool']}")
            if exp.get("date"):
                lines.append(f"Tested: {exp['date']}")
            if exp.get("use_case"):
                lines.append(f"Use case: {exp['use_case']}")
            if exp.get("what_I_did"):
                lines.append(f"What I did: {exp['what_I_did'].strip()}")
            if exp.get("key_finding"):
                lines.append(f"Key finding: {exp['key_finding'].strip()}")
            if exp.get("surprise"):
                lines.append(f"Surprising: {exp['surprise'].strip()}")
            if exp.get("brand_relevance"):
                lines.append(f"Brand relevance: {exp['brand_relevance'].strip()}")
            lines.append("")

        return "\n".join(lines)

    # ── Internal ───────────────────────────────────────────────────────────────

    def _load(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            experiments = data.get("experiments", [])
            if not isinstance(experiments, list):
                return []
            return experiments
        except Exception as exc:
            print(f"  [warn] Could not load experiments.yaml: {exc}")
            return []
