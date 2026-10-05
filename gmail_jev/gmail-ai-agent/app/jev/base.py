from abc import ABC, abstractmethod

class JevProvider(ABC):
    
    @abstractmethod
    def classify(self, state: str, questions: dict) -> dict:
        """
        Classify a state string given a dict of questions.
        Returns a dict of probabilities formatted as {question_key + "_probability": float}
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def model_name(self) -> str:
        pass
