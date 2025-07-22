"""LangGraph Generative UI Agent.

A true agent that uses LLM to decide between direct responses and tool calls.
"""

import os
import re
import uuid
import json
from typing import Annotated, Sequence, TypedDict, Literal

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.graph.ui import AnyUIMessage, push_ui_message, ui_message_reducer, UIMessage

# Language detection function
def detect_language(text: str) -> str:
    """Detect the language of the input text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code: 'zh' for Chinese, 'ja' for Japanese, 'en' for English
    """
    # Japanese characters detection (Hiragana, Katakana) - check first
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return 'ja'
    
    # Chinese characters detection (CJK Unified Ideographs)
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    
    # Default to English
    return 'en'

# Multi-language response templates
RESPONSE_TEMPLATES = {
    'weather': {
        'en': "Here's the current weather for {city}: {temperature}, {condition}. {description}",
        'zh': "这是{city}的当前天气：{temperature}，{condition}。{description}",
        'ja': "{city}の現在の天気：{temperature}、{condition}。{description}"
    },
    'weather_fallback': {
        'en': "Here's the weather information for {city}: {temperature}, {condition}. {description}",
        'zh': "这是{city}的天气信息：{temperature}，{condition}。{description}",
        'ja': "{city}の天気情報：{temperature}、{condition}。{description}"
    },
    'todo_success': {
        'en': "I've created a task plan titled '{title}' with {count} actionable steps to help you achieve your goal.",
        'zh': "我已经创建了一个名为'{title}'的任务计划，包含{count}个可执行步骤来帮助您实现目标。",
        'ja': "'{title}'というタスクプランを作成しました。目標達成のために{count}個の実行可能なステップが含まれています。"
    },
    'video_editing_success': {
        'en': "I've created a video editing plan titled '{title}' with {removal_count} removal tasks and {addition_count} addition tasks ({total_count} total tasks) to help you complete your video editing project.",
        'zh': "我已经创建了一个名为'{title}'的视频编辑计划，包含{removal_count}个移除任务和{addition_count}个添加任务（共{total_count}个任务）来帮助您完成视频编辑项目。",
        'ja': "'{title}'というビデオ編集プランを作成しました。{removal_count}個の削除タスクと{addition_count}個の追加タスク（合計{total_count}個のタスク）でビデオ編集プロジェクトの完成をサポートします。"
    },
    'video_editing_fallback': {
        'en': "I've created a general video editing plan with removal and addition tasks to help you with your video editing project.",
        'zh': "我已经创建了一个通用的视频编辑计划，包含移除和添加任务来帮助您的视频编辑项目。",
        'ja': "ビデオ編集プロジェクトをサポートするために、削除と追加のタスクを含む一般的なビデオ編集プランを作成しました。"
    }
}

class WeatherOutput(TypedDict):
    """Weather output with comprehensive weather information."""

    city: str
    temperature: str
    condition: str
    humidity: str
    windSpeed: str
    icon: str
    gradient: str
    description: str


class TodoOutput(TypedDict):
    """Todo output with task list."""

    title: str
    tasks: list[str]


class VideoEditingTask(TypedDict):
    """Video editing task with details."""
    
    id: str
    title: str
    description: str
    completed: bool


class VideoEditingOutput(TypedDict):
    """Video editing output with subtraction and addition tasks."""
    
    title: str
    subtractionTasks: list[VideoEditingTask]
    additionTasks: list[VideoEditingTask]


class AgentState(TypedDict):
    """Agent state with messages and UI components."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]


async def extract_city_with_openai(user_input: str) -> str:
    """Extract city name from user input using OpenAI API."""
    try:
        llm = ChatOpenAI(
            model=os.environ.get("OPENAI_MODEL_ID", "gpt-3.5-turbo"),
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        extraction_prompt = f"""
Extract the city name from the following user input. If no city is mentioned, return "San Francisco" as default.
Only return the city name, nothing else.

User input: {user_input}

