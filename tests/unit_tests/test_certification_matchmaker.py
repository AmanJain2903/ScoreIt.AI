import pytest
from unittest.mock import patch, MagicMock
from src.certification_matchmaker.certification_matching import CertificationMatching, CertificationSimilarity
import numpy as np

pytestmark = pytest.mark.unit

@pytest.fixture
def certification_matchmaker():
    return CertificationMatching(maxInputLength=10000)

@pytest.fixture
def certification_similarity():
    return CertificationSimilarity()

def test_ts_initialization(certification_similarity):
    assert certification_similarity.model1Score is None
    assert certification_similarity.model2Score is None
    assert certification_similarity.ensembleScore is not None
    assert isinstance(certification_similarity.ensembleScore, list)

def test_ts_set_model1_score(certification_similarity):
    certification_similarity.setModel1Score([0.8])
    assert certification_similarity.model1Score == [0.8]
    with pytest.raises(ValueError, match="Score must be a list."):
        certification_similarity.setModel1Score('1')

def test_ts_set_model2_score(certification_similarity):
    certification_similarity.setModel2Score([0.9])
    assert certification_similarity.model2Score == [0.9]
    with pytest.raises(ValueError, match="Score must be a list."):
        certification_similarity.setModel2Score('1')

def test_ts_average_ensemble(certification_similarity):
    certification_similarity.setModel1Score([0.8])
    certification_similarity.setModel2Score([0.6])
    certification_similarity.averageEnsemble()
    assert isinstance(certification_similarity.ensembleScore, list)
    assert len(certification_similarity.ensembleScore) == 1
    certification_similarity.model1Score = None
    certification_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        certification_similarity.averageEnsemble()

def test_ts_hard_ensemble(certification_similarity):
    certification_similarity.setModel1Score([0.9])
    certification_similarity.setModel2Score([0.5])
    certification_similarity.hardEnsemble()
    assert isinstance(certification_similarity.ensembleScore, list)
    assert len(certification_similarity.ensembleScore) == 1
    certification_similarity.reset()
    certification_similarity.setModel1Score([0.7])
    certification_similarity.setModel2Score([0.8])
    certification_similarity.hardEnsemble()
    assert isinstance(certification_similarity.ensembleScore, list)
    assert len(certification_similarity.ensembleScore) == 1
    certification_similarity.reset()
    certification_similarity.setModel1Score([0.9])
    certification_similarity.setModel2Score([0.9])
    certification_similarity.hardEnsemble()
    assert isinstance(certification_similarity.ensembleScore, list)
    assert len(certification_similarity.ensembleScore) == 1
    certification_similarity.reset()
    certification_similarity.model1Score = None
    certification_similarity.model2Score = None
    with pytest.raises(ValueError, match="Model scores are not set."):
        certification_similarity.hardEnsemble()

def test_ts_get_ensemble_score(certification_similarity):
    certification_similarity.setModel1Score([0.7])
    certification_similarity.setModel2Score([0.8])
    certification_similarity.hardEnsemble()
    assert isinstance(certification_similarity.ensembleScore, list)
    assert len(certification_similarity.ensembleScore) == 1
    certification_similarity.model1Score = None
    certification_similarity.model2Score = None
    certification_similarity.ensembleScore = None
    with pytest.raises(ValueError, match="Ensemble score has not been calculated."):
        certification_similarity.getEnsembleScore()
    certification_similarity.ensembleScore = '1'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        certification_similarity.getEnsembleScore()

def test_ts_reset(certification_similarity):
    certification_similarity.setModel1Score([0.8])
    certification_similarity.setModel2Score([0.9])
    certification_similarity.ensembleScore = [0.85]
    certification_similarity.reset()
    assert certification_similarity.model1Score is None
    assert certification_similarity.model2Score is None
    assert certification_similarity.ensembleScore is not None
    assert isinstance(certification_similarity.ensembleScore, list)

def test_initialization(certification_matchmaker):
    assert certification_matchmaker.maxInputLength == 10000
    assert certification_matchmaker.model1 is not None
    assert certification_matchmaker.model2 is not None
    assert certification_matchmaker.resumeCertification is None
    assert certification_matchmaker.jobCertification is None
    assert certification_matchmaker.similarity is not None
    assert isinstance(certification_matchmaker.similarity, CertificationSimilarity)

def test_set_inputs_success(certification_matchmaker):
    resumeCertification = "AWS Certified Solutions Architect, Google Professional Data Engineer, Certified Kubernetes Administrator"
    jobCertification = "AWS Solutions Architect Associate, GCP Professional Data Engineer, Kubernetes Certificationn"
    certification_matchmaker.setInputs(resumeCertification, jobCertification)
    assert len(certification_matchmaker.resumeCertification) == 3
    assert len(certification_matchmaker.jobCertification) == 3
    assert isinstance(certification_matchmaker.resumeCertification, list)
    assert isinstance(certification_matchmaker.jobCertification, list)

def test_set_inputs_failure(certification_matchmaker):
    resumeCertification = None
    jobCertification = "AWS Certified Solutions Architect, Google Professional Data Engineer, Certified Kubernetes Administrator"
    with pytest.raises(ValueError, match="Resume certification and job certification cannot be empty."):
        certification_matchmaker.setInputs(resumeCertification, jobCertification)
    
    resumeCertification = "AWS Certified Solutions Architect, Google Professional Data Engineer, Certified Kubernetes Administrator"
    jobCertification = None
    with pytest.raises(ValueError, match="Resume certification and job certification cannot be empty."):
        certification_matchmaker.setInputs(resumeCertification, jobCertification)

