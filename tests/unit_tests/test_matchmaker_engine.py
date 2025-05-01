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
from src.resume_extractor_agent.resume_agent import ResumeAgent
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
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
    
    agents = ["resume_agent", "jd_agent"]
    for a in agents:
        agent = MagicMock()
        agent.extract.return_value = {"key": "value"}
        setattr(engine, a, agent)

    return engine

def test_initialization_success(matching_engine):
    assert matching_engine.education_matcher is not None
    assert matching_engine.experience_matcher is not None
    assert matching_engine.technical_skill_matcher is not None
    assert matching_engine.soft_skill_matcher is not None
    assert matching_engine.tool_matcher is not None
    assert matching_engine.certification_matcher is not None
    assert matching_engine.designation_matcher is not None
    assert matching_engine.resume_agent is not None
    assert matching_engine.jd_agent is not None
    assert matching_engine.resumeText is None
    assert matching_engine.jdText is None
    assert matching_engine.resume_json is None
    assert matching_engine.jd_json is None
    assert isinstance(matching_engine.matchReport, dict)
    assert list(matching_engine.matchReport.keys()) == [
        "EDUCATION", "EXPERIENCE", "TECHNICAL_SKILL",
        "SOFT_SKILL", "TOOL", "CERTIFICATION", "DESIGNATION"
    ]
    assert all(value == 0.0 for value in matching_engine.matchReport.values())

def test_setInputs_success(matching_engine):
    resumeText = "Sample resume text"
    jdText = "Sample job description text"
    matching_engine.setInputs(resumeText, jdText)
    assert matching_engine.resumeText == resumeText
    assert matching_engine.jdText == jdText

def test_setInputs_empty_resume(matching_engine):
    resumeText = ""
    jdText = "Sample job description text"
    with pytest.raises(ValueError, match="Resume text and Job Description text cannot be empty."):
        matching_engine.setInputs(resumeText, jdText)

def test_setInputs_empty_jd(matching_engine):
    resumeText = "Sample resume text"
    jdText = ""
    with pytest.raises(ValueError, match="Resume text and Job Description text cannot be empty."):
        matching_engine.setInputs(resumeText, jdText)

def test_setInputs_empty_both(matching_engine):
    resumeText = ""
    jdText = ""
    with pytest.raises(ValueError, match="Resume text and Job Description text cannot be empty."):
        matching_engine.setInputs(resumeText, jdText)

def test_setInputs_none_resume(matching_engine):
    resumeText = None
    jdText = "Sample job description text"
    with pytest.raises(ValueError, match="Resume text and Job Description text cannot be empty."):
        matching_engine.setInputs(resumeText, jdText)

def test_setInputs_none_jd(matching_engine):
    resumeText = "Sample resume text"
    jdText = None
    with pytest.raises(ValueError, match="Resume text and Job Description text cannot be empty."):
        matching_engine.setInputs(resumeText, jdText)

def test_setInputs_none_both(matching_engine):
    resumeText = None
    jdText = None
    with pytest.raises(ValueError, match="Resume text and Job Description text cannot be empty."):
        matching_engine.setInputs(resumeText, jdText)

def test_setInputs_invalid_type_resume(matching_engine):
    resumeText = 12345
    jdText = "Sample job description text"
    with pytest.raises(TypeError, match="Resume text and Job Description text must be strings."):
        matching_engine.setInputs(resumeText, jdText)

def test_setInputs_invalid_type_jd(matching_engine):
    resumeText = "Sample resume text"
    jdText = 12345
    with pytest.raises(TypeError, match="Resume text and Job Description text must be strings."):
        matching_engine.setInputs(resumeText, jdText)

def test_setInputs_invalid_type_both(matching_engine):
    resumeText = 12345
    jdText = 67890
    with pytest.raises(TypeError, match="Resume text and Job Description text must be strings."):
        matching_engine.setInputs(resumeText, jdText)

def test_getResumeJson_success(matching_engine):
    resumeText = "Sample resume text"
    matching_engine.setInputs(resumeText, "Sample job description text")
    matching_engine.getResumeJson = MagicMock(return_value={"key": "value"})
    matching_engine.resume_json = {"key": "value"}
    result = matching_engine.getResumeJson()
    assert result == {"key": "value"}

def test_getResumeJson_no_resume(matching_engine):
    matching_engine.resumeText = None
    with pytest.raises(ValueError, match="Inputs not set. Please set resume and job description text before getting JSON."):
        matching_engine.getResumeJson()

def test_getJDJson_success(matching_engine):
    jdText = "Sample job description text"
    matching_engine.setInputs("Sample resume text", jdText)
    matching_engine.getJDJson = MagicMock(return_value={"key": "value"})
    matching_engine.jd_json = {"key": "value"}
    result = matching_engine.getJDJson()
    assert result == {"key": "value"}

def test_getJDJson_no_jd(matching_engine):
    matching_engine.jdText = None
    with pytest.raises(ValueError, match="Inputs not set. Please set resume and job description text before getting JSON."):
        matching_engine.getJDJson()

def test_getMatch_success(matching_engine):
    matching_engine.resumeText = "Sample resume text"
    matching_engine.jdText = "Sample job description text"
    matching_engine.resume_json = {
        "EDUCATION": ["BSc CS"], "EXPERIENCE": ["3 yrs"], "TECHNICAL_SKILL": ["Python"],
        "SOFT_SKILL": ["Leadership"], "TOOL": ["Git"], "CERTIFICATION": ["AWS"],
        "DESIGNATION": ["Engineer"]
    }
    matching_engine.jd_json = {
        "EDUCATION": ["BSc CS"], "EXPERIENCE": ["2 yrs"], "TECHNICAL_SKILL": ["Python"],
        "SOFT_SKILL": ["Leadership"], "TOOL": ["Git"], "CERTIFICATION": ["AWS"],
        "DESIGNATION": ["Engineer"]
    }

    result = matching_engine.getMatch()
    assert all(0.0 <= score <= 1.0 for score in result.values())
    assert all(score == 0.9 for score in result.values())

def test_getMatch_no_inputs(matching_engine):
    matching_engine.resumeText = None
    matching_engine.jdText = None
    with pytest.raises(ValueError, match="Inputs not set. Please set resume and job description text before getting match."):
        matching_engine.getMatch()

def test_getMatch_no_json(matching_engine):
    matching_engine.resumeText = "Sample resume text"
    matching_engine.jdText = "Sample job description text"
    matching_engine.resume_json = None
    matching_engine.jd_json = None
    result = matching_engine.getMatch()
    assert all(0.0 <= score <= 1.0 for score in result.values())
    assert all(score == 0.9 for score in result.values())






