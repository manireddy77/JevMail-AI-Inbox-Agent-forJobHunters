from app.jev.base import JevProvider
from app.config import TYPESAFE_API_KEY
import os

class TypeSafeJevProvider(JevProvider):
    def __init__(self):
        try:
            from typesafe_sdk import TypeSafeClient, Noul, Choice, Score
        except ImportError:
            raise ImportError("Please install typesafe-sdk")
            
        self.Noul = Noul
        self.Choice = Choice
        self.Score = Score
        
        if not TYPESAFE_API_KEY:
            raise ValueError("TYPESAFE_API_KEY environment variable is missing")
            
        # The SDK typically looks for TYPESAFE_API_KEY in the environment
        os.environ["TYPESAFE_API_KEY"] = TYPESAFE_API_KEY
        self.client = TypeSafeClient()

    def classify(self, state: str, questions: dict) -> dict:
        sdk_questions = {}
        for k, v in questions.items():
            if v["type"] == "noul":
                sdk_questions[k] = self.Noul(instructions=v["instructions"])
            elif v["type"] == "choice":
                sdk_questions[k] = self.Choice(instructions=v["instructions"], criteria=v["criteria"])
            elif v["type"] == "score":
                sdk_questions[k] = self.Score(instructions=v["instructions"], criteria=v["criteria"])
                
        result = self.client.system_one(state, sdk_questions)
        
        output = {}
        for k, v in questions.items():
            if v["type"] == "noul":
                output[f"{k}_probability"] = float(result.nouls[k].noul)
            elif v["type"] == "score":
                output[f"{k}_score"] = result.scores[k].score
            elif v["type"] == "choice":
                output[f"{k}_choice"] = result.choices[k].choice
                
        return output

    @property
    def provider_name(self) -> str:
        return "typesafe"

    @property
    def model_name(self) -> str:
        return "jev-latest"