def test_set_inputs_invalid(certification_matchmaker):
    resumeCertification = 12345
    jobCertification = "AWS Certified Solutions Architect, Google Professional Data Engineer, Certified Kubernetes Administrator"
    with pytest.raises(ValueError, match="Resume certification must be a string."):
        certification_matchmaker.setInputs(resumeCertification, jobCertification)
    
    resumeCertification = "AWS Certified Solutions Architect, Google Professional Data Engineer, Certified Kubernetes Administrator"
    jobCertification = 12345
    with pytest.raises(ValueError, match="Job certification must be a string."):
        certification_matchmaker.setInputs(resumeCertification, jobCertification)

def test_make_match_success(certification_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    certification_matchmaker.model1 = model1Mock
    certification_matchmaker.model2 = model2Mock
    certification_matchmaker.resumeCertification = ["AWS Certified Solutions Architect",
                                                        "Google Professional Data Engineer",
                                                        "Certified Kubernetes Administrator"]
    certification_matchmaker.jobCertification = ["AWS Certified Solutions Architect",
                                                        "Google Professional Data Engineer",
                                                        "Certified Kubernetes Administrator"]
    model1Mock.encode.return_value = [np.array([[0.1]])]
    model2Mock.encode.return_value = [np.array([[0.1]])]
    with patch('src.certification_matchmaker.certification_matching.cosine_similarity', return_value=np.array([[1.0]])):
            score = certification_matchmaker.makeMatch()
    assert score == 1.0


def test_make_match_no_models(certification_matchmaker):
    certification_matchmaker.model1 = None
    certification_matchmaker.model2 = None
    with pytest.raises(RuntimeError, match="Failed to load models"):
        certification_matchmaker.makeMatch()

def test_make_match_no_model_names(certification_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    certification_matchmaker.model1 = model1Mock
    certification_matchmaker.model2 = model2Mock
    with pytest.raises(ValueError, match="Inputs are not set"):
        certification_matchmaker.makeMatch()

def test_make_match_failure(certification_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    certification_matchmaker.model1 = model1Mock
    certification_matchmaker.model2 = model2Mock
    certification_matchmaker.resumeCertification = "AWS Certified Solutions Architect, Google Professional Data Engineer, Certified Kubernetes Administrator"
    certification_matchmaker.jobCertification = "AWS Solutions Architect Associate, GCP Professional Data Engineer, Kubernetes Certificationn"
    model1Mock.encode.side_effect = Exception("Encoding failed")
    with pytest.raises(RuntimeError, match="Failed to make match: Encoding failed"):
        certification_matchmaker.makeMatch()

def test_similarity_score_success(certification_matchmaker):
    certification_matchmaker.similarity.model1Score = [0.8, 0.9]
    certification_matchmaker.similarity.model2Score = [0.6, 0.7]
    certification_matchmaker.similarity.ensembleScore = [0.7, 0.8]
    score = certification_matchmaker.getSimilarityScore()
    assert score == 0.75

def test_similarity_score_no_ensemble(certification_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    certification_matchmaker.model1 = model1Mock
    certification_matchmaker.model2 = model2Mock
    certification_matchmaker.similarity.model1Score = []
    certification_matchmaker.similarity.model2Score = []
    certification_matchmaker.similarity.ensembleScore = []
    with patch.object(certification_matchmaker, 'makeMatch', side_effect=Exception("Failure")):
        with pytest.raises(RuntimeError, match="Failed to get similarity score: Failure"):
            certification_matchmaker.getSimilarityScore()

def test_similarity_score_invalid(certification_matchmaker):
    certification_matchmaker.similarity.model1Score = '1'
    certification_matchmaker.similarity.model2Score = '2'
    certification_matchmaker.similarity.ensembleScore = 'ensemble'
    with pytest.raises(ValueError, match="Ensemble score is not a valid list."):
        certification_matchmaker.getSimilarityScore()

def test_similarity_score_empty_list(certification_matchmaker):
    model1Mock = MagicMock()
    model2Mock = MagicMock()
    certification_matchmaker.model1 = model1Mock
    certification_matchmaker.model2 = model2Mock
    certification_matchmaker.similarity.model1Score = []
    certification_matchmaker.similarity.model2Score = []
    certification_matchmaker.similarity.ensembleScore = []
    certification_matchmaker.resumeCertification = " "
    certification_matchmaker.jobCertification = " "
    score = certification_matchmaker.getSimilarityScore()
    assert score == 0.0

def test_reset_success(certification_matchmaker):
    certification_matchmaker.similarity.model1Score = 0.8
    certification_matchmaker.similarity.model2Score = 0.6
    certification_matchmaker.similarity.ensembleScore = 0.7
    certification_matchmaker.model1 = MagicMock()
    certification_matchmaker.model2 = MagicMock()
    certification_matchmaker.reset()
    assert certification_matchmaker.similarity.model1Score is None
    assert certification_matchmaker.similarity.model2Score is None
    assert certification_matchmaker.similarity.ensembleScore is not None
    assert isinstance(certification_matchmaker.similarity.ensembleScore, list)
    assert certification_matchmaker.resumeCertification is None
    assert certification_matchmaker.jobCertification is None