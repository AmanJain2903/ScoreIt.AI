import time
import psutil
import gc
import json
import os
from datetime import datetime
import threading
import subprocess
import pandas as pd
from src.matchmaker_engine.matching_engine import MatchingEngine
from src.resume_extractor_agent.resume_agent import ResumeAgent
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

global globalResumeJsons, globalJdJsons
globalResumeJsons = []
globalJdJsons = []

def measure_module_performance(func, *args, **kwargs):
    gc.collect()
    process = psutil.Process(os.getpid())
    start_time = time.perf_counter()

    result = func(*args, **kwargs)

    end_time = time.perf_counter()
    gc.collect()

    return {
        "inference_time_sec": round(end_time - start_time, 3),
        "result": result
    }

class ResumeExtractorBenchmarkRunner:
    def __init__(self, resumeText):
        self.resumeText = resumeText
        self.resumeAgent = ResumeAgent(
            apiKey=API_KEY,
            modelName=None,
            systemPrompt=None,
            useDefaultModelIfNone=True,
            useDefaultSystemPromptIfNone=True,
            modelID=1
        )
        self.resumeAgent.setUserPrompt(resumeText)

    def get_gpu_metrics(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                mem, util = result.stdout.strip().split(', ')
                return {"gpu_memory_mb": int(mem), "gpu_util_percent": int(util)}
        except Exception:
            pass
        return {"gpu_memory_mb": None, "gpu_util_percent": None}

    def run(self):
        metrics = measure_module_performance(self.resumeAgent.getResponse)
        globalResumeJsons.append(metrics["result"])

        report = {
            "timestamp": datetime.now().isoformat(),
            "inference_time_sec": metrics["inference_time_sec"],
            "gpu_usage": self.get_gpu_metrics()
        }

        reportPath = "benchmarks/results/resume_extractor_performance.json"
        os.makedirs(os.path.dirname(reportPath), exist_ok=True)

        if os.path.exists(reportPath):
            with open(reportPath, "r") as f:
                try:
                    existingData = json.load(f)
                    if not isinstance(existingData, list):
                        existingData = [existingData]
                except json.JSONDecodeError:
                    existingData = []
        else:
            existingData = []

        existingData.append(report)

        with open(reportPath, "w") as f:
            json.dump(existingData, f, indent=2)

        print("✅ Resume Extractor benchmark saved.")


class JDExtractorBenchmarkRunner:
    def __init__(self, jdText):
        self.jdText = jdText
        self.jdAgent = JobDescriptionAgent(
            apiKey=API_KEY,
            modelName=None,
            systemPrompt=None,
            useDefaultModelIfNone=True,
            useDefaultSystemPromptIfNone=True,
            modelID=1
        )
        self.jdAgent.setUserPrompt(jdText)

    def get_gpu_metrics(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                mem, util = result.stdout.strip().split(', ')
                return {"gpu_memory_mb": int(mem), "gpu_util_percent": int(util)}
        except Exception:
            pass
        return {"gpu_memory_mb": None, "gpu_util_percent": None}

    def run(self):
        metrics = measure_module_performance(self.jdAgent.getResponse)
        globalJdJsons.append(metrics["result"])

        report = {
            "timestamp": datetime.now().isoformat(),
            "inference_time_sec": metrics["inference_time_sec"],
            "gpu_usage": self.get_gpu_metrics()
        }

        reportPath = "benchmarks/results/jd_extractor_performance.json"
        os.makedirs(os.path.dirname(reportPath), exist_ok=True)

        if os.path.exists(reportPath):
            with open(reportPath, "r") as f:
                try:
                    existingData = json.load(f)
                    if not isinstance(existingData, list):
                        existingData = [existingData]
                except json.JSONDecodeError:
                    existingData = []
        else:
            existingData = []

        existingData.append(report)

        with open(reportPath, "w") as f:
            json.dump(existingData, f, indent=2)

        print("✅ JD Extractor benchmark saved.")

class MatchmakerBenchmarkRunner:
    def __init__(self, resumeJSON, jdJSON):
        self.resumeJSON = resumeJSON
        self.jdJSON = jdJSON
        self.engine = MatchingEngine()
        self.engine.resume_json = resumeJSON
        self.engine.jd_json = jdJSON

    def get_gpu_metrics(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                mem, util = result.stdout.strip().split(', ')
                return {"gpu_memory_mb": int(mem), "gpu_util_percent": int(util)}
        except Exception:
            pass
        return {"gpu_memory_mb": None, "gpu_util_percent": None}

    def run(self):
        metrics = measure_module_performance(self.engine.getMatch)

        report = {
            "timestamp": datetime.now().isoformat(),
            "inference_time_sec": metrics["inference_time_sec"],
            "gpu_usage": self.get_gpu_metrics()
        }

        reportPath = "benchmarks/results/matchmaker_performance.json"
        os.makedirs(os.path.dirname(reportPath), exist_ok=True)

        if os.path.exists(reportPath):
            with open(reportPath, "r") as f:
                try:
                    existingData = json.load(f)
                    if not isinstance(existingData, list):
                        existingData = [existingData]
                except json.JSONDecodeError:
                    existingData = []
        else:
            existingData = []

        existingData.append(report)

        with open(reportPath, "w") as f:
            json.dump(existingData, f, indent=2)

        print("✅ Matchmaker benchmark saved.")

def resumeExtractorBenchmarks(samples, resumeDatasetPath):
    resumeDataset = pd.read_csv(resumeDatasetPath)
    for i in range(samples):
        resumeText = resumeDataset['Resume'].iloc[i]
        runner = ResumeExtractorBenchmarkRunner(resumeText)
        runner.run()

def jdExtractorBenchmarks(samples, jdDatasetPath):
    jdDataset = pd.read_csv(jdDatasetPath)
    for i in range(samples):
        jdText = jdDataset['Description'].iloc[i]
        runner = JDExtractorBenchmarkRunner(jdText)
        runner.run()

def matchmakerBenchmarks(samples, globalResumeJsons, globalJdJsons):

    for i in range(len(globalResumeJsons)):
        runner = MatchmakerBenchmarkRunner(globalResumeJsons[i], globalJdJsons[i])
        runner.run()


if __name__ == "__main__":
    os.makedirs("benchmarks/results", exist_ok=True)

    # Clear previous results
    for path in ["matchmaker_performance.json", "resume_extractor_performance.json", "jd_extractor_performance.json"]:
        fullPath = f"benchmarks/results/{path}"
        if os.path.exists(fullPath):
            with open(fullPath, "w") as f:
                f.truncate(0)

    samples = 50

    resumeExtractorBenchmarks(samples, "data/resume_dataset.csv")
    jdExtractorBenchmarks(samples, "data/job_description_dataset.csv")
    matchmakerBenchmarks(samples, globalResumeJsons, globalJdJsons)

    print("🎯 All benchmarks completed.")