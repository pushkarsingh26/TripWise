from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.models.modification import ModificationIntent


class BaseLLMProvider(ABC):
    """
    Abstract Base Class for LLM providers in Tripwise.
    Ensures provider-agnostic intent interpretation for Phase 7.
    """

    @abstractmethod
    def interpret_modification(
        self,
        message: str,
        current_trip: Optional[Dict[str, Any]] = None,
    ) -> ModificationIntent:
        """
        Interprets a natural-language modification request and returns a structured ModificationIntent.
        """
        pass
