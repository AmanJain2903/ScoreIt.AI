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
from src.resume_extractor_agent.resume_agent import ResumeAgent
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
from dotenv import load_dotenv
import threading

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class MatchingEngine:
    def __init__(self):
        self.education_matcher = EducationMatching()
        self.experience_matcher = ExperienceMatching()
        self.technical_skill_matcher = TechnicalSkillMatching()
        self.soft_skill_matcher = SoftSkillMatching()
        self.tool_matcher = ToolMatching()
        self.certification_matcher = CertificationMatching()
        self.designation_matcher = DesignationMatching()
        self.resume_agent = ResumeAgent(
            apiKey=os.getenv("OPENROUTER_API_KEY"),
            modelName=None,
            systemPrompt=None,
            useDefaultModelIfNone=True,
            useDefaultSystemPromptIfNone=True
        )
        self.jd_agent = JobDescriptionAgent(
            apiKey=os.getenv("OPENROUTER_API_KEY"),
            modelName=None,
            systemPrompt=None,
            useDefaultModelIfNone=True,
            useDefaultSystemPromptIfNone=True
        )
        self.resumeText = None
        self.jdText = None
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

    def setInputs(self, resumeText, jdText):
        if not resumeText or not jdText:
            raise ValueError("Resume text and Job Description text cannot be empty.")
        if not isinstance(resumeText, str) or not isinstance(jdText, str):
            raise TypeError("Resume text and Job Description text must be strings.")

        self.resumeText = resumeText
        self.jdText = jdText
    
    def getResumeJson(self):
        if not self.resumeText:
            raise ValueError("Inputs not set. Please set resume and job description text before getting JSON.")
        self.resume_agent.setUserPrompt(self.resumeText)
        self.resume_json = self.resume_agent.getJsonOutput()
        self.resume_agent.deleteAgent()
    
    def getJDJson(self):
        if not self.resumeText:
            raise ValueError("Inputs not set. Please set resume and job description text before getting JSON.")
        self.jd_agent.setUserPrompt(self.jdText)
        self.jd_json = self.jd_agent.getJsonOutput()
        self.jd_agent.deleteAgent()
            
    def getMatch(self):
        if not self.resumeText or not self.jdText:
            raise ValueError("Inputs not set. Please set resume and job description text before getting match.")
        
        if not self.resume_json or not self.jd_json:
            self.resume_agent.getClient()
            self.jd_agent.getClient()
            thread1 = threading.Thread(target=self.getResumeJson)
            thread2 = threading.Thread(target=self.getJDJson)
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
        
        for entity in self.matchReport.keys():
            if entity == "EDUCATION":
                print("Matching Education")
                if not self.resume_json['EDUCATION'] or not self.jd_json['EDUCATION']:
                    continue 
                self.education_matcher.setInputs(
                    self.resume_json['EDUCATION'],
                    self.jd_json['EDUCATION']
                )
                self.matchReport[entity] = self.education_matcher.makeMatch()
            elif entity == "EXPERIENCE":   
                print("Matching Experience")
                if not self.resume_json['EXPERIENCE'] or not self.jd_json['EXPERIENCE']:
                    continue 
                self.experience_matcher.setInputs(
                    self.resume_json['EXPERIENCE'],
                    self.jd_json['EXPERIENCE']
                )
                self.matchReport[entity] = self.experience_matcher.makeMatch()
            elif entity == "TECHNICAL_SKILL":
                print("Matching Technical Skill")
                if not self.resume_json['TECHNICAL_SKILL'] or not self.jd_json['TECHNICAL_SKILL']:
                    continue 
                self.technical_skill_matcher.setInputs(
                    self.resume_json['TECHNICAL_SKILL'],
                    self.jd_json['TECHNICAL_SKILL']
                )
                self.matchReport[entity] = self.technical_skill_matcher.makeMatch()
            elif entity == "SOFT_SKILL":
                print("Matching Soft Skill")
                if not self.resume_json['SOFT_SKILL'] or not self.jd_json['SOFT_SKILL']:
                    continue 
                self.soft_skill_matcher.setInputs(
                    self.resume_json['SOFT_SKILL'],
                    self.jd_json['SOFT_SKILL']
                )
                self.matchReport[entity] = self.soft_skill_matcher.makeMatch()
            elif entity == "TOOL":
                print("Matching Tool")
                if not self.resume_json['TOOL'] or not self.jd_json['TOOL']:
                    continue 
                self.tool_matcher.setInputs(
                    self.resume_json['TOOL'],
                    self.jd_json['TOOL']
                )
                self.matchReport[entity] = self.tool_matcher.makeMatch()
            elif entity == "CERTIFICATION":
                print("Matching Certification")
                if not self.resume_json['CERTIFICATION'] or not self.jd_json['CERTIFICATION']:
                    continue 
                self.certification_matcher.setInputs(
                    self.resume_json['CERTIFICATION'],
                    self.jd_json['CERTIFICATION']
                )
                self.matchReport[entity] = self.certification_matcher.makeMatch()
            elif entity == "DESIGNATION":
                print("Matching Designation")
                if not self.resume_json['DESIGNATION'] or not self.jd_json['DESIGNATION']:
                    continue 
                self.designation_matcher.setInputs(
                    self.resume_json['DESIGNATION'],
                    self.jd_json['DESIGNATION']
                )
                self.matchReport[entity] = self.designation_matcher.makeMatch()
        return self.matchReport



        
            

    

    