# EXAMPLE USAGE
# if __name__ == "__main__":
#     resumeCertification = "AWS Certified Solutions Architect, Microsoft Certified Azure Administrator, Certified Kubernetes Administrator"
#     jobCertification = "AWS Solutions Architect Associate, Azure Administrator Associate Certification, Kubernetes Certification"
    
#     certificationMatcher = CertificationMatching()
#     certificationMatcher.setInputs(resumeCertification, jobCertification)
#     score = certificationMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     certificationMatcher.reset()

#     print("------------------------------")

#     resumeCertification = "Google Analytics Certification, Adobe Certified Expert Photoshop, Meta Digital Marketing Associate"
#     jobCertification = "AWS Certified DevOps Engineer, Certified Kubernetes Administrator, Microsoft Azure Data Scientist"
    
#     certificationMatcher = CertificationMatching()
#     certificationMatcher.setInputs(resumeCertification, jobCertification)
#     score = certificationMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     certificationMatcher.reset()
   

import gc
import numpy as np
from src.certification_matchmaker import config
from src.utils import security
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.model_load import model1, model2

config = config.Config()

class CertificationSimilarity:
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
        # for i in range(len(self.model1Score)):
        #     if self.model1Score[i] < 0.5:
        #         self.model1Score[i] = min(1.0, self.model1Score[i] * 0.7)
        #     if self.model2Score[i] < 0.5:
        #         self.model2Score[i] = min(1.0, self.model2Score[i] * 0.7)
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

class CertificationMatching:
    def __init__(self, maxInputLength=None):
        self.maxInputLength = maxInputLength
        self.model1 = model1
        self.model2 = model2
        self.resumeCertification = None
        self.jobCertification = None
        self.similarity = CertificationSimilarity()
    
    def setInputs(self, resumeCertification, jobCertification):
        if resumeCertification is None or jobCertification is None:
            raise ValueError("Resume certification and job certification cannot be empty.")
        if not isinstance(resumeCertification,str):
            raise ValueError("Resume certification must be a string.")
        if not isinstance(jobCertification, str):
            raise ValueError("Job certification must be a string.")
        self.resumeCertification = security.sanitizeInput(resumeCertification, self.maxInputLength).split(',')
        self.jobCertification = security.sanitizeInput(jobCertification, self.maxInputLength).split(',')
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            raise RuntimeError(f"Failed to load models")
        if not self.resumeCertification or not self.jobCertification:
            raise ValueError("Inputs are not set")
        
        try:
            model1Scores = []
            model2Scores = []
            matchedCertifications = {}
            ResumeEmbeddings1 = []
            ResumeEmbeddings2 = []
            for resumeCertification in self.resumeCertification:
                resumeCertification = resumeCertification.strip()
                resumeEmbeddings1 = self.model1.encode([resumeCertification])
                resumeEmbeddings2 = self.model2.encode([resumeCertification])
                ResumeEmbeddings1.append(resumeEmbeddings1)
                ResumeEmbeddings2.append(resumeEmbeddings2)
            for jobCertification in self.jobCertification:
                maxModel1Score = 0
                maxModel2Score = 1
                jobCertification = jobCertification.strip()
                jobEmbeddings1 = self.model1.encode([jobCertification])
                jobEmbeddings2 = self.model2.encode([jobCertification])
                currBest = None
                for i, resumeCertification in enumerate(self.resumeCertification):
                    if resumeCertification in matchedCertifications:
                        continue
                    if not jobCertification or not resumeCertification:
                        continue
                    resumeEmbeddings1 = ResumeEmbeddings1[i]
                    resumeEmbeddings2 = ResumeEmbeddings2[i]
                    similarity1 = max(float(cosine_similarity(jobEmbeddings1, resumeEmbeddings1)[0][0]), 0)
                    similarity2 = max(float(cosine_similarity(jobEmbeddings2, resumeEmbeddings2)[0][0]), 0)
                    if similarity1>maxModel1Score:
                        maxModel1Score = similarity1
                        maxModel2Score = similarity2
                        currBest = resumeCertification
                model1Scores.append(maxModel1Score)
                model2Scores.append(maxModel2Score)
                if currBest:
                    matchedCertifications[currBest] = jobCertification
            
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
        gc.collect()
        self.resumeCertification = None
        self.jobCertification = None
