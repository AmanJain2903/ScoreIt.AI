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
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

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

class ToolMatching:
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
        self.resumeTool = None
        self.jobTool = None
        self.similarity = ToolSimilarity()
    
    def loadModels(self):
        if not self.modelName1 or not self.modelName2:
            raise ValueError("Model names cannot be empty.")
        try:
            self.model1 = SentenceTransformer(self.modelName1)
            self.model2 = SentenceTransformer(self.modelName2)
        except Exception as e:
            raise RuntimeError(f"Failed to load models '{self.modelName1}' and '{self.modelName2}': {e}")
    
    def setInputs(self, resumeTool, jobTool):
        if not resumeTool or not jobTool:
            raise ValueError("Resume tools and job tools cannot be empty.")
        if not isinstance(resumeTool,str):
            raise ValueError("Resume tools must be a string.")
        if not isinstance(jobTool, str):
            raise ValueError("Job tools must be a string.")
        self.resumeTool = security.sanitizeInput(resumeTool, self.maxInputLength).split(',')
        self.jobTool = security.sanitizeInput(jobTool, self.maxInputLength).split(',')
    
    def makeMatch(self):
        if not self.model1 or not self.model2:
            try:
                self.loadModels()
            except Exception as e:
                raise RuntimeError(f"Failed to load models: {e}")
        if not self.resumeTool or not self.jobTool:
            raise ValueError("Inputs are not set")
        
        try:
            model1Scores = []
            model2Scores = []
            matchedTools = {}
            for jobTool in self.jobTool:
                maxModel1Score = 0
                maxModel2Score = 1
                jobTool = jobTool.strip()
                jobEmbeddings1 = self.model1.encode([jobTool])
                jobEmbeddings2 = self.model2.encode([jobTool])
                currBest = None
                for resumeTool in self.resumeTool:
                    if resumeTool in matchedTools:
                        continue
                    resumeTool = resumeTool.strip()
                    if not jobTool or not resumeTool:
                        continue
                    resumeEmbeddings1 = self.model1.encode([resumeTool])
                    resumeEmbeddings2 = self.model2.encode([resumeTool])
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
        self.resumeTool = None
        self.jobTool = None