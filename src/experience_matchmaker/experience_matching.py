# EXAMPLE USAGE
# if __name__ == "__main__":
#     resumeExperience = "Worked for 6.5+ yrs as a cloud engineer"
#     jobExperience = "2.6 years of mandatory project management experience"
    
#     ExperienceMatcher = ExperienceMatching()
#     ExperienceMatcher.setInputs(resumeExperience, jobExperience)
#     score = ExperienceMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     ExperienceMatcher.reset()

#     print("------------------------------")

#     resumeExperience = "Internship for 5.9 years in product management"
#     jobExperience = "Minimum 15.9 years of relevant experience required"
    
#     ExperienceMatcher = ExperienceMatching()
#     ExperienceMatcher.setInputs(resumeExperience, jobExperience)
#     score = ExperienceMatcher.makeMatch()
#     print(f"Similarity Score: {score}")
    
#     # Reset the matcher
#     ExperienceMatcher.reset()



import gc
import numpy as np
from src.experience_matchmaker import config
from src.utils import security
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import regex as re

config = config.Config()

class ExperienceSimilarity:
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
        if self.model1Score>0.5:
            self.ensembleScore = min(1.0, self.model1Score * 1.2)
        elif self.model2Score<0.5:
            self.ensembleScore = min(1.0, self.model2Score * 0.8)
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


class ExperienceNumeralizer:
    def __init__(self, mode=None): # Min/Max/Avg/Sum mode
        if not mode:
            raise ValueError("Mode cannot be None.")
         # Regex for normal single numbers like 1, 2, 3+
        self.pattern_single = re.compile(r"(\d+(?:\.\d+)?)(\+)?\s*(years|yrs|year)?", re.IGNORECASE)
        # Regex for ranges like "0-1 years"
        self.pattern_range = re.compile(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(years|yrs|year)?", re.IGNORECASE)

        self.years = []
        self.mode = mode
    
    def extractYears(self, text):
        matches_range = self.pattern_range.findall(text)
        if matches_range:
            for match in matches_range:
                low = float(match[0])
                high = float(match[1])
                avg = (low + high) / 2
                self.years.append(avg)
        
        matches_single = self.pattern_single.findall(text)
        for match in matches_single:
            num_str = match[0]
            plus_sign = match[1]
            try:
                value = float(num_str)
                if plus_sign:
                    value += 0.5  # "3+" becomes "3.5"
                self.years.append(value)
            except ValueError:
                raise ValueError(f"Invalid number format: {num_str}")
        if not self.years:
            self.years.append(0)
        
        if self.mode == "max":
            return max(self.years)
        elif self.mode == "avg":
            return np.mean(self.years)
        elif self.mode == "min":
            return min(self.years)
        elif self.mode == "sum":
            return sum(self.years)
        else:
            raise ValueError("Invalid mode. Use 'min' / 'max' / 'avg' / 'sum.")
    
    def getYears(self):
        if not self.years:
            raise ValueError("No years extracted.")
        return self.years
    
    def reset(self):
        self.years = []
        self.mode = None


class ExperienceMatching:
    def __init__(self, modelName1=None, modelName2=None):
        if modelName1 is None:
            modelName1 = config.MODEL_NAME_1
        if modelName2 is None:
            modelName2 = config.MODEL_NAME_2
        self.modelName1 = modelName1
        self.modelName2 = modelName2
        self.model1 = None
        self.model2 = None
        self.resumeExperience = None
        self.jobExperience = None
        self.similarity = ExperienceSimilarity()
        self.resumeNumeralizer = ExperienceNumeralizer(mode="sum")
        self.jobNumeralizer = ExperienceNumeralizer(mode="avg")
        self.factor = 1
    
    def loadModels(self):
        if not self.modelName1 or not self.modelName2:
            raise ValueError("Model names cannot be empty.")
        try:
            self.model1 = SentenceTransformer(self.modelName1)
            self.model2 = SentenceTransformer(self.modelName2)
        except Exception as e:
            raise RuntimeError(f"Failed to load models '{self.modelName1}' and '{self.modelName2}': {e}")
    
    def setInputs(self, resumeExperience, jobExperience):
        if not resumeExperience or not jobExperience:
            raise ValueError("Resume Experience and job Experience cannot be empty.")
        if not isinstance(resumeExperience, str):
            raise ValueError("Resume Experience must be a string.")
        if not isinstance(jobExperience, str):
            raise ValueError("Job Experience must be a string.")
        self.resumeExperience = resumeExperience
        self.jobExperience = jobExperience
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            try:
                self.loadModels()
            except Exception as e:
                raise RuntimeError(f"Failed to load models: {e}")
        if not self.resumeExperience or not self.jobExperience:
            raise ValueError("Inputs are not set")
        
        try:
            jobExperience = security.sanitizeInput(self.jobExperience, config.MAX_INPUT_LENGTH)
            resumeExperience = security.sanitizeInput(self.resumeExperience, config.MAX_INPUT_LENGTH)

            resumeNumeral = self.resumeNumeralizer.extractYears(resumeExperience)
            jobNumeral = self.jobNumeralizer.extractYears(jobExperience)
            if resumeNumeral and jobNumeral:
                self.factor = resumeNumeral / jobNumeral

            jobEmbeddings1 = self.model1.encode([jobExperience])
            resumeEmbeddings1 = self.model1.encode([resumeExperience])
            jobEmbeddings2 = self.model2.encode([jobExperience])
            resumeEmbeddings2 = self.model2.encode([resumeExperience])
            similarity1 = max(float(cosine_similarity(jobEmbeddings1, resumeEmbeddings1)[0][0]), 0)
            similarity2 = max(float(cosine_similarity(jobEmbeddings2, resumeEmbeddings2)[0][0]), 0)
            self.similarity.setModel1Score(similarity1)
            self.similarity.setModel2Score(similarity2)
            self.similarity.hardEnsemble()
            self.similarity.ensembleScore = min(self.similarity.ensembleScore * self.factor, 1.0)

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
        self.resumeExperience = None
        self.jobExperience = None
