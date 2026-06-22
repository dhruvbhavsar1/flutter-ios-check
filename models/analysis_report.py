"""Complete analysis result used by console reporters."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from models.finding import Finding
from models.plugin_info import PluginInfo, PluginStatus
from models.project_info import ProjectInfo


class ReadinessStatus(StrEnum):
    """Overall readiness labels derived from the score."""

    READY = "READY"
    NEEDS_ATTENTION = "NEEDS ATTENTION"
    NOT_READY = "NOT READY"


@dataclass(frozen=True, slots=True)
class AnalysisReport:
    """Project information, findings, plugin classifications, and score."""

    project: ProjectInfo
    findings: list[Finding] = field(default_factory=list)
    plugins: list[PluginInfo] = field(default_factory=list)
    score: int = 0
    status: ReadinessStatus = ReadinessStatus.NOT_READY

    def plugin_count(self, status: PluginStatus) -> int:
        """Count plugins with a given compatibility status."""
        return sum(plugin.status is status for plugin in self.plugins)
