import pytest
from unittest.mock import patch, MagicMock
from src.skill_matchmaker.skill_matching import SkillMatching, SkillSimilarity
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def skill_matchmaker():
    return SkillMatching(maxInputLength=10000)

@pytest.fixture
def skill_similarity():
    return SkillSimilarity()

def test_ss_initialization(skill_similarity):
    assert skill_similarity.model1Score is None
    assert skill_similarity.model2Score is None
    assert skill_similarity.ensembleScore is not None
    assert isinstance(skill_similarity.ensembleScore, list)

def test_ss_set_model1_score(skill_similarity):
    skill_similarity.setModel1Score([0.8])
    assert skill_similarity.model1Score == [0.8]
    with pytest.raises(ValueError, match="Score must be a list."):
        skill_similarity.setModel1Score('1')

def test_ss_set_model2_score(skill_similarity):
    skill_similarity.setModel2Score([0.9])
    assert skill_similarity.model2Score == [0.9]
    with pytest.raises(ValueError, match="Score must be a list."):
        skill_similarity.setModel2Score('1')

def test_ss_average_ensemble(skill_similarity):
    skill_similarity.setModel1Score([0.8])
    skill_similarity.setModel2Score([0.6])
    skill_similarity.averageEnsemble()
    assert isinstance(skill_similarity.ensembleScore, list)
    assert len(skill_similarity.ensembleScore) == 1
    skill_similarity.model1Score = None
    skill_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        skill_similarity.averageEnsemble()

def test_ss_hard_ensemble(skill_similarity):
    skill_similarity.setModel1Score([0.9])
    skill_similarity.setModel2Score([0.5])
    skill_similarity.hardEnsemble()
    assert isinstance(skill_similarity.ensembleScore, list)
    assert len(skill_similarity.ensembleScore) == 1
    skill_similarity.reset()
    skill_similarity.setModel1Score([0.7])
    skill_similarity.setModel2Score([0.8])
    skill_similarity.hardEnsemble()
    assert isinstance(skill_similarity.ensembleScore, list)
    assert len(skill_similarity.ensembleScore) == 1
    skill_similarity.reset()
    skill_similarity.setModel1Score([0.9])
    skill_similarity.setModel2Score([0.9])
    skill_similarity.hardEnsemble()
    assert isinstance(skill_similarity.ensembleScore, list)
    assert len(skill_similarity.ensembleScore) == 1
    skill_similarity.reset()
    skill_similarity.model1Score = None
    skill_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        skill_similarity.hardEnsemble()

def test_ss_get_ensemble_score(skill_similarity):
    skill_similarity.setModel1Score([0.7])
    skill_similarity.setModel2Score([0.8])
    skill_similarity.hardEnsemble()
    assert isinstance(skill_similarity.ensembleScore, list)
    assert len(skill_similarity.ensembleScore) == 1
    skill_similarity.model1Score = None
    skill_similarity.model2Score = None
    skill_similarity.ensembleScore = None
    with pytest.raises(ValueError, match="Ensemble score has not been calculated."):
        skill_similarity.getEnsembleScore()
    skill_similarity.ensembleScore = '1'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        skill_similarity.getEnsembleScore()

def test_ss_reset(skill_similarity):
    skill_similarity.setModel1Score([0.8])
    skill_similarity.setModel2Score([0.9])
    skill_similarity.ensembleScore = [0.85]
    skill_similarity.reset()
    assert skill_similarity.model1Score is None
    assert skill_similarity.model2Score is None
    assert skill_similarity.ensembleScore is not None
    assert isinstance(skill_similarity.ensembleScore, list)

def test_initialization(skill_matchmaker):
    assert skill_matchmaker.maxInputLength == 10000
    assert skill_matchmaker.model1 is not None
    assert skill_matchmaker.model2 is not None
    assert skill_matchmaker.resumeSkill is None
    assert skill_matchmaker.jobSkill is None
    assert skill_matchmaker.similarity is not None
    assert isinstance(skill_matchmaker.similarity, SkillSimilarity)

def test_set_inputs_success(skill_matchmaker):
    resumeSkill = "Python, Java"
    jobSkill = "Python, Machine Learning, Data Science"
    skill_matchmaker.setInputs(resumeSkill, jobSkill)
    assert len(skill_matchmaker.resumeSkill) == 2
    assert len(skill_matchmaker.jobSkill) == 3
    assert isinstance(skill_matchmaker.resumeSkill, list)
    assert isinstance(skill_matchmaker.jobSkill, list)

def test_set_inputs_failure(skill_matchmaker):
    resumeSkill = None
    jobSkill = "Python, Machine Learning, Data Science"
    with pytest.raises(ValueError, match="Resume skill and job skill cannot be empty."):
        skill_matchmaker.setInputs(resumeSkill, jobSkill)
    
    resumeSkill = "Python, Machine Learning, Data Science"
    jobSkill = None
    with pytest.raises(ValueError, match="Resume skill and job skill cannot be empty."):
        skill_matchmaker.setInputs(resumeSkill, jobSkill)

