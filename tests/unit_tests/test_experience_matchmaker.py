import pytest
from unittest.mock import patch, MagicMock
from src.experience_matchmaker.experience_matching import ExperienceMatching, ExperienceSimilarity, ExperienceNumeralizer
import numpy as np
import regex as re

pytestmark = pytest.mark.unit


@pytest.fixture
def experience_similarity():
    return ExperienceSimilarity()

@pytest.fixture
def experience_numerilzer():
    return ExperienceNumeralizer(mode='min')

@pytest.fixture
def experience_matchmaker():
    return ExperienceMatching()

def test_es_initialization(experience_similarity):
    assert experience_similarity.model1Score is None
    assert experience_similarity.model2Score is None
    assert experience_similarity.ensembleScore == []

def test_es_set_model1_score(experience_similarity):
    experience_similarity.setModel1Score([0.8])
    assert experience_similarity.model1Score == [0.8]
    with pytest.raises(ValueError, match="Score must be a list."):
        experience_similarity.setModel1Score('1')

def test_es_set_model2_score(experience_similarity):
    experience_similarity.setModel2Score([0.9])
    assert experience_similarity.model2Score == [0.9]
    with pytest.raises(ValueError, match="Score must be a list."):
        experience_similarity.setModel2Score('1')

def test_es_average_ensemble(experience_similarity):
    experience_similarity.setModel1Score([0.8])
    experience_similarity.setModel2Score([0.6])
    experience_similarity.averageEnsemble()
    assert len(experience_similarity.ensembleScore) > 0
    experience_similarity.model1Score = None
    experience_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        experience_similarity.averageEnsemble()

def test_es_hard_ensemble(experience_similarity):
    experience_similarity.setModel1Score([0.6])
    experience_similarity.setModel2Score([0.4])
    experience_similarity.hardEnsemble()
    assert len(experience_similarity.ensembleScore) > 0
    experience_similarity.setModel1Score([0.5])
    experience_similarity.setModel2Score([0.4])
    experience_similarity.hardEnsemble()
    assert len(experience_similarity.ensembleScore) > 0
    experience_similarity.setModel1Score([0.4])
    experience_similarity.setModel2Score([0.6])
    experience_similarity.hardEnsemble()
    assert len(experience_similarity.ensembleScore) > 0
    experience_similarity.model1Score = None
    experience_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        experience_similarity.hardEnsemble()

def test_es_get_ensemble_score(experience_similarity):
    experience_similarity.setModel1Score([0.4])
    experience_similarity.setModel2Score([0.6])
    experience_similarity.hardEnsemble()
    assert len(experience_similarity.ensembleScore) > 0
    experience_similarity.model1Score = None
    experience_similarity.model2Score = None
    experience_similarity.ensembleScore = None
    with pytest.raises(ValueError, match="Ensemble score has not been calculated."):
        experience_similarity.getEnsembleScore()
    experience_similarity.ensembleScore = '1'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        experience_similarity.getEnsembleScore()

def test_es_reset(experience_similarity):
    experience_similarity.setModel1Score([0.8])
    experience_similarity.setModel2Score([0.9])
    experience_similarity.ensembleScore = [0.85]
    experience_similarity.reset()
    assert experience_similarity.model1Score is None
    assert experience_similarity.model2Score is None
    assert experience_similarity.ensembleScore == []

# EXPERIENCE NUMERALIZER TESTS

def test_en_initialization_success(experience_numerilzer):
    assert isinstance(experience_numerilzer, ExperienceNumeralizer)
    assert isinstance(experience_numerilzer.pattern_single, re.Pattern)
    assert isinstance(experience_numerilzer.pattern_range, re.Pattern)
    assert isinstance(experience_numerilzer.years, list)
    assert experience_numerilzer.years == []
    assert experience_numerilzer.mode == 'min'

def test_en_initialization_failure(experience_numerilzer):
    with pytest.raises(ValueError, match="Mode cannot be None."):
        ExperienceNumeralizer()

