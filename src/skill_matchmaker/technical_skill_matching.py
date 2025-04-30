# TECHNICAL SKILL MATCHING

# EXAMPLE USAGE
# if __name__ == "__main__":
#     resumeSkill = "Python, Java, C++, SQL, Database Systems"
#     jobSkill = "Python, Database Management, Java"
    
#     skillMatcher = TechnicalSkillMatching()
#     skillMatcher.setInputs(resumeSkill, jobSkill)
#     score = skillMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     skillMatcher.reset()

#     print("------------------------------")

#     resumeSkill = "Python, Java, C++, SQL, Machine Learning"
#     jobSkill = "Azure, AWS, Docker, Kubernetes, CI/CD"
    
#     skillMatcher = TechnicalSkillMatching()
#     skillMatcher.setInputs(resumeSkill, jobSkill)
#     score = skillMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     skillMatcher.reset()


from src.skill_matchmaker import config
from src.skill_matchmaker.skill_matching import SkillMatching

config = config.Config()


class TechnicalSkillMatching(SkillMatching):
    def __init__(self, modelName1=None, modelName2=None, maxInputLength=None):
        super().__init__(
            modelName1=config.TECHNICAL_MODEL_NAME_1 if modelName1 is None else modelName1,
            modelName2=config.TECHNICAL_MODEL_NAME_2 if modelName2 is None else modelName2,
            maxInputLength=config.TECHNICAL_MAX_INPUT_LENGTH if maxInputLength is None else maxInputLength,
        )