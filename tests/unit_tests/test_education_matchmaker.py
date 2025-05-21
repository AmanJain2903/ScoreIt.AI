import pytest
from unittest.mock import patch, MagicMock
from src.education_matchmaker.education_matching import EducationMatching, EducationSimilarity
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def education_matchmaker():
    return EducationMatching()

@pytest.fixture
def education_similarity():
    return EducationSimilarity()

def test_es_initialization(education_similarity):
    assert education_similarity.model1Score is None
    assert education_similarity.model2Score is None
    assert education_similarity.ensembleScore == []

def test_es_set_model1_score(education_similarity):
    education_similarity.setModel1Score([0.8])
    assert education_similarity.model1Score == [0.8]
    with pytest.raises(ValueError, match="Score must be a list."):
        education_similarity.setModel1Score('1')

def test_es_set_model2_score(education_similarity):
    education_similarity.setModel2Score([0.9])
    assert education_similarity.model2Score == [0.9]
    with pytest.raises(ValueError, match="Score must be a list."):
        education_similarity.setModel2Score('1')

def test_es_average_ensemble(education_similarity):
    education_similarity.setModel1Score([0.8])
    education_similarity.setModel2Score([0.6])
    education_similarity.averageEnsemble()
    assert len(education_similarity.ensembleScore) > 0
    education_similarity.model1Score = None
    education_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        education_similarity.averageEnsemble()

def test_es_hard_ensemble(education_similarity):
    education_similarity.setModel1Score([0.9])
    education_similarity.setModel2Score([0.5])
    education_similarity.hardEnsemble()
    assert len(education_similarity.ensembleScore) > 0
    education_similarity.setModel1Score([0.7])
    education_similarity.setModel2Score([0.8])
    education_similarity.hardEnsemble()
    assert len(education_similarity.ensembleScore) > 0
    education_similarity.setModel1Score([0.9])
    education_similarity.setModel2Score([0.9])
    education_similarity.hardEnsemble()
    assert len(education_similarity.ensembleScore) > 0
    education_similarity.model1Score = None
    education_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        education_similarity.hardEnsemble()

def test_es_get_ensemble_score(education_similarity):
    education_similarity.setModel1Score([0.7])
    education_similarity.setModel2Score([0.8])
    education_similarity.hardEnsemble()
    assert len(education_similarity.ensembleScore) > 0
    education_similarity.model1Score = None
    education_similarity.model2Score = None
    education_similarity.ensembleScore = None
    with pytest.raises(ValueError, match="Ensemble score has not been calculated."):
        education_similarity.getEnsembleScore()
    education_similarity.ensembleScore = '1'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        education_similarity.getEnsembleScore()

def test_es_reset(education_similarity):
    education_similarity.setModel1Score([0.8])
    education_similarity.setModel2Score([0.9])
    education_similarity.ensembleScore = [0.85]
    education_similarity.reset()
    assert education_similarity.model1Score is None
    assert education_similarity.model2Score is None
    assert education_similarity.ensembleScore == []

def test_initialization(education_matchmaker):
    assert education_matchmaker.model1 is not None
    assert education_matchmaker.model2 is not None
    assert education_matchmaker.resumeEducation is None
    assert education_matchmaker.jobEducation is None
    assert education_matchmaker.similarity is not None
    assert isinstance(education_matchmaker.similarity, EducationSimilarity)


def test_set_inputs_success(education_matchmaker):
    resumeEducation = "Bachelor of Science in Computer Science"
    jobEducation = "Master of Science in Computer Science"
    education_matchmaker.setInputs(resumeEducation, jobEducation)
    assert education_matchmaker.resumeEducation == [resumeEducation.lower()]
    assert education_matchmaker.jobEducation == [jobEducation.lower()]

def test_set_inputs_failure(education_matchmaker):
    resumeEducation = None
    jobEducation = "Master of Science in Computer Science"
    with pytest.raises(ValueError, match="Resume education and job education cannot be empty."):
        education_matchmaker.setInputs(resumeEducation, jobEducation)
    
    resumeEducation = "Bachelor of Science in Computer Science"
    jobEducation = None
    with pytest.raises(ValueError, match="Resume education and job education cannot be empty."):
        education_matchmaker.setInputs(resumeEducation, jobEducation)

    resumeEducation = ""
    jobEducation = "Master of Science in Computer Science"
    with pytest.raises(ValueError, match="Resume education and job education cannot be empty."):
        education_matchmaker.setInputs(resumeEducation, jobEducation)
    
    resumeEducation = "Bachelor of Science in Computer Science"
    jobEducation = ""
    with pytest.raises(ValueError, match="Resume education and job education cannot be empty."):
        education_matchmaker.setInputs(resumeEducation, jobEducation)

