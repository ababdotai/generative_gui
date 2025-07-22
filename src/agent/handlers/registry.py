"""Component registry for managing and loading component handlers."""

from typing import Dict, Type, Optional

from .base import BaseComponentHandler
from .weather import WeatherHandler
from .todo import TodoHandler
from .video_editing import VideoEditingHandler


class ComponentRegistry:
    """Registry for managing component handlers.
    
    This class provides a centralized way to register and retrieve
    component handlers for different types of user requests.
    """
    
    def __init__(self):
        """Initialize the component registry with default handlers."""
        self._handlers: Dict[str, Type[BaseComponentHandler]] = {}
        self._instances: Dict[str, BaseComponentHandler] = {}
        
        # Register default handlers
        self.register_handler('weather', WeatherHandler)
        self.register_handler('todo', TodoHandler)
        self.register_handler('video_editing', VideoEditingHandler)
    
    def register_handler(self, component_type: str, handler_class: Type[BaseComponentHandler]) -> None:
        """Register a component handler.
        
        Args:
            component_type: Type identifier for the component
            handler_class: Handler class that implements BaseComponentHandler
        """
        self._handlers[component_type] = handler_class
        # Clear cached instance if exists
        if component_type in self._instances:
            del self._instances[component_type]
    
    def get_handler(self, component_type: str) -> Optional[BaseComponentHandler]:
        """Get a component handler instance.
        
        Args:
            component_type: Type identifier for the component
            
        Returns:
            Handler instance or None if not found
        """
        if component_type not in self._handlers:
            return None
        
        # Use cached instance if available
        if component_type not in self._instances:
            handler_class = self._handlers[component_type]
            self._instances[component_type] = handler_class()
        
        return self._instances[component_type]
    
    def list_handlers(self) -> Dict[str, str]:
        """List all registered handlers.
        
        Returns:
            Dictionary mapping component types to handler class names
        """
        return {comp_type: handler_class.__name__ for comp_type, handler_class in self._handlers.items()}
    
    def unregister_handler(self, component_type: str) -> bool:
        """Unregister a component handler.
        
        Args:
            component_type: Type identifier for the component
            
        Returns:
            True if handler was removed, False if not found
        """
        removed = False
        if component_type in self._handlers:
            del self._handlers[component_type]
            removed = True
        
        if component_type in self._instances:
            del self._instances[component_type]
        
        return removed


# Global registry instance
component_registry = ComponentRegistry()


def get_component_handler(component_type: str) -> Optional[BaseComponentHandler]:
    """Convenience function to get a component handler.
    
    Args:
        component_type: Type identifier for the component
        
    Returns:
        Handler instance or None if not found
    """
    return component_registry.get_handler(component_type)


def register_component_handler(component_type: str, handler_class: Type[BaseComponentHandler]) -> None:
    """Convenience function to register a component handler.
    
    Args:
        component_type: Type identifier for the component
        handler_class: Handler class that implements BaseComponentHandler
    """
    component_registry.register_handler(component_type, handler_class)