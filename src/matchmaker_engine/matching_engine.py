# EXAMPLE USAGE
# if __name__ == "__main__":
#     resumeText = """
#     John Doe  
#     Email: john.doe@example.com  
#     Phone: +1-234-567-8900

#     Professional Summary:
#     Highly motivated software engineer with 3+ years of experience in full-stack development, machine learning, and cloud technologies.

#     Education:
#     - Bachelor of Technology in Computer Science, XYZ University, 2019

#     Experience:
#     - Software Engineer at TechNova (2020–2023)
#       • Developed and maintained backend APIs in Python and Flask
#       • Deployed ML models for customer churn prediction using Scikit-learn
#       • Worked with AWS Lambda, EC2, and S3

#     Skills:
#     - Programming: Python, JavaScript, SQL
#     - Frameworks: Flask, React
#     - ML: Scikit-learn, TensorFlow
#     - Tools: Git, Docker, AWS

#     Soft Skills:
#     - Problem solving, Communication, Teamwork
#     """

#     jdText = """
#     We are hiring a Machine Learning Engineer to join our data science team at InnovateAI.

#     Responsibilities:
#     - Design and deploy machine learning models for NLP and recommendation systems
#     - Collaborate with frontend and backend engineers to integrate models into production
#     - Optimize models for performance and scalability on cloud infrastructure

#     Requirements:
#     - Bachelor’s or Master’s degree in Computer Science or related field
#     - 2+ years of hands-on experience in ML or data science
#     - Proficiency in Python, TensorFlow or PyTorch, and SQL
#     - Experience with cloud services such as AWS or GCP
#     - Familiarity with Docker and CI/CD pipelines

#     Nice-to-Haves:
#     - Experience with NLP libraries like SpaCy or HuggingFace Transformers
#     - Strong communication and analytical skills
#     """

#     matchMaker = MatchingEngine()
#     matchMaker.setInputs(resumeText, jdText)
#     matchReport = matchMaker.getMatch()
#     print("Match Report:")
#     for key, value in matchReport.items():
#         print(f"{key}: {value:.2f}")
    
#     print('\n----------------------\n')

#     resumeText = """
#     Name: Priya Kapoor
#     Education: Bachelor of Design, NIFT Delhi (2018–2022)
#     Experience: 3 years as a Fashion Designer at H&M India
# 	•	Designed seasonal collections for menswear
# 	•	Managed a team of 4 junior designers
# 	•	Worked with tools like Adobe Illustrator, Photoshop, CLO 3D
# 	•	Strong creative sense, attention to detail, and trend analysis
# 	•	Languages: English, Hindi
# 	•	Certifications: Diploma in Fashion Styling
#     """

#     jdText = """
#     We are hiring a Machine Learning Engineer to join our Data Science team.
#     Requirements:
# 	•	B.Tech / M.S. in Computer Science or related field
# 	•	2+ years experience in machine learning or deep learning
# 	•	Proficient in Python, TensorFlow, and PyTorch
# 	•	Experience with cloud platforms (AWS, GCP)
# 	•	Strong understanding of statistics and data pipelines
# 	•	Excellent problem-solving and analytical skills
# 	•	Tools: Jupyter, Git, Docker
#     """

#     matchMaker = MatchingEngine()
#     matchMaker.setInputs(resumeText, jdText)
#     matchReport = matchMaker.getMatch()
#     print("Match Report:")
#     for key, value in matchReport.items():
#         print(f"{key}: {value:.2f}")

import os
from src.education_matchmaker.education_matching import EducationMatching
from src.experience_matchmaker.experience_matching import ExperienceMatching
from src.skill_matchmaker.technical_skill_matching import TechnicalSkillMatching
from src.skill_matchmaker.soft_skill_matching import SoftSkillMatching
from src.tools_matchmaker.tools_matching import ToolMatching
from src.certification_matchmaker.certification_matching import CertificationMatching
from src.designation_matchmaker.designation_matching import DesignationMatching
from dotenv import load_dotenv
from src.utils.model_load import model1, model2
import time
load_dotenv()
import torch
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp
import atexit
import os
import glob

class MatchingEngine:
    def __init__(self):
        self.education_matcher = EducationMatching()
        self.experience_matcher = ExperienceMatching()
        self.technical_skill_matcher = TechnicalSkillMatching()
        self.soft_skill_matcher = SoftSkillMatching()
        self.tool_matcher = ToolMatching()
        self.certification_matcher = CertificationMatching()
        self.designation_matcher = DesignationMatching()
        self.resume_json = None
        self.jd_json = None
        self.matchReport = {
            "EDUCATION": 0.0,
            "EXPERIENCE": 0.0,
            "TECHNICAL_SKILL": 0.0,
            "SOFT_SKILL": 0.0,
            "TOOL": 0.0,
            "CERTIFICATION": 0.0,
            "DESIGNATION": 0.0
        }
        self.matcher_map = {
            "EDUCATION": EducationMatching(),
            "EXPERIENCE": ExperienceMatching(),
            "TECHNICAL_SKILL": TechnicalSkillMatching(),
            "SOFT_SKILL": SoftSkillMatching(),
            "TOOL": ToolMatching(),
            "CERTIFICATION": CertificationMatching(),
            "DESIGNATION": DesignationMatching()
        }
    
    def _run_matcher(self, entity):
        try:
            resume_data = self.resume_json.get(entity, [])
            jd_data = self.jd_json.get(entity, [])
            matcher = self.matcher_map[entity]
            matcher.setInputs(resume_data, jd_data)
            score = matcher.makeMatch()
            return (entity, score)
        except Exception as e:
            return (entity, 0.0)

    def getMatch(self):
        if not self.resume_json or not self.jd_json:
            return self.matchReport
        
        total_start = time.time()

        with ThreadPoolExecutor(max_workers=len(self.matchReport)) as executor:
            futures = [executor.submit(self._run_matcher, entity) for entity in self.matchReport]
            for future in as_completed(futures):
                entity, score = future.result()
                self.matchReport[entity] = score

        total_end = time.time()
        print(f"🚀 Total matching completed in {total_end - total_start:.2f}s")

        return self.matchReport

    




        
            

    

    