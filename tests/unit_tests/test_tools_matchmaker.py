import pytest
from unittest.mock import patch, MagicMock
from src.tools_matchmaker.tools_matching import ToolMatching, ToolSimilarity
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def tools_matchmaker():
    return ToolMatching(maxInputLength=10000)

@pytest.fixture
def tools_similarity():
    return ToolSimilarity()

def test_ts_initialization(tools_similarity):
    assert tools_similarity.model1Score is None
    assert tools_similarity.model2Score is None
    assert tools_similarity.ensembleScore is not None
    assert isinstance(tools_similarity.ensembleScore, list)

def test_ts_set_model1_score(tools_similarity):
    tools_similarity.setModel1Score([0.8])
    assert tools_similarity.model1Score == [0.8]
    with pytest.raises(ValueError, match="Score must be a list."):
        tools_similarity.setModel1Score('1')

def test_ts_set_model2_score(tools_similarity):
    tools_similarity.setModel2Score([0.9])
    assert tools_similarity.model2Score == [0.9]
    with pytest.raises(ValueError, match="Score must be a list."):
        tools_similarity.setModel2Score('1')

def test_ts_average_ensemble(tools_similarity):
    tools_similarity.setModel1Score([0.8])
    tools_similarity.setModel2Score([0.6])
    tools_similarity.averageEnsemble()
    assert isinstance(tools_similarity.ensembleScore, list)
    assert len(tools_similarity.ensembleScore) == 1
    tools_similarity.model1Score = None
    tools_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        tools_similarity.averageEnsemble()

def test_ts_hard_ensemble(tools_similarity):
    tools_similarity.setModel1Score([0.9])
    tools_similarity.setModel2Score([0.5])
    tools_similarity.hardEnsemble()
    assert isinstance(tools_similarity.ensembleScore, list)
    assert len(tools_similarity.ensembleScore) == 1
    tools_similarity.reset()
    tools_similarity.setModel1Score([0.7])
    tools_similarity.setModel2Score([0.8])
    tools_similarity.hardEnsemble()
    assert isinstance(tools_similarity.ensembleScore, list)
    assert len(tools_similarity.ensembleScore) == 1
    tools_similarity.reset()
    tools_similarity.setModel1Score([0.9])
    tools_similarity.setModel2Score([0.9])
    tools_similarity.hardEnsemble()
    assert isinstance(tools_similarity.ensembleScore, list)
    assert len(tools_similarity.ensembleScore) == 1
    tools_similarity.reset()
    tools_similarity.model1Score = None
    tools_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        tools_similarity.hardEnsemble()

def test_ts_get_ensemble_score(tools_similarity):
    tools_similarity.setModel1Score([0.7])
    tools_similarity.setModel2Score([0.8])
    tools_similarity.hardEnsemble()
    assert isinstance(tools_similarity.ensembleScore, list)
    assert len(tools_similarity.ensembleScore) == 1
    tools_similarity.model1Score = None
    tools_similarity.model2Score = None
    tools_similarity.ensembleScore = None
    with pytest.raises(ValueError, match="Ensemble score has not been calculated."):
        tools_similarity.getEnsembleScore()
    tools_similarity.ensembleScore = '1'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        tools_similarity.getEnsembleScore()

def test_ts_reset(tools_similarity):
    tools_similarity.setModel1Score([0.8])
    tools_similarity.setModel2Score([0.9])
    tools_similarity.ensembleScore = [0.85]
    tools_similarity.reset()
    assert tools_similarity.model1Score is None
    assert tools_similarity.model2Score is None
    assert tools_similarity.ensembleScore is not None
    assert isinstance(tools_similarity.ensembleScore, list)

def test_initialization(tools_matchmaker):
    assert tools_matchmaker.maxInputLength == 10000
    assert tools_matchmaker.model1 is not None
    assert tools_matchmaker.model2 is not None
    assert tools_matchmaker.resumeTool is None
    assert tools_matchmaker.jobTool is None
    assert tools_matchmaker.similarity is not None
    assert isinstance(tools_matchmaker.similarity, ToolSimilarity)

def test_set_inputs_success(tools_matchmaker):
    resumeTool = "Docker, Kubernetes, Git, Jenkins, VS Code, Postman, Jira, MongoDB"
    jobTool = "Docker, GitHub, Jenkins, Azure DevOps, Jira, MySQL, Postman"
    tools_matchmaker.setInputs(resumeTool, jobTool)
    assert len(tools_matchmaker.resumeTool) == 8
    assert len(tools_matchmaker.jobTool) == 7
    assert isinstance(tools_matchmaker.resumeTool, list)
    assert isinstance(tools_matchmaker.jobTool, list)

def test_set_inputs_failure(tools_matchmaker):
    resumeTool = None
    jobTool = "Docker, GitHub, Jenkins, Azure DevOps, Jira, MySQL, Postman"
    with pytest.raises(ValueError, match="Resume tools and job tools cannot be empty."):
        tools_matchmaker.setInputs(resumeTool, jobTool)
    
    resumeTool = "Docker, GitHub, Jenkins, Azure DevOps, Jira, MySQL, Postman"
    jobTool = None
    with pytest.raises(ValueError, match="Resume tools and job tools cannot be empty."):
        tools_matchmaker.setInputs(resumeTool, jobTool)

    resumeTool = ""
    jobTool = "Docker, GitHub, Jenkins, Azure DevOps, Jira, MySQL, Postman"
    with pytest.raises(ValueError, match="Resume tools and job tools cannot be empty."):
        tools_matchmaker.setInputs(resumeTool, jobTool)
    
    resumeTool = "Docker, GitHub, Jenkins, Azure DevOps, Jira, MySQL, Postman"
    jobTool = ""
    with pytest.raises(ValueError, match="Resume tools and job tools cannot be empty."):
        tools_matchmaker.setInputs(resumeTool, jobTool)

