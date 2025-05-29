import time
import gc
import json
import os
import csv
from datetime import datetime
import threading
import subprocess
import pandas as pd
from dotenv import load_dotenv
from api.app import create_app

app = create_app()
client = app.test_client()

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

global globalResumeJsons, globalJdJsons
globalResumeJsons = []
globalJdJsons = []

def measure_module_performance(func, *args, **kwargs):
    gc.collect()
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
        def calApi():
            response = client.post("/extract_resume", data={"resume_text": self.resumeText, "model_id": 1})
            return response.get_json()
        metrics = None
        while metrics is None:
            try:
                metrics = measure_module_performance(calApi)
            except:
                time.sleep(1)
                continue
        globalResumeJsons.append(metrics["result"])

        report = {
            "timestamp": datetime.now().isoformat(),
            "inference_time_sec": metrics["inference_time_sec"],
            "gpu_usage": self.get_gpu_metrics()
        }

        reportPath = "benchmarks/results/resume_extractor_performance.json"

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
        def calApi():
            response = client.post("/extract_jd", data={"jd_text": self.jdText, "model_id": 1})
            return response.get_json()
        metrics = None
        while metrics is None:
            try:
                metrics = measure_module_performance(calApi)
            except:
                time.sleep(1)
                continue
        globalJdJsons.append(metrics["result"])

        report = {
            "timestamp": datetime.now().isoformat(),
            "inference_time_sec": metrics["inference_time_sec"],
            "gpu_usage": self.get_gpu_metrics()
        }

        reportPath = "benchmarks/results/jd_extractor_performance.json"

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
        def calApi():
            response = client.post("/make_match", data={"resume_json": self.resumeJSON, "jd_json": self.jdJSON})
            return response.get_json()
        metrics = None
        while metrics is None:
            try:
                metrics = measure_module_performance(calApi)
            except:
                time.sleep(1)
                continue

        report = {
            "timestamp": datetime.now().isoformat(),
            "inference_time_sec": metrics["inference_time_sec"],
            "gpu_usage": self.get_gpu_metrics()
        }

        reportPath = "benchmarks/results/matchmaker_performance.json"

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

    # Start resume and JD extraction in parallel
    thread1 = threading.Thread(target=resumeExtractorBenchmarks, args=(samples, "data/resume_dataset.csv"))
    thread2 = threading.Thread(target=jdExtractorBenchmarks, args=(samples, "data/job_description_dataset.csv"))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    # Now start matchmaker
    thread3 = threading.Thread(target=matchmakerBenchmarks, args=(samples, globalResumeJsons, globalJdJsons))
    thread3.start()
    thread3.join()

    report_files = {
    "ResumeExtractor": "benchmarks/results/resume_extractor_performance.json",
    "JDExtractor": "benchmarks/results/jd_extractor_performance.json",
    "Matchmaker": "benchmarks/results/matchmaker_performance.json"
    }

    summary = []

    for module_name, file_path in report_files.items():
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            continue

        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"❌ Could not decode JSON in {file_path}")
                continue

        if not data:
            print(f"⚠️ Empty data in {file_path}")
            continue

        avg_time = sum(entry["inference_time_sec"] for entry in data) / len(data)
        summary.append({
            "ModuleName": module_name,
            "AverageInferenceTime": round(avg_time, 3),
            "Support": len(data)
        })
    
    # Write summary CSV
    csv_output_path = "benchmarks/results/performance_report.csv"

    with open(csv_output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ModuleName", "AverageInferenceTime", "Support"])
        writer.writeheader()
        writer.writerows(summary)

    print(f"✅ Summary report saved to {csv_output_path}")
    print("🎯 All benchmarks completed.")