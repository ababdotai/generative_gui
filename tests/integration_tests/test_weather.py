"""Integration tests for weather functionality."""

import os
import pytest
from unittest.mock import patch, AsyncMock

from agent.graph import weather, extract_city_with_openai, fetch_weather_data, format_weather_data
from langchain_core.messages import HumanMessage


@pytest.mark.asyncio
async def test_extract_city_with_openai():
    """Test city extraction using OpenAI API."""
    with patch('agent.graph.ChatOpenAI') as mock_llm_class:
        # Mock the LLM response
        mock_llm = AsyncMock()
        mock_response = AsyncMock()
        mock_response.content = "Beijing"
        mock_llm.ainvoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        # Test city extraction
        city = await extract_city_with_openai("What's the weather in Beijing?")
        assert city == "Beijing"
        
        # Verify the LLM was called correctly
        mock_llm.ainvoke.assert_called_once()
        call_args = mock_llm.ainvoke.call_args[0][0]
        assert len(call_args) == 1
        assert isinstance(call_args[0], HumanMessage)


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("WEATHER_API_KEY"),
    reason="WEATHER_API_KEY not set, skipping real API test"
)
async def test_fetch_weather_data():
    """Test weather data fetching from real WeatherAPI."""
    # Test with a well-known city
    city = "London"
    
    try:
        result = await fetch_weather_data(city)
        
        # Verify the response structure
        assert isinstance(result, dict)
        assert "current" in result
        assert "location" in result
        
        # Verify current weather data structure
        current = result["current"]
        assert "temp_f" in current
        assert "condition" in current
        assert "humidity" in current
        assert "wind_mph" in current
        
        # Verify condition structure
        condition = current["condition"]
        assert "text" in condition
        assert isinstance(condition["text"], str)
        
        # Verify location data
        location = result["location"]
        assert "name" in location
        assert "country" in location
        
        # Verify data types
        assert isinstance(current["temp_f"], (int, float))
        assert isinstance(current["humidity"], int)
        assert isinstance(current["wind_mph"], (int, float))
        
        print(f"Successfully fetched weather data for {city}: {current['condition']['text']}, {current['temp_f']}°F")
        
    except Exception as e:
        pytest.fail(f"Real API test failed: {str(e)}")


def test_format_weather_data():
    """Test weather data formatting."""
    mock_api_response = {
        "current": {
            "temp_f": 97.2,
            "condition": {
                "text": "Sunny"
            },
            "wind_mph": 4.7,
            "humidity": 45
        }
    }
    
    result = format_weather_data(mock_api_response, "Beijing")
    
    assert result["city"] == "Beijing"
    assert result["temperature"] == "97.2°F"
    assert result["condition"] == "Sunny"
    assert result["humidity"] == "45%"
    assert result["windSpeed"] == "4.7 mph"
    assert result["icon"] == "☀️"  # Should map sunny to sun icon
    assert "sunny" in result["description"].lower() or "clear" in result["description"].lower()


@pytest.mark.asyncio
async def test_weather_node_success():
    """Test the weather node with successful API calls."""
    from langgraph.config import RunnableConfig
    
    state = {
        "messages": [HumanMessage(content="What's the weather in Tokyo?")],
        "ui": []
    }
    
    config = RunnableConfig(configurable={})
    
    # Mock all the API calls
    with patch('agent.graph.extract_city_with_openai') as mock_extract, \
         patch('agent.graph.fetch_weather_data') as mock_fetch, \
         patch('agent.graph.format_weather_data') as mock_format:
        
        mock_extract.return_value = "Tokyo"
        mock_fetch.return_value = {"current": {"temp_f": 75}}
        mock_format.return_value = {
            "city": "Tokyo",
            "temperature": "75°F",
            "condition": "Clear",
            "humidity": "60%",
            "windSpeed": "5 mph",
            "icon": "☀️",
            "gradient": "linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)",
            "description": "Clear and sunny"
        }
        
        # Mock the push_ui_message function to avoid config issues
        with patch('agent.graph.push_ui_message') as mock_push:
            result = await weather(state)
            
            # Verify the result structure
            assert "messages" in result
            assert len(result["messages"]) == 1
            assert "Tokyo" in result["messages"][0].content
            assert "Clear" in result["messages"][0].content
            
            # Verify API calls were made
            mock_extract.assert_called_once_with("What's the weather in Tokyo?")
            mock_fetch.assert_called_once_with("Tokyo")
            mock_format.assert_called_once()
            mock_push.assert_called_once()


@pytest.mark.asyncio
async def test_weather_node_fallback():
    """Test the weather node fallback when API calls fail."""
    from langgraph.config import RunnableConfig
    
    state = {
        "messages": [HumanMessage(content="What's the weather?")],
        "ui": []
    }
    
    config = RunnableConfig(configurable={})
    
    # Mock API failure
    with patch('agent.graph.extract_city_with_openai', side_effect=Exception("API Error")), \
         patch('agent.graph.push_ui_message') as mock_push:
        result = await weather(state)
        
        # Verify fallback behavior
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert "unavailable" in result["messages"][0].content.lower()
        assert "San Francisco" in result["messages"][0].content
        mock_push.assert_called_once()