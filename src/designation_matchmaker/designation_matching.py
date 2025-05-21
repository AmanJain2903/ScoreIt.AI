# EXAMPLE USAGE
# if __name__ == "__main__":
#     resumeDesignation = "Software Engineer, Backend Developer, Full Stack Developer"
#     jobDesignation = "Senior Software Engineer, Full Stack Engineer, Backend Developer"    
#     designationMatcher = DesignationMatching()
#     designationMatcher.setInputs(resumeDesignation, jobDesignation)
#     score = designationMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     designationMatcher.reset()

#     print("------------------------------")

#     resumeDesignation = "Teaching Assistant, Academic Researcher, Backend Intern"
#     jobDesignation = "Data Engineer, Cloud Architect, Senior Backend Developer"    
#     designationMatcher = DesignationMatching()
#     designationMatcher.setInputs(resumeDesignation, jobDesignation)
#     score = designationMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     designationMatcher.reset()
   

import gc
import numpy as np
from src.designation_matchmaker import config
from src.utils import security
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.model_load import model1, model2

config = config.Config()

class DesignationSimilarity:
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
            if self.model1Score[i] < 0.5:
                self.model1Score[i] = min(1.0, self.model1Score[i] * 0.7)
            if self.model2Score[i] < 0.5:
                self.model2Score[i] = min(1.0, self.model2Score[i] * 0.7)
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

class DesignationMatching:
    def __init__(self, modelName1=None, modelName2=None, maxInputLength=None):
        if modelName1 is None:
            modelName1 = config.MODEL_NAME_1
        if modelName2 is None:
            modelName2 = config.MODEL_NAME_2
        self.modelName1 = modelName1
        self.modelName2 = modelName2
        self.maxInputLength = maxInputLength
        self.model1 = None
        self.model2 = None
        self.resumeDesignation = None
        self.jobDesignation = None
        self.similarity = DesignationSimilarity()
    
    def loadModels(self):
        if not self.modelName1 or not self.modelName2:
            raise ValueError("Model names cannot be empty.")
        try:
            self.model1 = model1
            self.model2 = model2
        except Exception as e:
            raise RuntimeError(f"Failed to load models '{self.modelName1}' and '{self.modelName2}': {e}")
    
    def setInputs(self, resumeDesignation, jobDesignation):
        if not resumeDesignation or not jobDesignation:
            raise ValueError("Resume designation and job designation cannot be empty.")
        if not isinstance(resumeDesignation,str):
            raise ValueError("Resume designation must be a string.")
        if not isinstance(jobDesignation, str):
            raise ValueError("Job designation must be a string.")
        self.resumeDesignation = security.sanitizeInput(resumeDesignation, self.maxInputLength).split(',')
        self.jobDesignation = security.sanitizeInput(jobDesignation, self.maxInputLength).split(',')
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            try:
                self.loadModels()
            except Exception as e:
                raise RuntimeError(f"Failed to load models: {e}")
        if not self.resumeDesignation or not self.jobDesignation:
            raise ValueError("Inputs are not set")
        
        try:
            model1Scores = []
            model2Scores = []
            matchedDesignations = {}
            for jobDesignation in self.jobDesignation:
                maxModel1Score = 0
                maxModel2Score = 1
                jobDesignation = jobDesignation.strip()
                jobEmbeddings1 = self.model1.encode([jobDesignation])
                jobEmbeddings2 = self.model2.encode([jobDesignation])
                currBest = None
                for resumeDesignation in self.resumeDesignation:
                    if resumeDesignation in matchedDesignations:
                        continue
                    resumeDesignation = resumeDesignation.strip()
                    if not jobDesignation or not resumeDesignation:
                        continue
                    resumeEmbeddings1 = self.model1.encode([resumeDesignation])
                    resumeEmbeddings2 = self.model2.encode([resumeDesignation])
                    similarity1 = max(float(cosine_similarity(jobEmbeddings1, resumeEmbeddings1)[0][0]), 0)
                    similarity2 = max(float(cosine_similarity(jobEmbeddings2, resumeEmbeddings2)[0][0]), 0)
                    if similarity1>maxModel1Score:
                        maxModel1Score = similarity1
                        maxModel2Score = similarity2
                        currBest = resumeDesignation
                model1Scores.append(maxModel1Score)
                model2Scores.append(maxModel2Score)
                if currBest:
                    matchedDesignations[currBest] = jobDesignation
            
            self.similarity.setModel1Score(model1Scores)
            self.similarity.setModel2Score(model2Scores)
            self.similarity.hardEnsemble()

        except Exception as e:
            raise RuntimeError(f"Failed to make match: {e}")
        scores = self.similarity.getEnsembleScore()
        if not scores:
            return 0.0
        return min(1.0, np.mean(scores))
    
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
        return min(1.0, np.mean(scores))
    
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
        self.resumeDesignation = None
        self.jobDesignation = None