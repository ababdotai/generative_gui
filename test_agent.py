#!/usr/bin/env python3
"""Test script for the new LangGraph Agent."""

import asyncio
import sys
sys.path.append('./src')

from agent.graph import graph
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

async def test_agent():
    """Test the agent with various inputs."""
    
    test_cases = [
        "Can you check the weather in Tokyo?",
        "Help me plan a project to learn Python",
        "Create a todo list for organizing my study schedule", 
        "Hello, how are you today?",
        "I need to organize my study schedule"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n=== Test {i}: {test_input} ===")
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=test_input)],
            "ui": [],
            "next_action": ""  # Initialize next_action field
        }
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        # Print results
        print(f"Messages: {len(result['messages'])}")
        print(f"UI Components: {len(result['ui'])}")
        
        # Print the final response
        if result['messages']:
            last_message = result['messages'][-1]
            if hasattr(last_message, 'content'):
                print(f"Response: {last_message.content}")
        
        # Print UI components
        for ui_component in result['ui']:
            print(f"UI Component: {ui_component.get('name', 'unknown')}")
        
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(test_agent())