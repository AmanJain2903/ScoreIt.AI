import pytest
from unittest.mock import patch, MagicMock
from src.designation_matchmaker.designation_matching import DesignationMatching, DesignationSimilarity
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def designation_matchmaker():
    return DesignationMatching(modelName1='Model1', modelName2='Model2', maxInputLength=10000)

@pytest.fixture
def designation_similarity():
    return DesignationSimilarity()

def test_ts_initialization(designation_similarity):
    assert designation_similarity.model1Score is None
    assert designation_similarity.model2Score is None
    assert designation_similarity.ensembleScore is not None
    assert isinstance(designation_similarity.ensembleScore, list)

def test_ts_set_model1_score(designation_similarity):
    designation_similarity.setModel1Score([0.8])
    assert designation_similarity.model1Score == [0.8]
    with pytest.raises(ValueError, match="Score must be a list."):
        designation_similarity.setModel1Score('1')

def test_ts_set_model2_score(designation_similarity):
    designation_similarity.setModel2Score([0.9])
    assert designation_similarity.model2Score == [0.9]
    with pytest.raises(ValueError, match="Score must be a list."):
        designation_similarity.setModel2Score('1')

def test_ts_average_ensemble(designation_similarity):
    designation_similarity.setModel1Score([0.8])
    designation_similarity.setModel2Score([0.6])
    designation_similarity.averageEnsemble()
    assert isinstance(designation_similarity.ensembleScore, list)
    assert len(designation_similarity.ensembleScore) == 1
    designation_similarity.model1Score = None
    designation_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        designation_similarity.averageEnsemble()

def test_ts_hard_ensemble(designation_similarity):
    designation_similarity.setModel1Score([0.9])
    designation_similarity.setModel2Score([0.5])
    designation_similarity.hardEnsemble()
    assert isinstance(designation_similarity.ensembleScore, list)
    assert len(designation_similarity.ensembleScore) == 1
    designation_similarity.reset()
    designation_similarity.setModel1Score([0.7])
    designation_similarity.setModel2Score([0.8])
    designation_similarity.hardEnsemble()
    assert isinstance(designation_similarity.ensembleScore, list)
    assert len(designation_similarity.ensembleScore) == 1
    designation_similarity.reset()
    designation_similarity.setModel1Score([0.9])
    designation_similarity.setModel2Score([0.9])
    designation_similarity.hardEnsemble()
    assert isinstance(designation_similarity.ensembleScore, list)
    assert len(designation_similarity.ensembleScore) == 1
    designation_similarity.reset()
    designation_similarity.model1Score = None
    designation_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        designation_similarity.hardEnsemble()

def test_ts_get_ensemble_score(designation_similarity):
    designation_similarity.setModel1Score([0.7])
    designation_similarity.setModel2Score([0.8])
    designation_similarity.hardEnsemble()
    assert isinstance(designation_similarity.ensembleScore, list)
    assert len(designation_similarity.ensembleScore) == 1
    designation_similarity.model1Score = None
    designation_similarity.model2Score = None
    designation_similarity.ensembleScore = None
    with pytest.raises(ValueError, match="Ensemble score has not been calculated."):
        designation_similarity.getEnsembleScore()
    designation_similarity.ensembleScore = '1'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        designation_similarity.getEnsembleScore()

def test_ts_reset(designation_similarity):
    designation_similarity.setModel1Score([0.8])
    designation_similarity.setModel2Score([0.9])
    designation_similarity.ensembleScore = [0.85]
    designation_similarity.reset()
    assert designation_similarity.model1Score is None
    assert designation_similarity.model2Score is None
    assert designation_similarity.ensembleScore is not None
    assert isinstance(designation_similarity.ensembleScore, list)

def test_initialization(designation_matchmaker):
    assert designation_matchmaker.modelName1 == 'Model1'
    assert designation_matchmaker.modelName2 == 'Model2'
    assert designation_matchmaker.maxInputLength == 10000
    assert designation_matchmaker.model1 is None
    assert designation_matchmaker.model2 is None
    assert designation_matchmaker.resumeDesignation is None
    assert designation_matchmaker.jobDesignation is None
    assert designation_matchmaker.similarity is not None
    assert isinstance(designation_matchmaker.similarity, DesignationSimilarity)

