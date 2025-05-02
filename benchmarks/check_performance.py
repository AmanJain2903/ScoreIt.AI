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
from src.resume_ocr.resume_ocr import ResumeOCR

class MatchmakerBenchmarkRunner:
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
            "memory_used": round((mem_end - mem_start) / (1024 * 1024), 2),
            "gpu_usage": self.get_gpu_metrics(),
            "match_report": matchReport
        }

        reportPath = "benchmarks/results/matchmaker_performance.json"
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

        print("Benchmark report saved to matchmaker_performance.json")
        gc.collect()

class ResumeOCRBenchmarkRunner:
    def __init__(self, pdfPath):
        self.pdfPath = pdfPath
        self.ocr = ResumeOCR()
        self.ocr.setInputs(pdfPath=pdfPath)

    def run(self):

        gc.collect()

        process = psutil.Process(os.getpid())
        start_time = time.perf_counter()
        cpu_start = psutil.cpu_percent(interval=None)
        mem_start = process.memory_info().rss

        resumeText = self.ocr.extractText()

        cpu_end = psutil.cpu_percent(interval=None)
        mem_end = process.memory_info().rss
        end_time = time.perf_counter()

        gc.collect()

        report = {
            "timestamp": datetime.now().isoformat(),
            "inference_time": round(end_time - start_time, 3),
            "cpu_percent": round((cpu_start + cpu_end) / 2, 2),
            "memory_used": round((mem_end - mem_start) / (1024 * 1024), 2),
            "resume_text": resumeText
        }

        reportPath = "benchmarks/results/resume_ocr_performance.json"
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

        print("OCR benchmark report saved to resume_ocr_performance.json")

def matchmakerBenchmarks(samples, resumeDatasetPath, descriptionDatasetPath):
    resumeDataset = pd.read_csv(resumeDatasetPath)
    descriptionDataset = pd.read_csv(descriptionDatasetPath)

    for i in range(samples):
        resumeText = resumeDataset['Resume'].iloc[i]
        jdText = descriptionDataset['Description'].iloc[i]

        benchmarkRunner = MatchmakerBenchmarkRunner(resumeText, jdText)
        benchmarkRunner.run()
        gc.collect()

def resumeOCRBenchmarks(samples, resumesDatasetPath):
    resumeFiles = os.listdir(resumesDatasetPath)

    for i in range(samples):
        resumeFilePath = os.path.join(resumesDatasetPath, resumeFiles[i])

        benchmarkRunner = ResumeOCRBenchmarkRunner(resumeFilePath)
        benchmarkRunner.run()
        gc.collect()



# EXAMPLE USAGE

if __name__ == "__main__":

    reportPath = "benchmarks/results/matchmaker_performance.json"
    os.makedirs(os.path.dirname(reportPath), exist_ok=True)

    # Clear existing data if file exists
    if os.path.exists(reportPath):
        with open(reportPath, "w") as f:
            f.truncate(0)

    reportPath = "benchmarks/results/resume_ocr_performance.json"
    os.makedirs(os.path.dirname(reportPath), exist_ok=True)

    # Clear existing data if file exists
    if os.path.exists(reportPath):
        with open(reportPath, "w") as f:
            f.truncate(0)

    samples = 100

    thread1 = threading.Thread(target=matchmakerBenchmarks, args=(samples, "data/resume_dataset.csv", "data/job_description_dataset.csv"))
    thread2 = threading.Thread(target=resumeOCRBenchmarks, args=(samples, "data/pdf_resumes"))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    print("All benchmarks completed.")
    gc.collect()