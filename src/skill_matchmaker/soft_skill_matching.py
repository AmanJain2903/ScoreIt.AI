# SOFT SKILL MATCHING

# EXAMPLE USAGE
# if __name__ == "__main__":
#     resumeSkill = "Leadership, Teamwork, Communication, Problem Solving"
#     jobSkill = "Team Collaboration, Effective Communication, Conflict Resolution"
    
#     skillMatcher = SoftSkillMatching()
#     skillMatcher.setInputs(resumeSkill, jobSkill)
#     score = skillMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     skillMatcher.reset()

#     print("------------------------------")

#     resumeSkill = "Team Collaboration, Effective Communication, Conflict Resolution"
#     jobSkill = "Patience, Empathy, Active Listening, Negotiation"
    
#     skillMatcher = SoftSkillMatching()
#     skillMatcher.setInputs(resumeSkill, jobSkill)
#     score = skillMatcher.makeMatch()
#     print(f"Similarity Score: {score}")

#     skillMatcher.reset()

from src.skill_matchmaker import config
from src.skill_matchmaker.skill_matching import SkillMatching

config = config.Config()


class SoftSkillMatching(SkillMatching):
    def __init__(self, maxInputLength=None):
        super().__init__(
            maxInputLength=config.SOFT_MAX_INPUT_LENGTH if maxInputLength is None else maxInputLength,
        )

