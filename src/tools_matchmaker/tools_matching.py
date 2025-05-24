# EXAMPLE USAGE
# if __name__ == "__main__":
#     resumeTool = "Docker, Kubernetes, Git, Jenkins, Jira, MongoDB, AWS, Postman"
#     jobTool = "Docker, Kubernetes, GitHub, Jenkins, Jira, MySQL, AWS, Postman"
    
#     toolMatcher = ToolMatching()
#     toolMatcher.setInputs(resumeTool, jobTool)
#     score = toolMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     toolMatcher.reset()

#     print("------------------------------")

#     resumeTool = "Photoshop, Illustrator, Figma, Adobe XD, Canva, Kubernetes, Git, Jenkins"
#     jobTool = "AWS, Azure, Docker, Kubernetes, Jenkins, MongoDB, GitLab"
    
#     toolMatcher = ToolMatching()
#     toolMatcher.setInputs(resumeTool, jobTool)
#     score = toolMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     toolMatcher.reset()
   

import gc
import numpy as np
from src.tools_matchmaker import config
from src.utils import security
from sklearn.metrics.pairwise import cosine_similarity
from src.utils.model_load import model1, model2

config = config.Config()

class ToolSimilarity:
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

class ToolMatching:
    def __init__(self, maxInputLength=None):
        self.maxInputLength = maxInputLength
        self.model1 = model1
        self.model2 = model2
        self.resumeTool = None
        self.jobTool = None
        self.similarity = ToolSimilarity()
    
    def setInputs(self, resumeTool, jobTool):
        if resumeTool is None or jobTool is None:
            raise ValueError("Resume tools and job tools cannot be empty.")
        if not isinstance(resumeTool,str):
            raise ValueError("Resume tools must be a string.")
        if not isinstance(jobTool, str):
            raise ValueError("Job tools must be a string.")
        self.resumeTool = security.sanitizeInput(resumeTool, self.maxInputLength).split(',')
        self.jobTool = security.sanitizeInput(jobTool, self.maxInputLength).split(',')
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            raise RuntimeError(f"Failed to load models")
        if not self.resumeTool or not self.jobTool:
            raise ValueError("Inputs are not set")
        
        try:
            model1Scores = []
            model2Scores = []
            matchedTools = {}
            ResumeEmbeddings1 = []
            ResumeEmbeddings2 = []
            for resumeTool in self.resumeTool:
                resumeTool = resumeTool.strip()
                resumeEmbeddings1 = self.model1.encode([resumeTool])
                resumeEmbeddings2 = self.model2.encode([resumeTool])
                ResumeEmbeddings1.append(resumeEmbeddings1)
                ResumeEmbeddings2.append(resumeEmbeddings2)
            for jobTool in self.jobTool:
                maxModel1Score = 0
                maxModel2Score = 1
                jobTool = jobTool.strip()
                jobEmbeddings1 = self.model1.encode([jobTool])
                jobEmbeddings2 = self.model2.encode([jobTool])  
                currBest = None
                for i, resumeTool in enumerate(self.resumeTool):
                    if resumeTool in matchedTools:
                        continue
                    resumeTool = resumeTool.strip()
                    if not jobTool or not resumeTool:
                        continue
                    resumeEmbeddings1 = ResumeEmbeddings1[i]
                    resumeEmbeddings2 = ResumeEmbeddings2[i]
                    similarity1 = max(float(cosine_similarity(jobEmbeddings1, resumeEmbeddings1)[0][0]), 0)
                    similarity2 = max(float(cosine_similarity(jobEmbeddings2, resumeEmbeddings2)[0][0]), 0)
                    if similarity1>maxModel1Score:
                        maxModel1Score = similarity1
                        maxModel2Score = similarity2
                        currBest = resumeTool
                model1Scores.append(maxModel1Score)
                model2Scores.append(maxModel2Score)
                if currBest:
                    matchedTools[currBest] = jobTool
            
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
        self.resumeTool = None
        self.jobTool = None