def test_set_inputs_invalid(skill_matchmaker):
    resumeSkill = 12345
    jobSkill = "Python, Machine Learning, Data Science"
    with pytest.raises(ValueError, match="Resume skill must be a string."):
        skill_matchmaker.setInputs(resumeSkill, jobSkill)
    
    resumeSkill = "Python, Machine Learning, Data Science"
    jobSkill = 12345
    with pytest.raises(ValueError, match="Job skill must be a string."):
        skill_matchmaker.setInputs(resumeSkill, jobSkill)

def test_make_match_success(skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    skill_matchmaker.model1 = model1Mock
    skill_matchmaker.model2 = model2Mock
    skill_matchmaker.resumeSkill = ['python', 'java']
    skill_matchmaker.jobSkill = ['python', 'machine learning', 'data science']
    model1Mock.encode.return_value = [np.array([[0.1]]) * 6]
    model2Mock.encode.return_value = [np.array([[0.1]]) * 6]
    with patch('src.skill_matchmaker.skill_matching.cosine_similarity', return_value=np.array([[1.0]])):
            score = skill_matchmaker.makeMatch()
    assert score == 1.0


def test_make_match_no_models(skill_matchmaker):
    skill_matchmaker.model1 = None
    skill_matchmaker.model2 = None
    skill_matchmaker.modelName1 = None
    skill_matchmaker.modelName2 = None
    with pytest.raises(RuntimeError, match="Failed to load models"):
        skill_matchmaker.makeMatch()

def test_make_match_no_model_names(skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    skill_matchmaker.model1 = model1Mock
    skill_matchmaker.model2 = model2Mock
    with pytest.raises(ValueError, match="Inputs are not set"):
        skill_matchmaker.makeMatch()

def test_make_match_failure(skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    skill_matchmaker.model1 = model1Mock
    skill_matchmaker.model2 = model2Mock
    skill_matchmaker.resumeSkill = "Python, Java"
    skill_matchmaker.jobSkill = "Python, Machine Learning, Data Science"
    model1Mock.encode.side_effect = Exception("Encoding failed")
    with pytest.raises(RuntimeError, match="Failed to make match: Encoding failed"):
        skill_matchmaker.makeMatch()

def test_similarity_score_success(skill_matchmaker):
    skill_matchmaker.similarity.model1Score = [0.8, 0.9]
    skill_matchmaker.similarity.model2Score = [0.6, 0.7]
    skill_matchmaker.similarity.ensembleScore = [0.7, 0.8]
    score = skill_matchmaker.getSimilarityScore()
    assert score == 0.75

def test_similarity_score_no_ensemble(skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    skill_matchmaker.model1 = model1Mock
    skill_matchmaker.model2 = model2Mock
    skill_matchmaker.similarity.model1Score = []
    skill_matchmaker.similarity.model2Score = []
    skill_matchmaker.similarity.ensembleScore = []
    with patch.object(skill_matchmaker, 'makeMatch', side_effect=Exception("Failure")):
        with pytest.raises(RuntimeError, match="Failed to get similarity score: Failure"):
            skill_matchmaker.getSimilarityScore()

def test_similarity_score_invalid(skill_matchmaker):
    skill_matchmaker.similarity.model1Score = '1'
    skill_matchmaker.similarity.model2Score = '2'
    skill_matchmaker.similarity.ensembleScore = 'ensemble'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        skill_matchmaker.getSimilarityScore()

def test_similarity_score_empty_list(skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    skill_matchmaker.model1 = model1Mock
    skill_matchmaker.model2 = model2Mock
    skill_matchmaker.similarity.model1Score = []
    skill_matchmaker.similarity.model2Score = []
    skill_matchmaker.similarity.ensembleScore = []
    skill_matchmaker.resumeSkill = " "
    skill_matchmaker.jobSkill = " "
    score = skill_matchmaker.getSimilarityScore()
    assert score == 0.0

def test_reset_success(skill_matchmaker):
    skill_matchmaker.similarity.model1Score = 0.8
    skill_matchmaker.similarity.model2Score = 0.6
    skill_matchmaker.similarity.ensembleScore = 0.7
    skill_matchmaker.model1 = MagicMock()
    skill_matchmaker.model2 = MagicMock()
    skill_matchmaker.reset()
    assert skill_matchmaker.similarity.model1Score is None
    assert skill_matchmaker.similarity.model2Score is None
    assert skill_matchmaker.similarity.ensembleScore is not None
    assert isinstance(skill_matchmaker.similarity.ensembleScore, list)
    assert skill_matchmaker.resumeSkill is None
    assert skill_matchmaker.jobSkill is None