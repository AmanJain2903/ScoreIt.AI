import pandas as pd
import numpy as np
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from src.education_matchmaker.education_matching import EducationMatching
from src.experience_matchmaker.experience_matching import ExperienceMatching
from src.skill_matchmaker.technical_skill_matching import TechnicalSkillMatching
from src.skill_matchmaker.soft_skill_matching import SoftSkillMatching
from src.tools_matchmaker.tools_matching import ToolMatching
from src.certification_matchmaker.certification_matching import CertificationMatching
from src.designation_matchmaker.designation_matching import DesignationMatching
from src.resume_extractor_agent.resume_agent import ResumeAgent
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
from src.utils import security
from dotenv import load_dotenv
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

matchmakerFactor = 1 # 500 data points out of 500 total
agentFactor = 0.2 # 100 data points out of 500 total

# Mapping module names to their classes
matchmaker_configs = {
    "Education Matching": {"dataset_path": "data/education_dataset.csv", "matcher_class": EducationMatching},
    "Experience Matching": {"dataset_path": "data/experience_dataset.csv", "matcher_class": ExperienceMatching},
    "Technical Skills Matching": {"dataset_path": "data/technical_skills_dataset.csv", "matcher_class": TechnicalSkillMatching},
    "Soft Skills Matching": {"dataset_path": "data/soft_skills_dataset.csv", "matcher_class": SoftSkillMatching},
    "Tools Matching": {"dataset_path": "data/tools_dataset.csv", "matcher_class": ToolMatching},
    "Certification Matching": {"dataset_path": "data/certification_dataset.csv", "matcher_class": CertificationMatching},
    "Designation Matching": {"dataset_path": "data/designation_dataset.csv", "matcher_class": DesignationMatching}
}
matchmaker_dataset_columns = {
    "Education Matching": ["resume_edu", "jd_edu", "label"],
    "Experience Matching": ["resume_exp", "jd_exp", "label"],
    "Technical Skills Matching": ["resume_skills", "jd_skills", "label"],
    "Soft Skills Matching": ["resume_skills", "jd_skills", "label"],
    "Tools Matching": ["resume_tools", "jd_tools", "label"],
    "Certification Matching": ["resume_certs", "jd_certs", "label"],
    "Designation Matching": ["resume_title", "jd_title", "label"]
}
agent_configs = {
    "Resume Agent": {"dataset_path": "data/resume_dataset.csv", "matcher_class": ResumeAgent},
    "Job Description Agent": {"dataset_path": "data/job_description_dataset.csv", "matcher_class": JobDescriptionAgent}
}
agent_dataset_columns = {
    "Resume Agent": ["Resume", "EDUCATION", "EXPERIENCE", "TECHNICAL_SKILL", "SOFT_SKILL", "TOOL", "CERTIFICATION", "DESIGNATION"],
    "Job Description Agent": ["Description", "EDUCATION", "EXPERIENCE", "TECHNICAL_SKILL", "SOFT_SKILL", "TOOL", "CERTIFICATION", "DESIGNATION"],
}

class CustomAccuracy:
    def __init__(self):
        self.name = "Custom Accuracy"
        self.description = "Custom accuracy metric for evaluating model performance."
    def __call__(self, y_true, y_pred, tolerance=0.15):
        yTrue = np.array(y_true)
        yPred = np.array(y_pred)
        matches = np.abs(yTrue - yPred) <= tolerance
        return np.mean(matches) * 100