@patch('src.designation_matchmaker.designation_matching.SentenceTransformer')
def test_load_models_success(mock_sentence_transformer, designation_matchmaker):
    mockModel1 = MagicMock()
    mockModel2 = MagicMock()
    mock_sentence_transformer.side_effect = [mockModel1, mockModel2]
    designation_matchmaker.loadModels()
    assert designation_matchmaker.model1 is not None
    assert designation_matchmaker.model2 is not None
    assert designation_matchmaker.model1 == mockModel1
    assert designation_matchmaker.model2 == mockModel2

def test_load_models_no_names(designation_matchmaker):
    designation_matchmaker.modelName1 = None
    designation_matchmaker.modelName2 = None
    with pytest.raises(ValueError, match="Model names cannot be empty."):
        designation_matchmaker.loadModels()

@patch('src.designation_matchmaker.designation_matching.SentenceTransformer')
def test_load_models_failure(mock_sentence_transformer, designation_matchmaker):
    mock_sentence_transformer.side_effect = Exception("Model loading failed")
    with pytest.raises(RuntimeError, match="Failed to load models 'Model1' and 'Model2': Model loading failed"):
        designation_matchmaker.loadModels()

def test_set_inputs_success(designation_matchmaker):
    resumeDesignation = "Software Engineer, Backend Developer, Full Stack Developer"
    jobDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"
    designation_matchmaker.setInputs(resumeDesignation, jobDesignation)
    assert len(designation_matchmaker.resumeDesignation) == 3
    assert len(designation_matchmaker.jobDesignation) == 3
    assert isinstance(designation_matchmaker.resumeDesignation, list)
    assert isinstance(designation_matchmaker.jobDesignation, list)

def test_set_inputs_failure(designation_matchmaker):
    resumeDesignation = None
    jobDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"
    with pytest.raises(ValueError, match="Resume designation and job designation cannot be empty."):
        designation_matchmaker.setInputs(resumeDesignation, jobDesignation)
    
    resumeDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"
    jobDesignation = None
    with pytest.raises(ValueError, match="Resume designation and job designation cannot be empty."):
        designation_matchmaker.setInputs(resumeDesignation, jobDesignation)

    resumeDesignation = ""
    jobDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"
    with pytest.raises(ValueError, match="Resume designation and job designation cannot be empty."):
        designation_matchmaker.setInputs(resumeDesignation, jobDesignation)
    
    resumeDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"
    jobDesignation = ""
    with pytest.raises(ValueError, match="Resume designation and job designation cannot be empty."):
        designation_matchmaker.setInputs(resumeDesignation, jobDesignation)

def test_set_inputs_invalid(designation_matchmaker):
    resumeDesignation = 12345
    jobDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"
    with pytest.raises(ValueError, match="Resume designation must be a string."):
        designation_matchmaker.setInputs(resumeDesignation, jobDesignation)
    
    resumeDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"
    jobDesignation = 12345
    with pytest.raises(ValueError, match="Job designation must be a string."):
        designation_matchmaker.setInputs(resumeDesignation, jobDesignation)

