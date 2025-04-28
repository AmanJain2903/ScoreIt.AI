# EXAMPLE USAGE
# if __name__ == "__main__":
#     resumeEducation = "Bachelor of Science in Computer Science, Master of Science in Data Science"
#     jobEducation = "Master's degree in Computer Science or related field"
    
#     educationMatcher = EducationMatching()
#     educationMatcher.setInputs(resumeEducation, jobEducation)
#     score = educationMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     educationMatcher.reset()

#     print("------------------------------")

#     resumeEducation = "Bachelor of Technology in Civil Engineering, Master of Technology in Structural Engineering"
#     jobEducation = "Master's degree in Computer Science or related field"
    
#     educationMatcher = EducationMatching()
#     educationMatcher.setInputs(resumeEducation, jobEducation)
#     score = educationMatcher.makeMatch()
#     print(f"Similarity Score: {score}")
    
#     # Reset the matcher
#     educationMatcher.reset()


import gc
import numpy as np
from src.education_matchmaker import config
from src.utils import security
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

config = config.Config()

class EducationSimilarity:
    def __init__(self):
        self.model1Score = None
        self.model2Score = None
        self.ensembleScore = None
    
    def setModel1Score(self, score):
        if not isinstance(score, (int, float)):
            raise ValueError("Score must be an integer or float.")
        self.model1Score = score
    
    def setModel2Score(self, score):
        if not isinstance(score, (int, float)):
            raise ValueError("Score must be an integer or float.")
        self.model2Score = score
    
    def averageEnsemble(self):
        if self.model1Score is None or self.model2Score is None:
            raise ValueError("Model scores are not set.")
        self.ensembleScore = (self.model1Score + self.model2Score) / 2
    
    def hardEnsemble(self):
        if self.model1Score is None or self.model2Score is None:
            raise ValueError("Model scores are not set.")
        if self.model2Score<0.6:
            self.ensembleScore = self.model2Score * 0.6
        elif self.model1Score>0.8:
            self.ensembleScore = min(1.0, self.model1Score * 1.2)
        else:
            self.averageEnsemble()
    
    def getEnsembleScore(self):
        if self.ensembleScore is None:
            try:
                self.hardEnsemble()
            except ValueError:
                raise ValueError("Ensemble score has not been calculated.")
        if not isinstance(self.ensembleScore, (int, float)):
            raise ValueError("Ensemble score is not a valid number.")
        return self.ensembleScore

    def reset(self):
        """Reset the scores."""
        self.model1Score = None
        self.model2Score = None
        self.ensembleScore = None

class EducationMatching:
    def __init__(self, modelName1=None, modelName2=None):
        if modelName1 is None:
            modelName1 = config.MODEL_NAME_1
        if modelName2 is None:
            modelName2 = config.MODEL_NAME_2
        self.modelName1 = modelName1
        self.modelName2 = modelName2
        self.model1 = None
        self.model2 = None
        self.resumeEducation = None
        self.jobEducation = None
        self.similarity = EducationSimilarity()
    
    def loadModels(self):
        if not self.modelName1 or not self.modelName2:
            raise ValueError("Model names cannot be empty.")
        try:
            self.model1 = SentenceTransformer(self.modelName1)
            self.model2 = SentenceTransformer(self.modelName2)
        except Exception as e:
            raise RuntimeError(f"Failed to load models '{self.modelName1}' and '{self.modelName2}': {e}")
    
    def setInputs(self, resumeEducation, jobEducation):
        if not resumeEducation or not jobEducation:
            raise ValueError("Resume education and job education cannot be empty.")
        if not isinstance(resumeEducation, str):
            raise ValueError("Resume education must be a string.")
        if not isinstance(jobEducation, str):
            raise ValueError("Job education must be a string.")
        self.resumeEducation = resumeEducation
        self.jobEducation = jobEducation
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            try:
                self.loadModels()
            except Exception as e:
                raise RuntimeError(f"Failed to load models: {e}")
        if not self.resumeEducation or not self.jobEducation:
            raise ValueError("Inputs are not set")
        
        try:
            jobEducation = security.sanitizeInput(self.jobEducation, config.MAX_INPUT_LENGTH)
            resumeEducation = security.sanitizeInput(self.resumeEducation, config.MAX_INPUT_LENGTH)
            jobEmbeddings1 = self.model1.encode([jobEducation])
            resumeEmbeddings1 = self.model1.encode([resumeEducation])
            jobEmbeddings2 = self.model2.encode([jobEducation])
            resumeEmbeddings2 = self.model2.encode([resumeEducation])
            similarity1 = max(float(cosine_similarity(jobEmbeddings1, resumeEmbeddings1)[0][0]), 0)
            similarity2 = max(float(cosine_similarity(jobEmbeddings2, resumeEmbeddings2)[0][0]), 0)
            self.similarity.setModel1Score(similarity1)
            self.similarity.setModel2Score(similarity2)
            self.similarity.hardEnsemble()

        except Exception as e:
            raise RuntimeError(f"Failed to make match: {e}")
        return self.similarity.getEnsembleScore()
    
    def getSimilarityScore(self):
        if self.similarity.ensembleScore is None:
            try:
                self.makeMatch()
            except Exception as e:
                raise RuntimeError(f"Failed to get similarity score: {e}")
        if not isinstance(self.similarity.ensembleScore, (int, float)):
            raise ValueError("Ensemble score is not a valid number.")
        return self.similarity.getEnsembleScore()
    
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
        self.resumeEducation = None
        self.jobEducation = None
    