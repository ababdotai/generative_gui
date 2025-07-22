"""Base component handler interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseComponentHandler(ABC):
    """Abstract base class for all component handlers.
    
    Each component handler should implement the process_request method
    to handle user requests and return formatted responses with UI components.
    """
    
    @abstractmethod
    async def process_request(self, request: str, language: str = 'en') -> Dict[str, Any]:
        """Process user request and return response with UI components.
        
        Args:
            request: User's request string
            language: Language code for response ('en', 'zh', 'ja')
            
        Returns:
            Dictionary with 'result' (text) and 'ui_components' (list of UI data)
        """
        pass
    
    @property
    @abstractmethod
    def component_type(self) -> str:
        """Return the component type identifier.
        
        Returns:
            Component type string (e.g., 'weather', 'todo', 'videoEditingTodo')
        """
        pass
    
    def create_fallback_response(self, message: str, language: str = 'en') -> Dict[str, Any]:
        """Create a fallback response when processing fails.
        
        Args:
            message: Fallback message
            language: Language code
            
        Returns:
            Dictionary with fallback response
        """
        from ..utils.response import create_component_response
        return create_component_response(message, [])