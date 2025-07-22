"""Integration tests for weather functionality."""

import os
import pytest
from unittest.mock import patch, AsyncMock

from agent.handlers.weather import WeatherHandler
from agent.handlers.registry import get_component_handler
from langchain_core.messages import HumanMessage


@pytest.mark.asyncio
async def test_extract_city_with_openai():
    """Test city extraction using OpenAI API through WeatherHandler."""
    handler = WeatherHandler()
    
    with patch('agent.handlers.weather.ChatOpenAI') as mock_llm_class:
        # Mock the LLM response
        mock_llm = AsyncMock()
        mock_response = AsyncMock()
        mock_response.content = "Beijing"
        mock_llm.ainvoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        # Test city extraction
        city = await handler._extract_city_with_openai("What's the weather in Beijing?")
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
    """Test weather data fetching from real WeatherAPI through WeatherHandler."""
    handler = WeatherHandler()
    # Test with a well-known city
    city = "London"
    
    try:
        result = await handler._fetch_weather_data(city)
        
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
    """Test weather data formatting through WeatherHandler."""
    handler = WeatherHandler()
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
    
    result = handler._format_weather_data(mock_api_response, "Beijing")
    
    assert result["city"] == "Beijing"
    assert result["temperature"] == "97.2°F"
    assert result["condition"] == "Sunny"
    assert result["humidity"] == "45%"
    assert result["windSpeed"] == "4.7 mph"
    assert result["icon"] == "☀️"  # Should map sunny to sun icon
    assert "sunny" in result["description"].lower() or "clear" in result["description"].lower()


@pytest.mark.asyncio
async def test_weather_handler_success():
    """Test the weather handler with successful API calls."""
    handler = WeatherHandler()
    
    # Mock all the API calls
    with patch.object(handler, '_extract_city_with_openai') as mock_extract, \
         patch.object(handler, '_fetch_weather_data') as mock_fetch, \
         patch.object(handler, '_format_weather_data') as mock_format:
        
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
        
        result = await handler.process_request("What's the weather in Tokyo?", "en")
        
        # Verify the result structure
        assert "result" in result
        assert "ui_components" in result
        assert "Tokyo" in result["result"]
        assert "Clear" in result["result"]
        
        # Verify API calls were made
        mock_extract.assert_called_once_with("What's the weather in Tokyo?")
        mock_fetch.assert_called_once_with("Tokyo")
        mock_format.assert_called_once()


@pytest.mark.asyncio
async def test_weather_handler_fallback():
    """Test the weather handler fallback when API calls fail."""
    handler = WeatherHandler()
    
    # Mock API failure
    with patch.object(handler, '_extract_city_with_openai', side_effect=Exception("API Error")):
        result = await handler.process_request("What's the weather?", "en")
        
        # Verify fallback behavior
        assert "result" in result
        assert "ui_components" in result
        assert "San Francisco" in result["result"]  # Default fallback city
        
        # Verify UI components were still created
        assert len(result["ui_components"]) > 0