@patch('src.designation_matchmaker.designation_matching.SentenceTransformer')
def test_make_match_success(mock_sentence_transformer, designation_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
    designation_matchmaker.model1 = model1Mock
    designation_matchmaker.model2 = model2Mock
    designation_matchmaker.resumeDesignation = ["Senior Software Engineer", "Full Stack Engineer", "Backend Developer"]
    designation_matchmaker.jobDesignation = ["Software Engineer", "Backend Developer", "Full Stack Developer"]
    model1Mock.encode.return_value = [np.array([[0.1]])]
    model2Mock.encode.return_value = [np.array([[0.1]])]
    with patch('src.designation_matchmaker.designation_matching.cosine_similarity', return_value=np.array([[1.0]])):
            score = designation_matchmaker.makeMatch()
    assert score == 1.0


@patch('src.designation_matchmaker.designation_matching.SentenceTransformer')
def test_make_match_no_models(mock_sentence_transformer, designation_matchmaker):
    designation_matchmaker.model1 = None
    designation_matchmaker.model2 = None
    designation_matchmaker.modelName1 = None
    designation_matchmaker.modelName2 = None
    with pytest.raises(RuntimeError, match="Failed to load models: Model names cannot be empty."):
        designation_matchmaker.makeMatch()

@patch('src.designation_matchmaker.designation_matching.SentenceTransformer')
def test_make_match_no_model_names(mock_sentence_transformer, designation_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
    designation_matchmaker.model1 = model1Mock
    designation_matchmaker.model2 = model2Mock
    with pytest.raises(ValueError, match="Inputs are not set"):
        designation_matchmaker.makeMatch()

@patch('src.designation_matchmaker.designation_matching.SentenceTransformer')
def test_make_match_failure(mock_sentence_transformer, designation_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
    designation_matchmaker.resumeDesignation = "Software Engineer, Backend Developer, Full Stack Developer"
    designation_matchmaker.jobDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"
    model1Mock.encode.side_effect = Exception("Encoding failed")
    with pytest.raises(RuntimeError, match="Failed to make match: Encoding failed"):
        designation_matchmaker.makeMatch()

def test_similarity_score_success(designation_matchmaker):
    designation_matchmaker.similarity.model1Score = [0.8, 0.9]
    designation_matchmaker.similarity.model2Score = [0.6, 0.7]
    designation_matchmaker.similarity.ensembleScore = [0.7, 0.8]
    score = designation_matchmaker.getSimilarityScore()
    assert score == 0.75

@patch('src.designation_matchmaker.designation_matching.SentenceTransformer')
def test_similarity_score_no_ensemble(mock_sentence_transformer, designation_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
    designation_matchmaker.model1 = model1Mock
    designation_matchmaker.model2 = model2Mock
    designation_matchmaker.similarity.model1Score = []
    designation_matchmaker.similarity.model2Score = []
    designation_matchmaker.similarity.ensembleScore = []
    with patch.object(designation_matchmaker, 'makeMatch', side_effect=Exception("Failure")):
        with pytest.raises(RuntimeError, match="Failed to get similarity score: Failure"):
            designation_matchmaker.getSimilarityScore()

def test_similarity_score_invalid(designation_matchmaker):
    designation_matchmaker.similarity.model1Score = '1'
    designation_matchmaker.similarity.model2Score = '2'
    designation_matchmaker.similarity.ensembleScore = 'ensemble'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        designation_matchmaker.getSimilarityScore()

@patch('src.designation_matchmaker.designation_matching.SentenceTransformer')
def test_similarity_score_empty_list(mock_sentence_transformer, designation_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    mock_sentence_transformer.side_effect = [model1Mock, model2Mock]
    designation_matchmaker.model1 = model1Mock
    designation_matchmaker.model2 = model2Mock
    designation_matchmaker.similarity.model1Score = []
    designation_matchmaker.similarity.model2Score = []
    designation_matchmaker.similarity.ensembleScore = []
    designation_matchmaker.resumeDesignation = " "
    designation_matchmaker.jobDesignation = " "
    score = designation_matchmaker.getSimilarityScore()
    assert score == 0.0

def test_reset_success(designation_matchmaker):
    designation_matchmaker.similarity.model1Score = 0.8
    designation_matchmaker.similarity.model2Score = 0.6
    designation_matchmaker.similarity.ensembleScore = 0.7
    designation_matchmaker.model1 = MagicMock()
    designation_matchmaker.model2 = MagicMock()
    designation_matchmaker.reset()
    assert designation_matchmaker.similarity.model1Score is None
    assert designation_matchmaker.similarity.model2Score is None
    assert designation_matchmaker.similarity.ensembleScore is not None
    assert isinstance(designation_matchmaker.similarity.ensembleScore, list)
    assert designation_matchmaker.resumeDesignation is None
    assert designation_matchmaker.jobDesignation is None
    assert designation_matchmaker.model1 is None
    assert designation_matchmaker.model2 is None
    assert designation_matchmaker.modelName1 == 'Model1'
    assert designation_matchmaker.modelName2 == 'Model2'