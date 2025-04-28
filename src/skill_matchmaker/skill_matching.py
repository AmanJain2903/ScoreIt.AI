# BASE CLASS FOR TECHNICAL SKILL MATCHING & SOFT SKILL MATCHING


import gc
import numpy as np
from src.skill_matchmaker import config
from src.utils import security
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

config = config.Config()

class SkillSimilarity:
    def __init__(self):
        self.model1Score = None
        self.model2Score = None
        self.ensembleScore = []
    
    def setModel1Score(self, score):
        if not isinstance(score, (int, list)):
            raise ValueError("Score must be a list.")
        self.model1Score = score
    
    def setModel2Score(self, score):
        if not isinstance(score, (int, list)):
            raise ValueError("Score must be a list.")
        self.model2Score = score
    
    def averageEnsemble(self):
        if self.model1Score is None or self.model2Score is None:
            raise ValueError("Model scores are not set.")
        for i in range(len(self.model1Score)):
            if self.model1Score[i] and self.model2Score[i]:
                self.ensembleScore.append((self.model1Score[i] + self.model2Score[i]) / 2)

    def hardEnsemble(self):
        if self.model1Score is None or self.model2Score is None:
            raise ValueError("Model scores are not set.")
        for i in range(len(self.model1Score)):
            if self.model1Score[i] > 0.7:
                self.model1Score[i] = min(1.0, self.model1Score[i] * 1.2)
            if self.model2Score[i] < 0.3:
                self.model2Score[i] = self.model2Score[i] * 0.8
        self.averageEnsemble()
    
    def getEnsembleScore(self):
        if not self.ensembleScore:
            try:
                self.hardEnsemble()
            except ValueError:
                raise ValueError("Ensemble score has not been calculated.")
        if not isinstance(self.ensembleScore, list):
            raise ValueError("Ensemble score is not a valid list.")
        return self.ensembleScore

    def reset(self):
        """Reset the scores."""
        self.model1Score = None
        self.model2Score = None
        self.ensembleScore = []

class SkillMatching:
    def __init__(self, modelName1=None, modelName2=None, maxInputLength=None):
        self.modelName1 = modelName1
        self.modelName2 = modelName2
        self.maxInputLength = maxInputLength
        self.model1 = None
        self.model2 = None
        self.resumeSkill = None
        self.jobSkill = None
        self.similarity = SkillSimilarity()
    
    def loadModels(self):
        if not self.modelName1 or not self.modelName2:
            raise ValueError("Model names cannot be empty.")
        try:
            self.model1 = SentenceTransformer(self.modelName1)
            self.model2 = SentenceTransformer(self.modelName2)
        except Exception as e:
            raise RuntimeError(f"Failed to load models '{self.modelName1}' and '{self.modelName2}': {e}")
    
    def setInputs(self, resumeSkill, jobSkill):
        if not resumeSkill or not jobSkill:
            raise ValueError("Resume skill and job skill cannot be empty.")
        if not isinstance(resumeSkill,str):
            raise ValueError("Resume skill must be a string.")
        if not isinstance(jobSkill, str):
            raise ValueError("Job skill must be a string.")
        self.resumeSkill = security.sanitizeInput(resumeSkill, self.maxInputLength).split(',')
        self.jobSkill = security.sanitizeInput(jobSkill, self.maxInputLength).split(',')
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            try:
                self.loadModels()
            except Exception as e:
                raise RuntimeError(f"Failed to load models: {e}")
        if not self.resumeSkill or not self.jobSkill:
            raise ValueError("Inputs are not set")
        
        try:
            model1Scores = []
            model2Scores = []
            for jobSkill in self.jobSkill:
                maxModel1Score = 0
                maxModel2Score = 1
                jobSkill = jobSkill.strip()
                jobEmbeddings1 = self.model1.encode([jobSkill])
                jobEmbeddings2 = self.model2.encode([jobSkill])
                for resumeSkill in self.resumeSkill:
                    resumeSkill = resumeSkill.strip()
                    if not jobSkill or not resumeSkill:
                        continue
                    resumeEmbeddings1 = self.model1.encode([resumeSkill])
                    resumeEmbeddings2 = self.model2.encode([resumeSkill])
                    similarity1 = max(float(cosine_similarity(jobEmbeddings1, resumeEmbeddings1)[0][0]), 0)
                    similarity2 = max(float(cosine_similarity(jobEmbeddings2, resumeEmbeddings2)[0][0]), 0)
                    maxModel1Score = max(maxModel1Score, similarity1)
                    maxModel2Score = max(maxModel2Score, similarity2)
                model1Scores.append(maxModel1Score)
                model2Scores.append(maxModel2Score)
            
            self.similarity.setModel1Score(model1Scores)
            self.similarity.setModel2Score(model2Scores)
            self.similarity.hardEnsemble()

        except Exception as e:
            raise RuntimeError(f"Failed to make match: {e}")
        scores = self.similarity.getEnsembleScore()
        if not scores:
            return 0.0
        return np.mean(scores)
    
    def getSimilarityScore(self):
        if self.similarity.ensembleScore == []:
            try:
                self.makeMatch()
            except Exception as e:
                raise RuntimeError(f"Failed to get similarity score: {e}")
        if not isinstance(self.similarity.ensembleScore, list):
            raise ValueError("Ensemble score is not a valid list.")
        scores = self.similarity.getEnsembleScore()
        if not scores:
            return 0.0
        return np.mean(scores)
    
    def reset(self):
        """Reset the similarity scores and models."""
        self.similarity.reset()
        if self.model1:
            del self.model1
            self.model1 = None
        if self.model2:
            del self.model2
            self.model2 = None
        gc.collect()
        self.resumeSkill = None
        self.jobSkill = None