def test_set_inputs_invalid(education_matchmaker):
    resumeEducation = 12345
    jobEducation = "Master of Science in Computer Science"
    with pytest.raises(ValueError, match="Resume education must be a string."):
        education_matchmaker.setInputs(resumeEducation, jobEducation)
    
    resumeEducation = "Bachelor of Science in Computer Science"
    jobEducation = 12345
    with pytest.raises(ValueError, match="Job education must be a string."):
        education_matchmaker.setInputs(resumeEducation, jobEducation)

def test_make_match_success(education_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    education_matchmaker.model1 = model1Mock
    education_matchmaker.model2 = model2Mock
    education_matchmaker.resumeEducation = "Bachelor of Science in Computer Science"
    education_matchmaker.jobEducation = "Master of Science in Computer Science"
    model1Mock.encode.return_value = [np.array([[0.1, 0.2, 0.3]]), np.array([[0.1, 0.2, 0.3]])]
    model2Mock.encode.return_value = [np.array([[0.4, 0.5, 0.6]]), np.array([[0.4, 0.5, 0.6]])]
    with patch('src.education_matchmaker.education_matching.cosine_similarity', return_value=np.array([[1.0]])):
        score = education_matchmaker.makeMatch()
    assert score == 0.7


def test_make_match_no_models(education_matchmaker):
    education_matchmaker.model1 = None
    education_matchmaker.model2 = None
    with pytest.raises(RuntimeError, match="Failed to load models"):
        education_matchmaker.makeMatch()

def test_make_match_no_model_names(education_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    education_matchmaker.model1 = model1Mock
    education_matchmaker.model2 = model2Mock
    with pytest.raises(ValueError, match="Inputs are not set"):
        education_matchmaker.makeMatch()

def test_make_match_failure(education_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    education_matchmaker.model1 = model1Mock
    education_matchmaker.model2 = model2Mock
    education_matchmaker.resumeEducation = "Bachelor of Science in Computer Science"
    education_matchmaker.jobEducation = "Master of Science in Computer Science"
    model1Mock.encode.side_effect = Exception("Encoding failed")
    with pytest.raises(RuntimeError, match="Failed to make match: Encoding failed"):
        education_matchmaker.makeMatch()

def test_similarity_score_success(education_matchmaker):
    education_matchmaker.similarity.model1Score = [0.8]
    education_matchmaker.similarity.model2Score = [0.6]
    education_matchmaker.similarity.ensembleScore = [0.7]
    score = education_matchmaker.getSimilarityScore()
    assert score == 0.7

def test_similarity_score_no_ensemble(education_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    education_matchmaker.model1 = model1Mock
    education_matchmaker.model2 = model2Mock
    education_matchmaker.similarity.ensembleScore = None
    with patch.object(education_matchmaker, 'makeMatch', side_effect=Exception("Failure")):
        with pytest.raises(RuntimeError, match="Failed to get similarity score: Failure"):
            education_matchmaker.getSimilarityScore()

def test_similarity_score_invalid(education_matchmaker):
    education_matchmaker.similarity.model1Score = '1'
    education_matchmaker.similarity.model2Score = '2'
    education_matchmaker.similarity.ensembleScore = 'ensemble'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        education_matchmaker.getSimilarityScore()

def test_reset_success(education_matchmaker):
    education_matchmaker.similarity.model1Score = [0.8]
    education_matchmaker.similarity.model2Score = [0.6]
    education_matchmaker.similarity.ensembleScore = [0.7]
    education_matchmaker.reset()
    assert education_matchmaker.similarity.model1Score is None
    assert education_matchmaker.similarity.model2Score is None
    assert education_matchmaker.similarity.ensembleScore == []
    assert education_matchmaker.resumeEducation is None
    assert education_matchmaker.jobEducation is None