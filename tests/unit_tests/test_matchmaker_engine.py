import pytest
from unittest.mock import patch, MagicMock
from src.matchmaker_engine.matching_engine import MatchingEngine
from src.education_matchmaker.education_matching import EducationMatching
from src.experience_matchmaker.experience_matching import ExperienceMatching
from src.skill_matchmaker.technical_skill_matching import TechnicalSkillMatching
from src.skill_matchmaker.soft_skill_matching import SoftSkillMatching
from src.tools_matchmaker.tools_matching import ToolMatching
from src.certification_matchmaker.certification_matching import CertificationMatching
from src.designation_matchmaker.designation_matching import DesignationMatching
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def matching_engine():
    engine = MatchingEngine()

    # Mock all matchers with dummy return value
    matchers = [
        "education_matcher", "experience_matcher", "technical_skill_matcher",
        "soft_skill_matcher", "tool_matcher", "certification_matcher", "designation_matcher"
    ]
    for m in matchers:
        matcher = MagicMock()
        matcher.makeMatch.return_value = 0.9
        matcher.setInputs.return_value = None
        setattr(engine, m, matcher)

    return engine

def test_initialization_success(matching_engine):
    assert matching_engine.education_matcher is not None
    assert matching_engine.experience_matcher is not None
    assert matching_engine.technical_skill_matcher is not None
    assert matching_engine.soft_skill_matcher is not None
    assert matching_engine.tool_matcher is not None
    assert matching_engine.certification_matcher is not None
    assert matching_engine.designation_matcher is not NotImplementedError
    assert matching_engine.resume_json is None
    assert matching_engine.jd_json is None
    assert isinstance(matching_engine.matchReport, dict)
    assert list(matching_engine.matchReport.keys()) == [
        "EDUCATION", "EXPERIENCE", "TECHNICAL_SKILL",
        "SOFT_SKILL", "TOOL", "CERTIFICATION", "DESIGNATION"
    ]
    assert list(matching_engine.matcher_map.keys()) == [
        "EDUCATION", "EXPERIENCE", "TECHNICAL_SKILL",
        "SOFT_SKILL", "TOOL", "CERTIFICATION", "DESIGNATION"
    ]
    assert all(value == 0.0 for value in matching_engine.matchReport.values())

def test_getMatch_success(matching_engine):
    matching_engine.resume_json = {
        "EDUCATION": "BSc CS", "EXPERIENCE": "3 yrs", "TECHNICAL_SKILL": "Python",
        "SOFT_SKILL": "Leadership", "TOOL": "Git", "CERTIFICATION": "AWS",
        "DESIGNATION": "Engineer"
    }
    matching_engine.jd_json = {
        "EDUCATION": "BSc CS", "EXPERIENCE": "2 yrs", "TECHNICAL_SKILL": "Python",
        "SOFT_SKILL": "Leadership", "TOOL": "Git", "CERTIFICATION": "AWS",
        "DESIGNATION": "Engineer"
    }

    result = matching_engine.getMatch()
    assert all(0.0 <= score <= 1.0 for score in result.values())

def test_getMatch_no_json(matching_engine):
    matching_engine.resume_json = None
    matching_engine.jd_json = None
    result = matching_engine.getMatch()
    assert all(score == 0.0 for score in result.values())






