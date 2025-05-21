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
from src.education_matchmaker import config
from src.utils import security
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.model_load import model1, model2

config = config.Config()

class EducationSimilarity:
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
            if self.model1Score[i] > self.model2Score[i] and self.model2Score[i] > 0.5:
                self.model1Score[i] = min(1.0, self.model1Score[i] * 1.2)
            elif self.model2Score[i] > self.model1Score[i] and self.model1Score[i] > 0.5:
                self.model2Score[i] = min(1.0, self.model2Score[i] * 1.2)
            else:
                self.model1Score[i] = min(1.0, self.model1Score[i] * 0.7)
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

class EducationMatching:
    def __init__(self):
        self.model1 = model1
        self.model2 = model2
        self.resumeEducation = None
        self.jobEducation = None
        self.similarity = EducationSimilarity()
    
    def setInputs(self, resumeEducation, jobEducation):
        if not resumeEducation or not jobEducation:
            raise ValueError("Resume education and job education cannot be empty.")
        if not isinstance(resumeEducation, str):
            raise ValueError("Resume education must be a string.")
        if not isinstance(jobEducation, str):
            raise ValueError("Job education must be a string.")
        self.resumeEducation = security.sanitizeInput(resumeEducation, config.MAX_INPUT_LENGTH).split(',')
        self.jobEducation = security.sanitizeInput(jobEducation, config.MAX_INPUT_LENGTH).split(',')
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            raise RuntimeError(f"Failed to load models")
        if not self.resumeEducation or not self.jobEducation:
            raise ValueError("Inputs are not set")
        
        try:
            model1Scores = []
            model2Scores = []
            matchedEducations = {}
            ResumeEmbeddings1 = []
            ResumeEmbeddings2 = []
            for resumeEducation in self.resumeEducation:
                resumeEducation = resumeEducation.strip()
                resumeEmbeddings1 = self.model1.encode([resumeEducation])
                resumeEmbeddings2 = self.model2.encode([resumeEducation])
                ResumeEmbeddings1.append(resumeEmbeddings1)
                ResumeEmbeddings2.append(resumeEmbeddings2)
            for jobEducation in self.jobEducation:
                maxModel1Score = 0.0
                maxModel2Score = 0.0
                jobEducation = jobEducation.strip()
                jobEmbeddings1 = self.model1.encode([jobEducation])
                jobEmbeddings2 = self.model2.encode([jobEducation])
                currBest = None
                for i, resumeEducation in enumerate(self.resumeEducation):
                    if resumeEducation in matchedEducations:
                        continue
                    resumeEducation = resumeEducation.strip()
                    if not jobEducation or not resumeEducation:
                        continue
                    resumeEmbeddings1 = ResumeEmbeddings1[i]
                    resumeEmbeddings2 = ResumeEmbeddings2[i]
                    similarity1 = max(float(cosine_similarity(jobEmbeddings1, resumeEmbeddings1)[0][0]), 0.0)
                    similarity2 = max(float(cosine_similarity(jobEmbeddings2, resumeEmbeddings2)[0][0]), 0.0)
                    if similarity1>maxModel1Score:
                        maxModel1Score = similarity1
                        maxModel2Score = similarity2
                        currBest = resumeEducation
                model1Scores.append(maxModel1Score)
                model2Scores.append(maxModel2Score)
                if currBest:
                    matchedEducations[currBest] = jobEducation
            
            self.similarity.setModel1Score(model1Scores)
            self.similarity.setModel2Score(model2Scores)
            self.similarity.hardEnsemble()

        except Exception as e:
            raise RuntimeError(f"Failed to make match: {e}")
        scores = self.similarity.getEnsembleScore()
        if not scores:
            return 0.0
        return min(1.0, max(scores))
    
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
        self.resumeEducation = None
        self.jobEducation = None
