"""Video editing component handler."""

import os
import json
from typing import Dict, Any, TypedDict, List

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .base import BaseComponentHandler
from ..utils.language import format_response
from ..utils.response import create_component_response, create_ui_component


class VideoEditingTask(TypedDict):
    """Video editing task with details."""
    
    id: str
    title: str
    description: str
    completed: bool


class VideoEditingOutput(TypedDict):
    """Video editing output with subtraction and addition tasks."""
    
    title: str
    subtractionTasks: List[VideoEditingTask]
    additionTasks: List[VideoEditingTask]


class VideoEditingHandler(BaseComponentHandler):
    """Handler for video editing requests."""
    
    @property
    def component_type(self) -> str:
        """Return the component type identifier."""
        return "videoEditingTodo"
    
    async def process_request(self, request: str, language: str = 'en') -> Dict[str, Any]:
        """Process video editing request and return response with UI components.
        
        Args:
            request: User's video editing request
            language: Language code for response ('en', 'zh', 'ja')
            
        Returns:
            Dictionary with 'result' (text) and 'ui_components' (list of UI data)
        """
        try:
            # Generate video editing plan using OpenAI
            video_editing_data = await self._generate_video_editing_plan(request)
            
            # Create UI component
            ui_component = create_ui_component(self.component_type, video_editing_data)
            
            # Calculate task counts
            removal_count = len(video_editing_data['subtractionTasks'])
            addition_count = len(video_editing_data['additionTasks'])
            total_count = removal_count + addition_count
            
            # Generate response text
            result_text = format_response(
                'video_editing_success', language,
                title=video_editing_data['title'],
                removal_count=removal_count,
                addition_count=addition_count,
                total_count=total_count
            )
            
            return create_component_response(result_text, [ui_component])
            
        except Exception as e:
            # Fallback response if API call fails
            return self._create_fallback_video_editing_response(language)
    
    async def _generate_video_editing_plan(self, request: str) -> VideoEditingOutput:
        """Generate video editing plan using OpenAI API."""
        # Initialize OpenAI client
        llm = ChatOpenAI(
            model=os.environ.get("OPENAI_MODEL_ID", "gpt-3.5-turbo"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Create prompt for video editing task planning with structured JSON output
        video_editing_prompt = f"""
You are a professional video editing assistant. Based on the user's video editing request, create a comprehensive editing plan with two categories of tasks:

1. SUBTRACTION tasks (things to remove, cut, or reduce)
2. ADDITION tasks (things to add, enhance, or create)

User request: {request}

You MUST respond with a valid JSON object in the following exact format:
{{
  "title": "A clear, concise title for this video editing project (max 8 words)",
  "subtractionTasks": [
    {{
      "title": "Task title",
      "details": "Detailed description of what to do and why"
    }},
    {{
      "title": "Another task",
      "details": "Another detailed description"
    }}
  ],
  "additionTasks": [
    {{
      "title": "Task title",
      "details": "Detailed description of what to add and how"
    }},
    {{
      "title": "Another task",
      "details": "Another detailed description"
    }}
  ]
}}

Requirements:
- Provide 2-4 subtraction tasks (removing unwanted elements)
- Provide 2-4 addition tasks (adding new elements or enhancements)
- Each task must have a concise title and detailed description
- Make each task specific and actionable for video editing
- Use the same language as the user's request for all text content
- Return ONLY the JSON object, no additional text or formatting
"""

        # Call OpenAI API
        response = await llm.ainvoke([HumanMessage(content=video_editing_prompt)])
        ai_response = response.content

        # Parse JSON response with robust error handling
        title = "Video Editing Project"
        subtraction_tasks = []
        addition_tasks = []

        if isinstance(ai_response, str):
            try:
                # Clean the response to extract JSON
                cleaned_response = ai_response.strip()
                
                # Remove any markdown code block formatting if present
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]
                
                cleaned_response = cleaned_response.strip()
                
                # Parse JSON
                parsed_data = json.loads(cleaned_response)
                
                # Extract data from parsed JSON
                if isinstance(parsed_data, dict):
                    title = parsed_data.get('title', 'Video Editing Project')
                    subtraction_tasks_raw = parsed_data.get('subtractionTasks', [])
                    addition_tasks_raw = parsed_data.get('additionTasks', [])
                    
                    # Process task objects
                    subtraction_tasks = []
                    addition_tasks = []
                    
                    for task in subtraction_tasks_raw:
                        if isinstance(task, dict):
                            subtraction_tasks.append({
                                'title': task.get('title', ''),
                                'details': task.get('details', '')
                            })
                        elif isinstance(task, str):
                            # Backward compatibility for string tasks
                            subtraction_tasks.append({
                                'title': task,
                                'details': f"Remove or reduce: {task.lower()}"
                            })
                    
                    for task in addition_tasks_raw:
                        if isinstance(task, dict):
                            addition_tasks.append({
                                'title': task.get('title', ''),
                                'details': task.get('details', '')
                            })
                        elif isinstance(task, str):
                            # Backward compatibility for string tasks
                            addition_tasks.append({
                                'title': task,
                                'details': f"Add or enhance: {task.lower()}"
                            })
                    
            except (json.JSONDecodeError, KeyError, TypeError) as parse_error:
                print(f"JSON parsing failed: {parse_error}")
                # Fallback to basic text parsing for backward compatibility
                lines = ai_response.split("\n")
                current_section = None
                
                for line in lines:
                    line = line.strip()
                    if "title" in line.lower() and ":" in line:
                        title_part = line.split(":", 1)[1].strip().strip('"').strip("'")
                        if title_part:
                            title = title_part
                    elif "subtraction" in line.lower() and ("task" in line.lower() or "[" in line):
                        current_section = "subtraction"
                    elif "addition" in line.lower() and ("task" in line.lower() or "[" in line):
                        current_section = "addition"
                    elif line.startswith("-") or line.startswith("*") or (line.startswith('"') and line.endswith('"')):
                        task_text = line.lstrip("-*").strip().strip('"').strip("'").rstrip(",")
                        if task_text and current_section == "subtraction":
                            subtraction_tasks.append({
                                'title': task_text,
                                'details': f"Remove or reduce: {task_text.lower()}"
                            })
                        elif task_text and current_section == "addition":
                            addition_tasks.append({
                                'title': task_text,
                                'details': f"Add or enhance: {task_text.lower()}"
                            })

        # Fallback if no tasks found
        if not subtraction_tasks:
            subtraction_tasks = [
                {'title': "Remove unwanted footage", 'details': "Cut out unnecessary or poor quality clips"},
                {'title': "Cut unnecessary scenes", 'details': "Remove redundant or overly long segments"},
                {'title': "Delete background noise", 'details': "Clean up audio by removing unwanted sounds"}
            ]
        if not addition_tasks:
            addition_tasks = [
                {'title': "Add transitions", 'details': "Insert smooth transitions between scenes for better flow"},
                {'title': "Insert background music", 'details': "Add appropriate music to enhance the mood"},
                {'title': "Create title sequence", 'details': "Add opening and closing title cards"}
            ]

        # Create task objects with IDs
        subtraction_task_objects = [
            VideoEditingTask(
                id=f"sub_{i+1}",
                title=task['title'],
                description=task['details'],
                completed=False
            )
            for i, task in enumerate(subtraction_tasks)
        ]
        
        addition_task_objects = [
            VideoEditingTask(
                id=f"add_{i+1}",
                title=task['title'],
                description=task['details'],
                completed=False
            )
            for i, task in enumerate(addition_tasks)
        ]

        return VideoEditingOutput(
            title=title,
            subtractionTasks=subtraction_task_objects,
            additionTasks=addition_task_objects
        )
    
    def _create_fallback_video_editing_response(self, language: str) -> Dict[str, Any]:
        """Create fallback video editing response when API call fails."""
        fallback_subtraction = [
            VideoEditingTask(id="sub_1", title="Remove unwanted footage", description="Cut out unnecessary or poor quality clips", completed=False),
            VideoEditingTask(id="sub_2", title="Reduce background noise", description="Clean up audio by removing unwanted sounds", completed=False),
            VideoEditingTask(id="sub_3", title="Trim excess content", description="Remove redundant or overly long segments", completed=False)
        ]
        
        fallback_addition = [
            VideoEditingTask(id="add_1", title="Add smooth transitions", description="Insert transitions between scenes for better flow", completed=False),
            VideoEditingTask(id="add_2", title="Insert background music", description="Add appropriate music to enhance the mood", completed=False),
            VideoEditingTask(id="add_3", title="Create title cards", description="Add opening and closing title sequences", completed=False)
        ]
        
        fallback_data = VideoEditingOutput(
            title="General Video Editing",
            subtractionTasks=fallback_subtraction,
            additionTasks=fallback_addition
        )
        
        ui_component = create_ui_component(self.component_type, fallback_data)
        
        # Generate fallback response text
        result_text = format_response(
            'video_editing_fallback', language
        )
        
        return create_component_response(result_text, [ui_component])