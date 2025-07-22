"""LangGraph Generative UI Agent.

A true agent that uses LLM to decide between direct responses and tool calls.
Refactored with modular component architecture for better maintainability.
"""

import os
import uuid
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.graph.ui import AnyUIMessage, push_ui_message, ui_message_reducer, UIMessage

# Import modular components
from agent.utils.language import detect_language
from agent.handlers.registry import get_component_handler

class AgentState(TypedDict):
    """Agent state with messages and UI components."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]

async def call_model(state: AgentState) -> dict[str, list[BaseMessage]]:
    """Main model calling function with component handler support and UI component handling."""
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
    
    # Define available tools using component handlers
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
            # Process each tool call using component handlers
            tool_messages = []
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                try:
                    # Map tool names to component types and get handlers
                    component_type_map = {
                        "get_weather_data": "weather",
                        "get_todo_data": "todo", 
                        "get_video_editing_data": "video_editing"
                    }
                    
                    component_type = component_type_map.get(tool_name)
                    if component_type:
                        # Get the appropriate component handler
                        handler = get_component_handler(component_type)
                        if handler:
                            # Process request using the handler
                            if tool_name == "get_weather_data":
                                tool_result = await handler.process_request(tool_args["city"], user_language)
                            else:
                                tool_result = await handler.process_request(tool_args["request"], user_language)
                        else:
                            tool_result = {"result": f"Handler not found for {component_type}", "ui_components": []}
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
