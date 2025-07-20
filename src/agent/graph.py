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
# from langgraph.prebuilt import ToolNode  # Not needed anymore, using custom tool execution


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


async def get_weather_data(city: str) -> dict:
    """Get weather data for a specific city and return with UI component.
    
    Args:
        city: The name of the city to get weather for
        
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
        
        return {
            "result": f"Here's the current weather for {weather_data['city']}: {weather_data['temperature']}, {weather_data['condition']}. {weather_data['description']}",
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
        
        return {
            "result": f"Here's the weather for {fallback_weather['city']}: {fallback_weather['temperature']}, {fallback_weather['condition']}. {fallback_weather['description']}",
            "ui_components": [ui_component]
        }


async def get_todo_data(request: str) -> dict:
    """Create task plan data based on user request and return with UI component.
    
    Args:
        request: The user's request for task planning
        
    Returns:
        Dictionary with 'result' (text) and 'ui_components' (list of UI data)
    """
    # Initialize OpenAI client
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL_ID", "gpt-3.5-turbo"),
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create prompt for task planning
    planning_prompt = f"""
You are a helpful task planning assistant. Based on the user's request, create a detailed step-by-step plan.

User request: {request}

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

        todo_data = {
            "title": title,
            "tasks": tasks
        }
        
        # Create UI component data
        ui_component = {
            "type": "todo",
            "data": todo_data
        }
        
        return {
            "result": f"I've created a task plan titled '{title}' with {len(tasks)} actionable steps to help you achieve your goal.",
            "ui_components": [ui_component]
        }

    except Exception as e:
        # Fallback response if API call fails
        fallback_data = {
            "title": "Task Planning",
            "tasks": [
                "Break down the request into smaller steps",
                "Prioritize tasks by importance",
                "Execute tasks one by one",
                "Review and adjust as needed"
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


# Note: weather_node and todo_node functions have been removed as their functionality
# is now integrated into the call_model function with tool calling support


async def call_model(state: AgentState) -> dict[str, list[BaseMessage]]:
    """Main model calling function with tool support and UI component handling."""
    messages = state["messages"]
    
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
                "description": "Create a task planning list based on user request. This tool will display a todo UI component with organized tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "string",
                            "description": "The user's request for task planning or organization"
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
        content="""You are a helpful AI assistant with access to weather and task planning tools. 
        
Use the available tools when users ask for:
- Weather information (use get_weather_data)
- Task planning, scheduling, or organization help (use get_todo_data)

You can call multiple tools in a single response if the user's request requires it. For example, if someone asks "What's the weather like and how should I plan my day?", you can call both tools.
        
For general conversation that doesn't require these tools, respond directly in a friendly and helpful manner."""
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
                    # Execute the tool
                    if tool_name == "get_weather_data":
                        tool_result = await get_weather_data(tool_args["city"])
                    elif tool_name == "get_todo_data":
                        tool_result = await get_todo_data(tool_args["request"])
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
