"""Todo component handler."""

import os
import re
from typing import Dict, Any, TypedDict, List

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .base import BaseComponentHandler
from ..utils.language import format_response
from ..utils.response import create_component_response, create_ui_component


class TodoOutput(TypedDict):
    """Todo output with task list."""

    title: str
    tasks: List[str]


class TodoHandler(BaseComponentHandler):
    """Handler for todo/task planning requests."""
    
    @property
    def component_type(self) -> str:
        """Return the component type identifier."""
        return "todo"
    
    async def process_request(self, request: str, language: str = 'en') -> Dict[str, Any]:
        """Process todo request and return response with UI components.
        
        Args:
            request: User's todo/task planning request
            language: Language code for response ('en', 'zh', 'ja')
            
        Returns:
            Dictionary with 'result' (text) and 'ui_components' (list of UI data)
        """
        try:
            # Generate task plan using OpenAI
            todo_data = await self._generate_task_plan(request)
            
            # Create UI component
            ui_component = create_ui_component(self.component_type, todo_data)
            
            # Generate response text
            result_text = format_response(
                'todo_success', language,
                title=todo_data['title'],
                count=len(todo_data['tasks'])
            )
            
            return create_component_response(result_text, [ui_component])
            
        except Exception as e:
            # Fallback response if API call fails
            return self._create_fallback_todo_response(language)
    
    async def _generate_task_plan(self, request: str) -> TodoOutput:
        """Generate task plan using OpenAI API."""
        # Initialize OpenAI client
        llm = ChatOpenAI(
            model=os.environ.get("OPENAI_MODEL_ID", "gpt-3.5-turbo"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Create prompt for task planning with optimized constraints
        planning_prompt = f"""
You are a helpful task planning assistant. Based on the user's request, create a concise and actionable plan.

User request: {request}

Please provide:
1. A clear, concise title for this plan (max 6 words)
2. A list of 3-5 high-level, actionable tasks in markdown bullet point format

Constraints:
- Keep tasks at a high level, not detailed sub-steps
- Each task should be a meaningful milestone
- Limit to 3-5 tasks maximum for better focus
- Make each task actionable and clear

Format your response as:
Title: [Your title here]

Tasks:
- Task 1
- Task 2
- Task 3
...

Make sure each task represents a significant step towards the goal.
IMPORTANT: You must respond in exactly the same language as the user's request.
"""

        # Call OpenAI API
        response = await llm.ainvoke([HumanMessage(content=planning_prompt)])
        ai_response = response.content

        # Parse the response to extract title and tasks
        title = "Task Plan"
        tasks = []

        if isinstance(ai_response, str):
            # Extract title
            title_match = re.search(r"Title:\s*(.+)", ai_response)
            if title_match:
                title = title_match.group(1).strip()

            # Extract tasks (bullet points)
            task_pattern = r"^\s*[-*]\s+(.+)$"
            for line in ai_response.split("\n"):
                match = re.match(task_pattern, line)
                if match:
                    tasks.append(match.group(1).strip())

        # Fallback if no tasks found
        if not tasks:
            tasks = ["Analyze requirements", "Create action plan", "Execute key steps", "Review progress"]

        return TodoOutput(
            title=title,
            tasks=tasks
        )
    
    def _create_fallback_todo_response(self, language: str) -> Dict[str, Any]:
        """Create fallback todo response when API call fails."""
        fallback_data = TodoOutput(
            title="General Plan",
            tasks=[
                "Analyze the request",
                "Plan your approach",
                "Take action",
                "Review results"
            ]
        )
        
        ui_component = create_ui_component(self.component_type, fallback_data)
        
        result_text = f"I've created a general task plan with {len(fallback_data['tasks'])} steps to help you get started."
        
        return create_component_response(result_text, [ui_component])