def test_set_inputs_invalid(tools_matchmaker):
    resumeTool = 12345
    jobTool = "Docker, GitHub, Jenkins, Azure DevOps, Jira, MySQL, Postman"
    with pytest.raises(ValueError, match="Resume tools must be a string."):
        tools_matchmaker.setInputs(resumeTool, jobTool)
    
    resumeTool = "Docker, GitHub, Jenkins, Azure DevOps, Jira, MySQL, Postman"
    jobTool = 12345
    with pytest.raises(ValueError, match="Job tools must be a string."):
        tools_matchmaker.setInputs(resumeTool, jobTool)

def test_make_match_success(tools_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    tools_matchmaker.model1 = model1Mock
    tools_matchmaker.model2 = model2Mock
    tools_matchmaker.resumeTool = ['Docker', 'Kubernetes', 'Git', 'Jenkins', 'VS Code', 'Postman', 'Jira', 'MongoDB']
    tools_matchmaker.jobTool = ['Docker', 'GitHub', 'Jenkins', 'Azure DevOps', 'Jira', 'MySQL', 'Postman']
    model1Mock.encode.return_value = [np.array([[0.1]])]
    model2Mock.encode.return_value = [np.array([[0.1]])]
    with patch('src.tools_matchmaker.tools_matching.cosine_similarity', return_value=np.array([[1.0]])):
            score = tools_matchmaker.makeMatch()
    assert score == 1.0


def test_make_match_no_models(tools_matchmaker):
    tools_matchmaker.model1 = None
    tools_matchmaker.model2 = None
    with pytest.raises(RuntimeError, match="Failed to load models"):
        tools_matchmaker.makeMatch()

def test_make_match_no_model_names(tools_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    tools_matchmaker.model1 = model1Mock
    tools_matchmaker.model2 = model2Mock
    with pytest.raises(ValueError, match="Inputs are not set"):
        tools_matchmaker.makeMatch()

def test_make_match_failure(tools_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    tools_matchmaker.model1 = model1Mock
    tools_matchmaker.model2 = model2Mock
    tools_matchmaker.resumeTool = "Docker, Kubernetes, Git, Jenkins, VS Code, Postman, Jira, MongoDB"
    tools_matchmaker.jobTool = "Docker, GitHub, Jenkins, Azure DevOps, Jira, MySQL, Postman"
    model1Mock.encode.side_effect = Exception("Encoding failed")
    with pytest.raises(RuntimeError, match="Failed to make match: Encoding failed"):
        tools_matchmaker.makeMatch()

def test_similarity_score_success(tools_matchmaker):
    tools_matchmaker.similarity.model1Score = [0.8, 0.9]
    tools_matchmaker.similarity.model2Score = [0.6, 0.7]
    tools_matchmaker.similarity.ensembleScore = [0.7, 0.8]
    score = tools_matchmaker.getSimilarityScore()
    assert score == 0.75

def test_similarity_score_no_ensemble(tools_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    tools_matchmaker.model1 = model1Mock
    tools_matchmaker.model2 = model2Mock
    tools_matchmaker.similarity.model1Score = []
    tools_matchmaker.similarity.model2Score = []
    tools_matchmaker.similarity.ensembleScore = []
    with patch.object(tools_matchmaker, 'makeMatch', side_effect=Exception("Failure")):
        with pytest.raises(RuntimeError, match="Failed to get similarity score: Failure"):
            tools_matchmaker.getSimilarityScore()

def test_similarity_score_invalid(tools_matchmaker):
    tools_matchmaker.similarity.model1Score = '1'
    tools_matchmaker.similarity.model2Score = '2'
    tools_matchmaker.similarity.ensembleScore = 'ensemble'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        tools_matchmaker.getSimilarityScore()

def test_similarity_score_empty_list(tools_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    tools_matchmaker.model1 = model1Mock
    tools_matchmaker.model2 = model2Mock
    tools_matchmaker.similarity.model1Score = []
    tools_matchmaker.similarity.model2Score = []
    tools_matchmaker.similarity.ensembleScore = []
    tools_matchmaker.resumeTool = " "
    tools_matchmaker.jobTool = " "
    score = tools_matchmaker.getSimilarityScore()
    assert score == 0.0

def test_reset_success(tools_matchmaker):
    tools_matchmaker.similarity.model1Score = 0.8
    tools_matchmaker.similarity.model2Score = 0.6
    tools_matchmaker.similarity.ensembleScore = 0.7
    tools_matchmaker.model1 = MagicMock()
    tools_matchmaker.model2 = MagicMock()
    tools_matchmaker.reset()
    assert tools_matchmaker.similarity.model1Score is None
    assert tools_matchmaker.similarity.model2Score is None
    assert tools_matchmaker.similarity.ensembleScore is not None
    assert isinstance(tools_matchmaker.similarity.ensembleScore, list)
    assert tools_matchmaker.resumeTool is None
    assert tools_matchmaker.jobTool is None