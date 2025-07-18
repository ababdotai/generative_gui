"""LangGraph Generative UI Agent.

A simple weather agent that demonstrates generative UI components.
"""

import os
import re
import uuid
import json
from typing import Annotated, Sequence, TypedDict

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.ui import AnyUIMessage, push_ui_message, ui_message_reducer


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


class AgentState(TypedDict):
    """Agent state with messages and UI components."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]


async def extract_city_with_openai(user_input: str) -> str:
    """Extract city name from user input using OpenAI API."""
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
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


async def weather(state: AgentState) -> dict[str, list[AIMessage]]:
    """Weather node that generates UI components with real weather data."""
    # Get user input from the last message
    last_message = state["messages"][-1] if state["messages"] else None
    user_input = last_message.content if last_message else ""

    # Ensure user_input is a string for processing
    if isinstance(user_input, list):
        user_input = " ".join(str(item) for item in user_input)
    user_input = str(user_input)

    try:
        # Extract city using OpenAI API
        city = await extract_city_with_openai(user_input)
        
        # Fetch real weather data
        weather_response = await fetch_weather_data(city)
        
        # Format the weather data for UI
        weather_data = format_weather_data(weather_response, city)
        
        message = AIMessage(
            id=str(uuid.uuid4()), 
            content=f"Here's the current weather for {city}: {weather_data['condition']}, {weather_data['temperature']}"
        )
        
        # Emit UI elements associated with the message
        push_ui_message("weather", dict(weather_data), message=message)
        
        return {"messages": [message]}
        
    except Exception as e:
        # Fallback to mock data if API calls fail
        city = "San Francisco"  # Default fallback
        
        # Create fallback weather data
        fallback_weather: WeatherOutput = {
            "city": city,
            "temperature": "72°F",
            "condition": "Partly Cloudy",
            "humidity": "65%",
            "windSpeed": "8 mph",
            "icon": "⛅",
            "gradient": "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
            "description": "Weather data unavailable, showing sample data"
        }
        
        message = AIMessage(
            id=str(uuid.uuid4()), 
            content=f"Weather service temporarily unavailable. Showing sample data for {city}. Error: {str(e)}"
        )
        
        push_ui_message("weather", dict(fallback_weather), message=message)
        return {"messages": [message]}


async def todo_planner(state: AgentState) -> dict[str, list[AIMessage]]:
    """Todo planner node that generates task lists using OpenAI."""
    # Get the last user message
    last_message = state["messages"][-1] if state["messages"] else None
    user_input = last_message.content if last_message else ""

    # Ensure user_input is a string for processing
    if isinstance(user_input, list):
        user_input = " ".join(str(item) for item in user_input)
    user_input = str(user_input)

    # Initialize OpenAI client
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create prompt for task planning
    planning_prompt = f"""
You are a helpful task planning assistant. Based on the user's request, create a detailed step-by-step plan.

User request: {user_input}

Please provide:
1. A clear title for this plan
2. A list of specific, actionable tasks in markdown bullet point format

Format your response as:
Title: [Your title here]

Tasks:
- Task 1
- Task 2
- Task 3
...

Make sure each task is specific and actionable.
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
            tasks = ["Review the request", "Plan the approach", "Execute the plan"]

        todo_data: TodoOutput = {
            "title": title,
            "tasks": tasks
        }

        message = AIMessage(
            id=str(uuid.uuid4()),
            content=f"I've created a task plan for: {title}"
        )

        # Emit UI elements associated with the message
        push_ui_message("todo", dict(todo_data), message=message)

        return {"messages": [message]}

    except Exception as e:
        # Fallback response if API call fails
        fallback_todo: TodoOutput = {
            "title": "Task Planning",
            "tasks": [
                "Break down the request into smaller steps",
                "Prioritize tasks by importance",
                "Execute tasks one by one",
                "Review and adjust as needed"
            ]
        }

        message = AIMessage(
            id=str(uuid.uuid4()),
            content=f"I've created a basic task plan (API unavailable: {str(e)})"
        )

        push_ui_message("todo", dict(fallback_todo), message=message)
        return {"messages": [message]}


async def route_request(state: AgentState) -> str:
    """Route requests to appropriate handler based on content."""
    last_message = state["messages"][-1] if state["messages"] else None
    user_input = last_message.content if last_message else ""
    
    # Ensure user_input is a string for processing
    if isinstance(user_input, list):
        user_input = " ".join(str(item) for item in user_input)
    user_input = str(user_input).lower()
    
    # Check for todo/task/plan related keywords
    todo_keywords = ["todo", "task", "plan", "steps", "organize", "schedule", "checklist"]
    weather_keywords = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy"]
    
    # Count keyword matches
    todo_score = sum(1 for keyword in todo_keywords if keyword in user_input)
    weather_score = sum(1 for keyword in weather_keywords if keyword in user_input)
    
    # Route based on keyword matches
    if todo_score > weather_score:
        return "todo_planner"
    else:
        return "weather"


# Define the graph
graph = (
    StateGraph(AgentState)
    .add_node("weather", weather)
    .add_node("todo_planner", todo_planner)
    .add_conditional_edges(
        "__start__",
        route_request,
        {
            "weather": "weather",
            "todo_planner": "todo_planner"
        }
    )
    .compile()
)
