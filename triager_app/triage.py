"""Rule-based issue triage for the Copilot plugin."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TriageResult:
    """Structured triage output for an issue."""

    labels: list[str]
    priority: str
    issue_type: str
    summary: str
    rationale: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "labels": self.labels,
            "priority": self.priority,
            "type": self.issue_type,
            "summary": self.summary,
            "rationale": self.rationale,
        }


def triage_issue(title: str, body: str = "") -> dict[str, object]:
    """Return label, priority, and summary suggestions for a GitHub issue."""

    title = title.strip()
    body = body.strip()
    text = f"{title}\n{body}".lower()

    labels: list[str] = []
    rationale: list[str] = []

    def add_label(label: str, reason: str) -> None:
        if label not in labels:
            labels.append(label)
            rationale.append(reason)

    if _contains_any(text, "crash", "exception", "traceback", "error", "fails", "broken", "bug"):
        add_label("bug", "The issue describes failing or broken behavior.")

    if _contains_any(text, "feature", "enhancement", "request", "add support", "would like"):
        add_label("enhancement", "The issue asks for new or improved functionality.")

    if _contains_any(text, "docs", "documentation", "readme", "typo", "example"):
        add_label("documentation", "The issue is related to documentation or examples.")

    if _contains_any(text, "question", "how do i", "how to", "can i", "is it possible"):
        add_label("question", "The issue is phrased as a question or support request.")

    if _contains_any(text, "security", "vulnerability", "xss", "csrf", "injection", "secret", "token leak"):
        add_label("security", "The issue mentions a possible security concern.")

    if _contains_any(text, "install", "setup", "configure", "configuration", "dependency"):
        add_label("setup", "The issue appears related to setup or configuration.")

    if not labels:
        add_label("needs-triage", "No specific category was detected from the issue text.")

    priority = _priority_for(text, labels)
    issue_type = _issue_type_for(labels)
    summary = _summarize(title, body)

    return TriageResult(
        labels=labels,
        priority=priority,
        issue_type=issue_type,
        summary=summary,
        rationale=rationale,
    ).to_dict()


def _contains_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def _priority_for(text: str, labels: list[str]) -> str:
    if "security" in labels or _contains_any(text, "data loss", "production down", "outage", "critical"):
        return "high"
    if "bug" in labels or _contains_any(text, "blocked", "regression", "urgent"):
        return "medium"
    return "low"


def _issue_type_for(labels: list[str]) -> str:
    if "security" in labels:
        return "security"
    if "bug" in labels:
        return "bug"
    if "enhancement" in labels:
        return "feature"
    if "question" in labels:
        return "support"
    if "documentation" in labels:
        return "docs"
    return "task"


def _summarize(title: str, body: str) -> str:
    if title:
        return title[:120]

    first_line = next((line.strip() for line in body.splitlines() if line.strip()), "")
    return first_line[:120] if first_line else "No issue summary provided."