def test_en_extract_years_success(experience_numerilzer):
    for mode in ['min', 'max', 'avg', 'sum']:
        experience_numerilzer.mode = mode
        testSentence = 'I have 2 years of experience in Python and 3-5 years in Java.'
        experience_numerilzer.extractYears(testSentence)
        assert len(experience_numerilzer.years) != 0
        testSentence = 'I have 2 years of experience in Python and 3-5 years in Java. I also have 1+ years of experience in C++.'
        experience_numerilzer.extractYears(testSentence)
        assert len(experience_numerilzer.years) != 0
        testSentence = 'I have 2 years of experience in Python and 3-5 years in Java. I also have 1+ years of experience in C++.'
        experience_numerilzer.extractYears(testSentence)
        assert len(experience_numerilzer.years) != 0

def test_en_extract_years_failure(experience_numerilzer):
    experience_numerilzer.mode = 'wrong_mode'
    testSentence = 'I have 2 years of experience in Python and 3-5 years in Java.'
    with pytest.raises(ValueError, match="Invalid mode. Use 'min' / 'max' / 'avg' / 'sum."):
        experience_numerilzer.extractYears(testSentence)

def test_en_get_years_success(experience_numerilzer):
    testSentence = 'I have 2 years of experience in Python and 3-5 years in Java.'
    experience_numerilzer.extractYears(testSentence)
    assert experience_numerilzer.getYears() is not None

def test_en_get_years_failure(experience_numerilzer):
    experience_numerilzer.years = []
    with pytest.raises(ValueError, match="No years extracted."):
        experience_numerilzer.getYears()

def test_en_reset(experience_numerilzer):
    testSentence = 'I have 2 years of experience in Python and 3-5 years in Java.'
    experience_numerilzer.extractYears(testSentence)
    assert len(experience_numerilzer.years) != 0
    experience_numerilzer.reset()
    assert len(experience_numerilzer.years) == 0
    assert experience_numerilzer.mode is None

# EXPERIENCE MATCHING TESTS

def test_initialization(experience_matchmaker):
    assert experience_matchmaker.model1 is not None
    assert experience_matchmaker.model2 is not None
    assert experience_matchmaker.resumeExperience is None
    assert experience_matchmaker.jobExperience is None
    assert experience_matchmaker.similarity is not None
    assert isinstance(experience_matchmaker.similarity, ExperienceSimilarity)

def test_set_inputs_success(experience_matchmaker):
    resumeExperience = "Bachelor of Science in Computer Science"
    jobExperience = "Master of Science in Computer Science"
    experience_matchmaker.setInputs(resumeExperience, jobExperience)
    assert experience_matchmaker.resumeExperience == [resumeExperience.lower()]
    assert experience_matchmaker.jobExperience == [jobExperience.lower()]

def test_set_inputs_failure(experience_matchmaker):
    resumeExperience = None
    jobExperience = "Master of Science in Computer Science"
    with pytest.raises(ValueError, match="Resume Experience and job Experience cannot be empty."):
        experience_matchmaker.setInputs(resumeExperience, jobExperience)
    
    resumeExperience = "Bachelor of Science in Computer Science"
    jobExperience = None
    with pytest.raises(ValueError, match="Resume Experience and job Experience cannot be empty."):
        experience_matchmaker.setInputs(resumeExperience, jobExperience)

    resumeExperience = ""
    jobExperience = "Master of Science in Computer Science"
    with pytest.raises(ValueError, match="Resume Experience and job Experience cannot be empty."):
        experience_matchmaker.setInputs(resumeExperience, jobExperience)
    
    resumeExperience = "Bachelor of Science in Computer Science"
    jobExperience = ""
    with pytest.raises(ValueError, match="Resume Experience and job Experience cannot be empty."):
        experience_matchmaker.setInputs(resumeExperience, jobExperience)

