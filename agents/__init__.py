"""Agentes del sistema de captación B2B v2."""

from agents.base import BaseAgent
from agents.phase1_collection import ScraperAgent, EnricherAgent, ValidatorAgent
from agents.pain_point_detector import PainPointDetectorAgent
from agents.phase2_clustering import ClassifierAgent, ScorerAgent, SegmenterAgent
from agents.pre_diagnostic import PreDiagnosticAgent
from agents.role_personalizer import RolePersonalizerAgent
from agents.phase3_outreach import CopywriterAgent, SenderAgent, FollowUpAgent
from agents.humanizer import HumanizerAgent
from agents.learning_engine import LearningEngineAgent
from agents.orchestrator import Orchestrator

__all__ = [
    "BaseAgent",
    "ScraperAgent",
    "EnricherAgent",
    "ValidatorAgent",
    "PainPointDetectorAgent",
    "ClassifierAgent",
    "ScorerAgent",
    "SegmenterAgent",
    "PreDiagnosticAgent",
    "RolePersonalizerAgent",
    "CopywriterAgent",
    "HumanizerAgent",
    "SenderAgent",
    "FollowUpAgent",
    "LearningEngineAgent",
    "Orchestrator",
]
