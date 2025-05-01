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

class BenchmarkRunner:
    def __init__(self, resumeText, jdText):
        self.resumeText = resumeText
        self.jdText = jdText
        self.engine = MatchingEngine()
        self.engine.setInputs(resumeText, jdText)

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
        process = psutil.Process(os.getpid())
        start_time = time.perf_counter()
        cpu_start = psutil.cpu_percent(interval=None)
        mem_start = process.memory_info().rss

        matchReport = self.engine.getMatch()

        cpu_end = psutil.cpu_percent(interval=None)
        mem_end = process.memory_info().rss
        end_time = time.perf_counter()

        report = {
            "timestamp": datetime.now().isoformat(),
            "inference_time": round(end_time - start_time, 3),
            "cpu_percent": round((cpu_start + cpu_end) / 2, 2),
            "peak_memory": round((mem_end - mem_start) / (1024 * 1024), 2),
            "gpu_usage": self.get_gpu_metrics(),
            "match_report": matchReport
        }

        reportPath = "benchmarks/results/performance_report.json"
        os.makedirs(os.path.dirname(reportPath), exist_ok=True)

        # Load existing data if file exists
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

        print("Benchmark report saved to performance_report.json")
        gc.collect()

# EXAMPLE USAGE

if __name__ == "__main__":

    reportPath = "benchmarks/results/performance_report.json"
    os.makedirs(os.path.dirname(reportPath), exist_ok=True)

    # Clear existing data if file exists
    if os.path.exists(reportPath):
        with open(reportPath, "w") as f:
            f.truncate(0)

    descriptionDatasetPath = "data/job_description_dataset.csv"
    resumeDatasetPath = "data/resume_dataset.csv"

    resumeDataset = pd.read_csv(resumeDatasetPath)
    descriptionDataset = pd.read_csv(descriptionDatasetPath)

    for i in range(100):
        resumeText = resumeDataset['Resume'].iloc[i]
        jdText = descriptionDataset['Description'].iloc[i]

        benchmarkRunner = BenchmarkRunner(resumeText, jdText)
        benchmarkRunner.run()