class Matchmakers:
    def __init__(self):
        self.results = {}
        self.metrics = {
            "MAE": mean_absolute_error,
            "MSE": mean_squared_error,
            "Accuracy" : CustomAccuracy()
        }
        self.module_configs = matchmaker_configs
        self.dataset_columns = matchmaker_dataset_columns
        self.factor = matchmakerFactor
    def runBenchmarks(self):
        for moduleName, config in self.module_configs.items():
            print(f"Running benchmarks for {moduleName}...")
            datasetPath = config["dataset_path"]
            matcherClass = config["matcher_class"]
            dataset = pd.read_csv(datasetPath)
            dataset = dataset.sample(frac=self.factor, random_state=1).reset_index(drop=True)
            datasetColumns = self.dataset_columns[moduleName]
            if dataset.empty:
                raise ValueError(f"Dataset for {moduleName} is empty. Please check the data path.")
            for col in datasetColumns:
                if col not in dataset.columns:
                    raise ValueError(f"Column '{col}' not found in the dataset for {moduleName}.")
            yTrue = []
            yPred = []
            matcher = matcherClass()
            support = 0
            for i in tqdm(range(len(dataset))):
                support += 1
                matcher.setInputs(
                    dataset[datasetColumns[0]].iloc[i],
                    dataset[datasetColumns[1]].iloc[i]
                )
                output = matcher.makeMatch()
                yPred.append(output)
                yTrue.append(dataset[datasetColumns[2]].iloc[i])
            yTrue = np.array(yTrue)
            yPred = np.array(yPred)
            metrics = {}
            for metricName, metricFunc in self.metrics.items():
                metrics[metricName] = round(metricFunc(yTrue, yPred), 2)
            metrics["Support"] = support
            self.results[moduleName] = metrics
        metric_sums = {}
        module_count = len(self.results)
        for module_scores in self.results.values():
            for metric, score in module_scores.items():
                metric_sums[metric] = metric_sums.get(metric, 0) + score
        average_metrics = {metric: round(total / module_count, 2) for metric, total in metric_sums.items()}
        self.results["Average"] = average_metrics
    def displayResults(self):
        for moduleName, metrics in self.results.items():
            print(f"Matchmaker: {moduleName}")
            for metricName, metricValue in metrics.items():
                print(f"{metricName}: {metricValue}")
            print("\n")
    
    def saveResults(self):
        results_df = pd.DataFrame(self.results).T
        results_df.to_csv("benchmarks/results/matchmaker_evaluations.csv", index=True)
        print("Results saved to matchmaker_evaluations.csv")

class ExtractorAgents:
    def __init__(self):
        self.results = {}
        self.metrics = {}
        for moduleName, moduleConfig in agent_configs.items():
            self.metrics[moduleName] = None
        self.module_configs = agent_configs
        self.dataset_columns = agent_dataset_columns
        self.vectorizer = TfidfVectorizer()
        self.factor = agentFactor   
        
    def runBenchmarks(self):
        for moduleName, config in self.module_configs.items():
            print(f"Running benchmarks for {moduleName}...")
            datasetPath = config["dataset_path"]
            extractorClass = config["matcher_class"]
            dataset = pd.read_csv(datasetPath)
            dataset = dataset.sample(frac=self.factor, random_state=1).reset_index(drop=True)
            datasetColumns = self.dataset_columns[moduleName]
            if dataset.empty:
                raise ValueError(f"Dataset for {moduleName} is empty. Please check the data path.")
            for col in datasetColumns:
                if col not in dataset.columns:
                    raise ValueError(f"Column '{col}' not found in the dataset for {moduleName}.")
            results = {}
            for i in tqdm(range(len(dataset))):
                extractor = extractorClass(apiKey=os.getenv("OPENROUTER_API_KEY"),
                                        modelName=None, # Default model will be used
                                        systemPrompt=None, # Default system prompt will be used
                                        useDefaultModelIfNone=True,
                                        useDefaultSystemPromptIfNone=True)
                inputText = dataset[datasetColumns[0]].iloc[i]
                extractor.setUserPrompt(inputText)
                output = extractor.getJsonOutput()
                results[str(i)] = output
                extractor.deleteAgent()
            scores = {}
            for col in datasetColumns[1:]:
                score = 0
                support = 0
                for i in results.keys():
                    if col not in results[i]:
                        continue
                    true = dataset[col].iloc[int(i)]
                    pred = results[i][col]
                    true = security.sanitizeInput(true, 20000)
                    pred = security.sanitizeInput(pred, 20000)
                    self.vectorizer.fit([true, pred])
                    vectors = self.vectorizer.transform([true, pred])
                    similarityScore = cosine_similarity(vectors[0], vectors[1])[0][0]
                    score += similarityScore
                    support += 1
                score /= support
                scores[col] = round(score, 2)
            scores["Support"] = support
            self.results[moduleName] = scores
        metric_sums = {}
        module_count = len(self.results)
        for module_scores in self.results.values():
            for metric, score in module_scores.items():
                metric_sums[metric] = metric_sums.get(metric, 0) + score
        average_metrics = {metric: round(total / module_count, 2) for metric, total in metric_sums.items()}
        self.results["Average"] = average_metrics


    def displayResults(self):
        for moduleName, metrics in self.results.items():
            print(f"Agent: {moduleName}")
            for columnName, metricValue in metrics.items():
                print(f"{columnName}: {metricValue}")
            print("\n")
    
    def saveResults(self):
        results_df = pd.DataFrame(self.results).T
        results_df.to_csv("benchmarks/results/agent_evaluations.csv", index=True)
        print("Results saved to agent_evaluations.csv")
    
if __name__ == "__main__":

    matchmakers = Matchmakers()
    matchmakers.runBenchmarks()
    matchmakers.saveResults()

    extractor_agents = ExtractorAgents()
    extractor_agents.runBenchmarks()
    extractor_agents.saveResults()


            