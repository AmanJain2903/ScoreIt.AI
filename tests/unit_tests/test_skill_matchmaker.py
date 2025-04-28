import pytest
from unittest.mock import patch, MagicMock
from src.skill_matchmaker.skill_matching import SkillMatching, SkillSimilarity
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def skill_matchmaker():
    return SkillMatching(modelName1='Model1', modelName2='Model2', maxInputLength=10000)

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
    assert skill_matchmaker.modelName1 == 'Model1'
    assert skill_matchmaker.modelName2 == 'Model2'
    assert skill_matchmaker.maxInputLength == 10000
    assert skill_matchmaker.model1 is None
    assert skill_matchmaker.model2 is None
    assert skill_matchmaker.resumeSkill is None
    assert skill_matchmaker.jobSkill is None
    assert skill_matchmaker.similarity is not None
    assert isinstance(skill_matchmaker.similarity, SkillSimilarity)

@patch('src.skill_matchmaker.skill_matching.SentenceTransformer')
def test_load_models_success(mock_sentence_transformer, skill_matchmaker):
    mockModel1 = MagicMock()
    mockModel2 = MagicMock()
    mock_sentence_transformer.side_effect = [mockModel1, mockModel2]
    skill_matchmaker.loadModels()
    assert skill_matchmaker.model1 is not None
    assert skill_matchmaker.model2 is not None
    assert skill_matchmaker.model1 == mockModel1
    assert skill_matchmaker.model2 == mockModel2

def test_load_models_no_names(skill_matchmaker):
    skill_matchmaker.modelName1 = None
    skill_matchmaker.modelName2 = None
    with pytest.raises(ValueError, match="Model names cannot be empty."):
        skill_matchmaker.loadModels()

@patch('src.skill_matchmaker.skill_matching.SentenceTransformer')
def test_load_models_failure(mock_sentence_transformer, skill_matchmaker):
    mock_sentence_transformer.side_effect = Exception("Model loading failed")
    with pytest.raises(RuntimeError, match="Failed to load models 'Model1' and 'Model2': Model loading failed"):
        skill_matchmaker.loadModels()

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

    resumeSkill = ""
    jobSkill = "Python, Machine Learning, Data Science"
    with pytest.raises(ValueError, match="Resume skill and job skill cannot be empty."):
        skill_matchmaker.setInputs(resumeSkill, jobSkill)
    
    resumeSkill = "Python, Machine Learning, Data Science"
    jobSkill = ""
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

@patch('src.skill_matchmaker.skill_matching.SentenceTransformer')
def test_make_match_success(mock_sentence_transformer, skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
    skill_matchmaker.model1 = model1Mock
    skill_matchmaker.model2 = model2Mock
    skill_matchmaker.resumeSkill = ['python', 'java']
    skill_matchmaker.jobSkill = ['python', 'machine learning', 'data science']
    model1Mock.encode.return_value = [np.array([[0.1]]) * 6]
    model2Mock.encode.return_value = [np.array([[0.1]]) * 6]
    with patch('src.skill_matchmaker.skill_matching.cosine_similarity', return_value=np.array([[1.0]])):
            score = skill_matchmaker.makeMatch()
    assert score == 1.0
    assert model1Mock.encode.call_count == 9
    assert model2Mock.encode.call_count == 9


@patch('src.skill_matchmaker.skill_matching.SentenceTransformer')
def test_make_match_no_models(mock_sentence_transformer, skill_matchmaker):
    skill_matchmaker.model1 = None
    skill_matchmaker.model2 = None
    skill_matchmaker.modelName1 = None
    skill_matchmaker.modelName2 = None
    with pytest.raises(RuntimeError, match="Failed to load models: Model names cannot be empty."):
        skill_matchmaker.makeMatch()

@patch('src.skill_matchmaker.skill_matching.SentenceTransformer')
def test_make_match_no_model_names(mock_sentence_transformer, skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
    skill_matchmaker.model1 = model1Mock
    skill_matchmaker.model2 = model2Mock
    with pytest.raises(ValueError, match="Inputs are not set"):
        skill_matchmaker.makeMatch()

@patch('src.skill_matchmaker.skill_matching.SentenceTransformer')
def test_make_match_failure(mock_sentence_transformer, skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
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

@patch('src.skill_matchmaker.skill_matching.SentenceTransformer')
def test_similarity_score_no_ensemble(mock_sentence_transformer, skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
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

@patch('src.skill_matchmaker.skill_matching.SentenceTransformer')
def test_similarity_score_empty_list(mock_sentence_transformer, skill_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
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
    assert skill_matchmaker.model1 is None
    assert skill_matchmaker.model2 is None
    assert skill_matchmaker.modelName1 == 'Model1'
    assert skill_matchmaker.modelName2 == 'Model2'