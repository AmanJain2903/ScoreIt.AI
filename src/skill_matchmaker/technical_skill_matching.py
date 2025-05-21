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
    def __init__(self, maxInputLength=None):
        super().__init__(
            maxInputLength=config.TECHNICAL_MAX_INPUT_LENGTH if maxInputLength is None else maxInputLength,
        )