City:"""
        
        response = await llm.ainvoke([HumanMessage(content=extraction_prompt)])
        city = response.content.strip() if isinstance(response.content, str) else "San Francisco"
        return city
    except Exception:
        return "San Francisco"


async def fetch_weather_data(city: str) -> dict:
    """Fetch real weather data from WeatherAPI."""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("WEATHER_API_KEY not found in environment variables")
    
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    
    # Create client without proxy to avoid SOCKS proxy issues
    async with httpx.AsyncClient(proxies={}) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def format_weather_data(weather_response: dict, city: str) -> WeatherOutput:
    """Format weather API response into WeatherOutput format."""
    current = weather_response.get("current", {})
    condition = current.get("condition", {})
    
    # Convert temperature to Fahrenheit
    temp_f = current.get("temp_f", 70)
    temperature = f"{temp_f}°F"
    
    # Get condition text
    condition_text = condition.get("text", "Clear")
    
    # Get humidity and wind
    humidity = f"{current.get('humidity', 50)}%"
    wind_mph = current.get("wind_mph", 5)
    wind_speed = f"{wind_mph} mph"
    
    # Map weather conditions to icons and gradients
    condition_lower = condition_text.lower()
    if "rain" in condition_lower or "drizzle" in condition_lower:
        icon = "🌧️"
        gradient = "linear-gradient(135deg, #636e72 0%, #2d3436 100%)"
        description = "Rainy weather today"
    elif "cloud" in condition_lower:
        icon = "⛅"
        gradient = "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)"
        description = "Partly cloudy skies"
    elif "sun" in condition_lower or "clear" in condition_lower:
        icon = "☀️"
        gradient = "linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)"
        description = "Clear and sunny"
    elif "snow" in condition_lower:
        icon = "❄️"
        gradient = "linear-gradient(135deg, #ddd6fe 0%, #a78bfa 100%)"
        description = "Snowy conditions"
    else:
        icon = "🌤️"
        gradient = "linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)"
        description = "Pleasant weather"
    
    return WeatherOutput(
        city=city,
        temperature=temperature,
        condition=condition_text,
        humidity=humidity,
        windSpeed=wind_speed,
        icon=icon,
        gradient=gradient,
        description=description
    )


async def get_weather_data(city: str, language: str = 'en') -> dict:
    """Get weather data for a specific city and return with UI component.
    
    Args:
        city: The name of the city to get weather for
        language: Language code for response ('en', 'zh', 'ja')
        
    Returns:
        Dictionary with 'result' (text) and 'ui_components' (list of UI data)
    """
    try:
        # Fetch real weather data
        weather_response = await fetch_weather_data(city)
        weather_data = format_weather_data(weather_response, city)
        
        # Create UI component data
        ui_component = {
            "type": "weather",
            "data": weather_data
        }
        
        # Generate response in appropriate language
        template = RESPONSE_TEMPLATES['weather'][language]
        result_text = template.format(
            city=weather_data['city'],
            temperature=weather_data['temperature'],
            condition=weather_data['condition'],
            description=weather_data['description']
        )
        
        return {
            "result": result_text,
            "ui_components": [ui_component]
        }
        
    except Exception as e:
        # Fallback to mock data if API calls fail
        city_fallback = city or "San Francisco"
        
        # Create fallback weather data
        fallback_weather: WeatherOutput = {
            "city": city_fallback,
            "temperature": "72°F",
            "condition": "Partly Cloudy",
            "humidity": "65%",
            "windSpeed": "8 mph",
            "icon": "⛅",
            "gradient": "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
            "description": "Weather data unavailable, showing sample data"
        }
        
        ui_component = {
            "type": "weather",
            "data": fallback_weather
        }
        
        # Generate fallback response in appropriate language
        template = RESPONSE_TEMPLATES['weather_fallback'][language]
        result_text = template.format(
            city=fallback_weather['city'],
            temperature=fallback_weather['temperature'],
            condition=fallback_weather['condition'],
            description=fallback_weather['description']
        )
        
        return {
            "result": result_text,
            "ui_components": [ui_component]
        }


async def get_todo_data(request: str, language: str = 'en') -> dict:
    """Create task plan data based on user request and return with UI component.
    
    Args:
        request: The user's request that needs to be broken down into tasks
        language: Language code for response ('en', 'zh', 'ja')
        
    Returns:
        Dictionary with 'result' (text) and 'ui_components' (list of UI data)
    """
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

    try:
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

        todo_data = {
            "title": title,
            "tasks": tasks
        }
        
        # Create UI component data
        ui_component = {
            "type": "todo",
            "data": todo_data
        }
        
        # Generate response in appropriate language
        template = RESPONSE_TEMPLATES['todo_success'][language]
        result_text = template.format(
            title=title,
            count=len(tasks)
        )
        
        return {
            "result": result_text,
            "ui_components": [ui_component]
        }

    except Exception as e:
        # Fallback response if API call fails
        fallback_data = {
            "title": "General Plan",
            "tasks": [
                "Analyze the request",
                "Plan your approach",
                "Take action",
                "Review results"
            ]
        }
        
        ui_component = {
            "type": "todo",
            "data": fallback_data
        }
        
        return {
            "result": f"I've created a general task plan with {len(fallback_data['tasks'])} steps to help you get started.",
            "ui_components": [ui_component]
        }


async def get_video_editing_data(request: str, language: str = 'en') -> dict:
    """Create video editing task plan based on user request and return with UI component.
    
    Args:
        request: The user's video editing request
        language: Language code for response ('en', 'zh', 'ja')
        
    Returns:
        Dictionary with 'result' (text) and 'ui_components' (list of UI data)
    """
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
    "Remove task 1",
    "Cut task 2",
    "Delete task 3"
  ],
  "additionTasks": [
    "Add task 1",
    "Create task 2",
    "Enhance task 3"
  ]
}}

Requirements:
- Provide 2-4 subtraction tasks (removing unwanted elements)
- Provide 2-4 addition tasks (adding new elements or enhancements)
- Make each task specific and actionable for video editing
- Use the same language as the user's request for all text content
- Return ONLY the JSON object, no additional text or formatting
"""

    try:
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
                    subtraction_tasks = parsed_data.get('subtractionTasks', [])
                    addition_tasks = parsed_data.get('additionTasks', [])
                    
                    # Ensure tasks are strings
                    subtraction_tasks = [str(task) for task in subtraction_tasks if task]
                    addition_tasks = [str(task) for task in addition_tasks if task]
                    
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
                            subtraction_tasks.append(task_text)
                        elif task_text and current_section == "addition":
                            addition_tasks.append(task_text)

        # Fallback if no tasks found
        if not subtraction_tasks:
            subtraction_tasks = ["Remove unwanted footage", "Cut unnecessary scenes", "Delete background noise"]
        if not addition_tasks:
            addition_tasks = ["Add transitions", "Insert background music", "Create title sequence"]

        # Create task objects with IDs
        subtraction_task_objects = [
            {
                "id": f"sub_{i+1}",
                "title": task,
                "description": f"Remove or reduce: {task.lower()}",
                "completed": False
            }
            for i, task in enumerate(subtraction_tasks)
        ]
        
        addition_task_objects = [
            {
                "id": f"add_{i+1}",
                "title": task,
                "description": f"Add or enhance: {task.lower()}",
                "completed": False
            }
            for i, task in enumerate(addition_tasks)
        ]

        video_editing_data = {
            "title": title,
            "subtractionTasks": subtraction_task_objects,
            "additionTasks": addition_task_objects
        }
        
        # Create UI component data
        ui_component = {
            "type": "videoEditingTodo",
            "data": video_editing_data
        }
        
        total_tasks = len(subtraction_task_objects) + len(addition_task_objects)
        
        # Generate response in appropriate language
        template = RESPONSE_TEMPLATES['video_editing_success'][language]
        result_text = template.format(
            title=title,
            removal_count=len(subtraction_task_objects),
            addition_count=len(addition_task_objects),
            total_count=total_tasks
        )
        
        return {
            "result": result_text,
            "ui_components": [ui_component]
        }

    except Exception as e:
        # Fallback response if API call fails
        fallback_subtraction = [
            {"id": "sub_1", "title": "Remove unwanted footage", "description": "Cut out unnecessary or poor quality clips", "completed": False},
            {"id": "sub_2", "title": "Delete background noise", "description": "Clean up audio by removing unwanted sounds", "completed": False}
        ]
        
        fallback_addition = [
            {"id": "add_1", "title": "Add transitions", "description": "Insert smooth transitions between clips", "completed": False},
            {"id": "add_2", "title": "Insert background music", "description": "Add appropriate music to enhance the video", "completed": False}
        ]
        
        fallback_data = {
            "title": "Video Editing Project",
            "subtractionTasks": fallback_subtraction,
            "additionTasks": fallback_addition
        }
        
        ui_component = {
            "type": "videoEditingTodo",
            "data": fallback_data
        }
        
        # Generate fallback response in appropriate language
        template = RESPONSE_TEMPLATES['video_editing_fallback'][language]
        result_text = template
        
        return {
            "result": result_text,
            "ui_components": [ui_component]
        }


