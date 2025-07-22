"""Response formatting utilities."""

from typing import Dict, List, Any


def create_component_response(result_text: str, ui_components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create standardized component response format.
    
    Args:
        result_text: Text response for the user
        ui_components: List of UI component data
        
    Returns:
        Dictionary with 'result' and 'ui_components' keys
    """
    return {
        "result": result_text,
        "ui_components": ui_components
    }


def create_ui_component(component_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create UI component data structure.
    
    Args:
        component_type: Type of the UI component (e.g., 'weather', 'todo', 'videoEditingTodo')
        data: Component-specific data
        
    Returns:
        UI component dictionary
    """
    return {
        "type": component_type,
        "data": data
    }