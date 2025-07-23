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
      "details": "Detailed description of what to do and why",
      "tags": ["tag1", "tag2"]
    }},
    {{
      "title": "Another task",
      "details": "Another detailed description",
      "tags": ["tag1", "tag2", "tag3"]
    }}
  ],
  "additionTasks": [
    {{
      "title": "Task title",
      "details": "Detailed description of what to add and how",
      "tags": ["tag1", "tag2"]
    }},
    {{
      "title": "Another task",
      "details": "Another detailed description",
      "tags": ["tag1"]
    }}
  ]
}}

Requirements:
- Provide 2-4 subtraction tasks (removing unwanted elements)
- Provide 2-4 addition tasks (adding new elements or enhancements)
- Each task must have a concise title and detailed description
- Each task should have 1-3 relevant tags for categorization
- Tags should be in the SAME LANGUAGE as the user's request (if Chinese: use "音频", "视觉", "特效", "转场", "颜色", "时机", "质量", "创意"; if English: use "audio", "visual", "effects", "transitions", "color", "timing", "quality", "creative")
- Make each task specific and actionable for video editing
- Use the same language as the user's request for all text content including tags
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
                                'details': task.get('details', ''),
                                'tags': task.get('tags', [])
                            })
                        elif isinstance(task, str):
                            # Backward compatibility for string tasks
                            subtraction_tasks.append({
                                'title': task,
                                'details': f"Remove or reduce: {task.lower()}",
                                'tags': ['editing']
                            })
                    
                    for task in addition_tasks_raw:
                        if isinstance(task, dict):
                            addition_tasks.append({
                                'title': task.get('title', ''),
                                'details': task.get('details', ''),
                                'tags': task.get('tags', [])
                            })
                        elif isinstance(task, str):
                            # Backward compatibility for string tasks
                            addition_tasks.append({
                                'title': task,
                                'details': f"Add or enhance: {task.lower()}",
                                'tags': ['enhancement']
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

        # Fallback if no tasks found - detect language from request
        is_chinese = any(ord(char) > 127 for char in request)
        
        if not subtraction_tasks:
            if is_chinese:
                subtraction_tasks = [
                    {'title': "移除不需要的片段", 'details': "剪掉不必要或质量差的镜头", 'tags': ['剪辑', '质量']},
                    {'title': "删除冗余场景", 'details': "移除重复或过长的片段", 'tags': ['剪辑', '时机']},
                    {'title': "清除背景噪音", 'details': "清理音频中的不需要声音", 'tags': ['音频', '质量']}
                ]
            else:
                subtraction_tasks = [
                    {'title': "Remove unwanted footage", 'details': "Cut out unnecessary or poor quality clips", 'tags': ['editing', 'quality']},
                    {'title': "Cut unnecessary scenes", 'details': "Remove redundant or overly long segments", 'tags': ['editing', 'timing']},
                    {'title': "Delete background noise", 'details': "Clean up audio by removing unwanted sounds", 'tags': ['audio', 'quality']}
                ]
        
        if not addition_tasks:
            if is_chinese:
                addition_tasks = [
                    {'title': "添加转场效果", 'details': "在场景间插入平滑的转场以提升流畅度", 'tags': ['特效', '视觉']},
                    {'title': "插入背景音乐", 'details': "添加合适的音乐来增强氛围", 'tags': ['音频', '创意']},
                    {'title': "制作标题序列", 'details': "添加开头和结尾的标题卡片", 'tags': ['视觉', '创意']}
                ]
            else:
                addition_tasks = [
                    {'title': "Add transitions", 'details': "Insert smooth transitions between scenes for better flow", 'tags': ['effects', 'visual']},
                    {'title': "Insert background music", 'details': "Add appropriate music to enhance the mood", 'tags': ['audio', 'creative']},
                    {'title': "Create title sequence", 'details': "Add opening and closing title cards", 'tags': ['visual', 'creative']}
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
        
        # Add tags to task objects if available
        for i, task in enumerate(subtraction_tasks):
            if 'tags' in task and task['tags']:
                subtraction_task_objects[i]['tags'] = task['tags']
        
        for i, task in enumerate(addition_tasks):
            if 'tags' in task and task['tags']:
                addition_task_objects[i]['tags'] = task['tags']

        return VideoEditingOutput(
            title=title,
            subtractionTasks=subtraction_task_objects,
            additionTasks=addition_task_objects
        )
    
    def _create_fallback_video_editing_response(self, language: str) -> Dict[str, Any]:
        """Create fallback video editing response when API call fails."""
        # Determine if Chinese language
        is_chinese = language == 'zh'
        
        if is_chinese:
            fallback_subtraction = [
                VideoEditingTask(id="sub_1", title="移除不需要的片段", description="剪掉不必要或质量差的镜头", completed=False, tags=["剪辑", "质量"]),
                VideoEditingTask(id="sub_2", title="清除背景噪音", description="清理音频中的不需要声音", completed=False, tags=["音频", "质量"]),
                VideoEditingTask(id="sub_3", title="删除冗余内容", description="移除重复或过长的片段", completed=False, tags=["剪辑", "时机"])
            ]
            
            fallback_addition = [
                VideoEditingTask(id="add_1", title="添加转场效果", description="在场景间插入平滑的转场以提升流畅度", completed=False, tags=["特效", "视觉"]),
                VideoEditingTask(id="add_2", title="插入背景音乐", description="添加合适的音乐来增强氛围", completed=False, tags=["音频", "创意"]),
                VideoEditingTask(id="add_3", title="制作标题序列", description="添加开头和结尾的标题卡片", completed=False, tags=["视觉", "创意"])
            ]
        else:
            fallback_subtraction = [
                VideoEditingTask(id="sub_1", title="Remove unwanted footage", description="Cut out unnecessary or poor quality clips", completed=False, tags=["editing", "quality"]),
                VideoEditingTask(id="sub_2", title="Reduce background noise", description="Clean up audio by removing unwanted sounds", completed=False, tags=["audio", "quality"]),
                VideoEditingTask(id="sub_3", title="Trim excess content", description="Remove redundant or overly long segments", completed=False, tags=["editing", "timing"])
            ]
            
            fallback_addition = [
                VideoEditingTask(id="add_1", title="Add smooth transitions", description="Insert transitions between scenes for better flow", completed=False, tags=["effects", "visual"]),
                VideoEditingTask(id="add_2", title="Insert background music", description="Add appropriate music to enhance the mood", completed=False, tags=["audio", "creative"]),
                VideoEditingTask(id="add_3", title="Create title cards", description="Add opening and closing title sequences", completed=False, tags=["visual", "creative"])
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