# Note: weather_node and todo_node functions have been removed as their functionality
# is now integrated into the call_model function with tool calling support


async def call_model(state: AgentState) -> dict[str, list[BaseMessage]]:
    """Main model calling function with tool support and UI component handling."""
    messages = state["messages"]
    
    # Detect language from the latest user message
    user_language = 'en'  # Default to English
    if messages:
        latest_message = messages[-1]
        if hasattr(latest_message, 'content') and latest_message.content:
            # Handle both string and list content types
            content = latest_message.content
            if isinstance(content, list):
                # If content is a list, extract text from the first text element
                text_content = ""
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_content = item.get('text', '')
                        break
                    elif isinstance(item, str):
                        text_content = item
                        break
                if text_content:
                    user_language = detect_language(text_content)
            elif isinstance(content, str):
                user_language = detect_language(content)
    
    # Define available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather_data",
                "description": "Get current weather information for a specific city. This tool will display a weather UI component with detailed weather data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The name of the city to get weather for"
                        }
                    },
                    "required": ["city"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_todo_data",
                "description": "Create a task planning list when users ask for help with planning, organizing, preparing, or need step-by-step guidance. Use this for requests about planning events, preparing for activities, organizing tasks, creating schedules, or breaking down complex goals. This tool will display a todo UI component with organized tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "string",
                            "description": "The user's request that needs to be broken down into actionable tasks or steps"
                        }
                    },
                    "required": ["request"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_video_editing_data",
                "description": "Create a video editing task plan when users ask for help with video editing, video production, or multimedia content creation. Use this for requests about editing videos, creating video content, post-production work, or video enhancement. This tool will display a specialized video editing UI component with subtraction (removal) and addition (enhancement) tasks organized in a Git diff-style layout.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "string",
                            "description": "The user's video editing request that needs to be broken down into removal and addition tasks"
                        }
                    },
                    "required": ["request"]
                }
            }
        }
    ]
    
    # Initialize LLM with tools
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL_ID", "gpt-3.5-turbo"),
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    ).bind_tools(tools)
    
    # Add system message for tool usage guidance
    system_message = SystemMessage(
        content="""You are a helpful AI assistant with access to weather, task planning, and video editing tools. 
        
Use the available tools when users ask for:
- Weather information (use get_weather_data): When users ask about weather, temperature, conditions in any city
- Task planning and organization (use get_todo_data): When users need help with:
  * Planning events, trips, activities, or projects
  * Preparing for interviews, meetings, exams, or presentations
  * Organizing tasks, schedules, or workflows
  * Breaking down complex goals into steps
  * Creating action plans or to-do lists
  * Getting guidance on how to approach something
- Video editing and production (use get_video_editing_data): When users need help with:
  * Video editing projects and post-production work
  * Creating or enhancing video content
  * Video production planning and workflow
  * Multimedia content creation
  * Film editing and video enhancement
  * YouTube video creation or social media video editing

Examples of when to use get_todo_data:
- "Help me prepare for a job interview"
- "I want to plan a birthday party"
- "How should I organize my study schedule?"
- "I need to start a business, where do I begin?"
- "Help me plan my weekend"

Examples of when to use get_video_editing_data:
- "Help me edit my vacation video"
- "I need to create a promotional video for my business"
- "How should I edit this interview footage?"
- "I want to make a YouTube video, what editing steps do I need?"
- "Help me improve the quality of my recorded presentation"
- "I need to edit a wedding video"

You can call multiple tools in a single response if needed. For general conversation that doesn't require planning, weather, or video editing, respond directly.
IMPORTANT: You must respond in exactly the same language as the user's request."""
    )
    
    # Prepare messages for the model
    model_messages = [system_message] + messages
    
    try:
        # Call the model
        response = await llm.ainvoke(model_messages)
        
        # Check if the model wants to use tools
        if response.tool_calls:
            # Process each tool call
            tool_messages = []
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                try:
                    # Execute the tool with language parameter
                    if tool_name == "get_weather_data":
                        tool_result = await get_weather_data(tool_args["city"], user_language)
                    elif tool_name == "get_todo_data":
                        tool_result = await get_todo_data(tool_args["request"], user_language)
                    elif tool_name == "get_video_editing_data":
                        tool_result = await get_video_editing_data(tool_args["request"], user_language)
                    else:
                        tool_result = {"result": f"Unknown tool: {tool_name}", "ui_components": []}
                    
                    # Create tool message
                    tool_message = ToolMessage(
                        content=tool_result["result"],
                        tool_call_id=tool_call_id
                    )
                    tool_messages.append(tool_message)
                    
                    # Process UI components using push_ui_message
                    for ui_component in tool_result.get("ui_components", []):
                        # Create an AIMessage for this UI component
                        ui_message = AIMessage(
                            id=str(uuid.uuid4()),
                            content=tool_result["result"]
                        )
                        
                        # Emit UI elements associated with the message
                        push_ui_message(
                            ui_component["type"],
                            ui_component["data"],
                            message=ui_message
                        )
                        tool_messages.append(ui_message)
                        
                except Exception as e:
                    # Handle tool execution errors
                    error_message = ToolMessage(
                        content=f"Error executing {tool_name}: {str(e)}",
                        tool_call_id=tool_call_id
                    )
                    tool_messages.append(error_message)

            # Return all messages (tool response and final response)
            return {"messages": [response] + tool_messages}
        
        else:
            # No tools called, return the direct response
            return {"messages": [response]}
            
    except Exception as e:
        # Fallback response on error
        error_response = AIMessage(
            id=str(uuid.uuid4()),
            content=f"I apologize, but I encountered an error while processing your request. Please try again. Error: {str(e)}"
        )
        return {"messages": [error_response]}


# Simplified graph with only call_model node
graph = (
    StateGraph(AgentState)
    .add_node("call_model", call_model)
    .add_edge("__start__", "call_model")
    .add_edge("call_model", END)
    .compile()
)
