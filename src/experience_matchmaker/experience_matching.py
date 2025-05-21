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
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.model_load import model1, model2
import regex as re

config = config.Config()

class ExperienceSimilarity:
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
    def __init__(self):
        self.model1 = model1
        self.model2 = model2
        self.resumeExperience = None
        self.jobExperience = None
        self.similarity = ExperienceSimilarity()
        self.resumeNumeralizer = ExperienceNumeralizer(mode="sum")
        self.jobNumeralizer = ExperienceNumeralizer(mode="avg")
        self.factor = 1

    
    def setInputs(self, resumeExperience, jobExperience):
        if not resumeExperience or not jobExperience:
            raise ValueError("Resume Experience and job Experience cannot be empty.")
        if not isinstance(resumeExperience, str):
            raise ValueError("Resume Experience must be a string.")
        if not isinstance(jobExperience, str):
            raise ValueError("Job Experience must be a string.")
        self.resumeExperience = security.sanitizeInput(resumeExperience, config.MAX_INPUT_LENGTH).split(',')
        self.jobExperience = security.sanitizeInput(jobExperience, config.MAX_INPUT_LENGTH).split(',')
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            raise RuntimeError(f"Failed to load models")
        if not self.resumeExperience or not self.jobExperience:
            raise ValueError("Inputs are not set")
        
        try:
            model1Scores = []
            model2Scores = []
            matchedExperiences = {}
            ResumeEmbeddings1 = []
            ResumeEmbeddings2 = []
            ResumeNumerals = []
            for resumeExperience in self.resumeExperience:
                resumeExperience = resumeExperience.strip()
                resumeEmbeddings1 = self.model1.encode([resumeExperience])
                resumeEmbeddings2 = self.model2.encode([resumeExperience])
                resumeNumeral = self.resumeNumeralizer.extractYears(resumeExperience)
                ResumeEmbeddings1.append(resumeEmbeddings1)
                ResumeEmbeddings2.append(resumeEmbeddings2)
                ResumeNumerals.append(resumeNumeral)
            for jobExperience in self.jobExperience:
                maxModel1Score = 0
                maxModel2Score = 1
                jobExperience = jobExperience.strip()
                jobNumeral = self.jobNumeralizer.extractYears(jobExperience)
                jobEmbeddings1 = self.model1.encode([jobExperience])
                jobEmbeddings2 = self.model2.encode([jobExperience])
                currBest = None
                for i, resumeExperience in enumerate(self.resumeExperience):
                    if resumeExperience in matchedExperiences:
                        continue
                    resumeNumeral = ResumeNumerals[i]
                    if resumeNumeral and jobNumeral:
                        self.factor = resumeNumeral / jobNumeral
                    if not jobExperience or not resumeExperience:
                        continue
                    resumeEmbeddings1 = ResumeEmbeddings1[i]
                    resumeEmbeddings2 = ResumeEmbeddings2[i]
                    similarity1 = min(1.0, max(float(cosine_similarity(jobEmbeddings1, resumeEmbeddings1)[0][0]), 0) * self.factor)
                    similarity2 = min(1.0, max(float(cosine_similarity(jobEmbeddings2, resumeEmbeddings2)[0][0]), 0) * self.factor)
                    if similarity1>maxModel1Score:
                        maxModel1Score = similarity1
                        maxModel2Score = similarity2
                        currBest = resumeExperience
                model1Scores.append(maxModel1Score)
                model2Scores.append(maxModel2Score)
                if currBest:
                    matchedExperiences[currBest] = jobExperience
            
            self.similarity.setModel1Score(model1Scores)
            self.similarity.setModel2Score(model2Scores)
            self.similarity.hardEnsemble()

        except Exception as e:
            raise RuntimeError(f"Failed to make match: {e}")
        scores = self.similarity.getEnsembleScore()
        if not scores:
            return 0.0
        return min(1.0,max(scores))
    
    def getSimilarityScore(self):
        if self.similarity.ensembleScore is None:
            try:
                self.makeMatch()
            except Exception as e:
                raise RuntimeError(f"Failed to get similarity score: {e}")
        if not isinstance(self.similarity.ensembleScore, (int, list)):
            raise ValueError("Ensemble score is not a valid list.")
        scores = self.similarity.getEnsembleScore()
        if not scores:
            return 0.0
        return min(1.0, max(scores))
    
    def reset(self):
        """Reset the similarity scores and models."""
        self.similarity.reset()
        gc.collect()
        self.resumeExperience = None
        self.jobExperience = None
