# 📊 Benchmarks - ScoreIt.AI

This folder contains **benchmark evaluation scripts** and **generated results** for the different modules of the ScoreIt.AI system.

---

## ⚙️ What is Benchmarked?

| Module Type | Evaluated Items |
|:---|:---|
| **Matchmakers** | Education Matching, Experience Matching, Technical Skill Matching, Soft Skill Matching, Tool Matching, Certification Matching, Designation Matching |
| **Extractor Agents** | Resume Extractor Agent, Job Description Extractor Agent |

---

## 🛠️ Files Inside

| File | Purpose |
|:---|:---|
| `evaluate_modules.py` | Script to run evaluations and generate benchmark CSVs |
| `results/matchmaker_evaluations.csv` | Evaluation results for all Matchmaker modules |
| `results/agent_evaluations.csv` | Evaluation results for Resume Agent and JD Agent |

---

## 🚀 How to Run Locally

Make sure you have the project installed and environment ready.

Then run:

```bash
PYTHONPATH=. python benchmarks/evaluate_modules.py
```

✅ This will:
- Benchmark all matchmakers and agents
- Save the results into `benchmarks/results/` as CSV files

---

## 🚀 How to Run from GitHub Actions

This project provides a **manual GitHub Action** to run benchmarks anytime.

- Workflow File: `.github/workflows/evaluate_modules.yml`
- Trigger manually from GitHub → **Actions** tab → **Run workflow**

After running:
- Download artifacts:
  - `matchmaker-evaluations`
  - `agent-evaluations`

Each artifact will contain the corresponding CSV benchmark file.

---

## 📈 Metrics for Matchmakers

| Metric | Description |
|:---|:---|
| MAE | Mean Absolute Error |
| MSE | Mean Squared Error |
| R² | Coefficient of Determination (Goodness of Fit) |
| Accuracy | Custom metric (Predictions within ±15% range are considered accurate) |

---

## 📈 Metrics for Extractor Agents

| Metric | Description |
|:---|:---|
| Cosine Similarity | Measures semantic similarity between extracted vs true fields like Education, Experience, Skills, Certifications, Designation |

---

## 📦 Notes

- Benchmark datasets are located inside the `/data/` folder.
- Benchmarks must be **manually refreshed** after major model or prompt improvements.
- Future Enhancements Planned:
  - Performance Benchmarks
    - Inference Time Benchmarking
    - CPU/RAM Usage Metrics

---

# 🎯 Goal

Ensure that every module in ScoreIt.AI is **accurate, fast, and reliable** through continuous evaluation.