"""LangGraph Generative UI Agent.

A simple weather agent that demonstrates generative UI components.
"""

import os
import re
import uuid
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.ui import AnyUIMessage, push_ui_message, ui_message_reducer


class WeatherOutput(TypedDict):
    """Weather output with city information."""

    city: str


class TodoOutput(TypedDict):
    """Todo output with task list."""

    title: str
    tasks: list[str]


class AgentState(TypedDict):
    """Agent state with messages and UI components."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]


async def weather(state: AgentState) -> dict[str, list[AIMessage]]:
    """Weather node that generates UI components."""
    # For this demo, we'll extract city from the last user message
    # In a real implementation, you'd use structured output with ChatOpenAI
    last_message = state["messages"][-1] if state["messages"] else None
    user_input = last_message.content if last_message else ""

    # Ensure user_input is a string for processing
    if isinstance(user_input, list):
        user_input = " ".join(str(item) for item in user_input)
    user_input = str(user_input)

    # Simple city extraction (in real implementation, use structured output)
    city = "San Francisco"  # Default city
    if "london" in user_input.lower():
        city = "London"
    elif "new york" in user_input.lower():
        city = "New York"
    elif "tokyo" in user_input.lower():
        city = "Tokyo"

    weather_data: WeatherOutput = {"city": city}

    message = AIMessage(
        id=str(uuid.uuid4()), content=f"Here's the weather for {weather_data['city']}"
    )

    # Emit UI elements associated with the message
    push_ui_message("weather", dict(weather_data), message=message)

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