def test_set_inputs_invalid(experience_matchmaker):
    resumeExperience = 12345
    jobExperience = "Master of Science in Computer Science"
    with pytest.raises(ValueError, match="Resume Experience must be a string."):
        experience_matchmaker.setInputs(resumeExperience, jobExperience)
    
    resumeExperience = "Bachelor of Science in Computer Science"
    jobExperience = 12345
    with pytest.raises(ValueError, match="Job Experience must be a string."):
        experience_matchmaker.setInputs(resumeExperience, jobExperience)

def test_make_match_success(experience_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    experience_matchmaker.model1 = model1Mock
    experience_matchmaker.model2 = model2Mock
    experience_matchmaker.resumeExperience = "Bachelor of Science in Computer Science"
    experience_matchmaker.jobExperience = "Master of Science in Computer Science"
    model1Mock.encode.return_value = [np.array([[0.1, 0.2, 0.3]]), np.array([[0.1, 0.2, 0.3]])]
    model2Mock.encode.return_value = [np.array([[0.4, 0.5, 0.6]]), np.array([[0.4, 0.5, 0.6]])]
    experience_matchmaker.resumeNumeralizer.extractYears = MagicMock(return_value=2.0)
    experience_matchmaker.jobNumeralizer.extractYears = MagicMock(return_value=4.0)
    with patch('src.experience_matchmaker.experience_matching.cosine_similarity', return_value=np.array([[1.0]])):
        score = experience_matchmaker.makeMatch()
    assert score == 0.5


def test_make_match_no_models(experience_matchmaker):
    experience_matchmaker.model1 = None
    experience_matchmaker.model2 = None
    experience_matchmaker.modelName1 = None
    experience_matchmaker.modelName2 = None
    with pytest.raises(RuntimeError, match="Failed to load models"):
        experience_matchmaker.makeMatch()

def test_make_match_no_model_names(experience_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    experience_matchmaker.model1 = model1Mock
    experience_matchmaker.model2 = model2Mock
    with pytest.raises(ValueError, match="Inputs are not set"):
        experience_matchmaker.makeMatch()

def test_make_match_failure(experience_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    experience_matchmaker.model1 = model1Mock
    experience_matchmaker.model2 = model2Mock
    experience_matchmaker.resumeExperience = "Bachelor of Science in Computer Science"
    experience_matchmaker.jobExperience = "Master of Science in Computer Science"
    model1Mock.encode.side_effect = Exception("Encoding failed")
    with pytest.raises(RuntimeError, match="Failed to make match: Encoding failed"):
        experience_matchmaker.makeMatch()

def test_similarity_score_success(experience_matchmaker):
    experience_matchmaker.similarity.model1Score = [0.8]
    experience_matchmaker.similarity.model2Score = [0.6]
    experience_matchmaker.similarity.ensembleScore = [0.7]
    score = experience_matchmaker.getSimilarityScore()
    assert score == 0.7

def test_similarity_score_no_ensemble(experience_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    experience_matchmaker.model1 = model1Mock
    experience_matchmaker.model2 = model2Mock
    experience_matchmaker.similarity.ensembleScore = None
    with patch.object(experience_matchmaker, 'makeMatch', side_effect=Exception("Failure")):
        with pytest.raises(RuntimeError, match="Failed to get similarity score: Failure"):
            experience_matchmaker.getSimilarityScore()

def test_similarity_score_invalid(experience_matchmaker):
    experience_matchmaker.similarity.model1Score = '1'
    experience_matchmaker.similarity.model2Score = '2'
    experience_matchmaker.similarity.ensembleScore = 'ensemble'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        experience_matchmaker.getSimilarityScore()

def test_reset_success(experience_matchmaker):
    experience_matchmaker.similarity.model1Score = 0.8
    experience_matchmaker.similarity.model2Score = 0.6
    experience_matchmaker.similarity.ensembleScore = 0.7
    experience_matchmaker.reset()
    assert experience_matchmaker.similarity.model1Score is None
    assert experience_matchmaker.similarity.model2Score is None
    assert experience_matchmaker.similarity.ensembleScore == []
    assert experience_matchmaker.resumeExperience is None
    assert experience_matchmaker.jobExperience is None