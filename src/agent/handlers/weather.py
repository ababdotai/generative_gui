"""Weather component handler."""

import os
from typing import Dict, Any, TypedDict

import httpx
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .base import BaseComponentHandler
from ..utils.language import format_response
from ..utils.response import create_component_response, create_ui_component


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


class WeatherHandler(BaseComponentHandler):
    """Handler for weather-related requests."""
    
    @property
    def component_type(self) -> str:
        """Return the component type identifier."""
        return "weather"
    
    async def process_request(self, request: str, language: str = 'en') -> Dict[str, Any]:
        """Process weather request and return response with UI components.
        
        Args:
            request: User's weather request
            language: Language code for response ('en', 'zh', 'ja')
            
        Returns:
            Dictionary with 'result' (text) and 'ui_components' (list of UI data)
        """
        try:
            # Extract city from request
            city = await self._extract_city_with_openai(request)
            
            # Fetch real weather data
            weather_response = await self._fetch_weather_data(city)
            weather_data = self._format_weather_data(weather_response, city, language)
            
            # Create UI component
            ui_component = create_ui_component(self.component_type, weather_data)
            
            # Generate response text
            result_text = format_response(
                'weather', language,
                city=weather_data['city'],
                temperature=weather_data['temperature'],
                condition=weather_data['condition'],
                description=weather_data['description']
            )
            
            return create_component_response(result_text, [ui_component])
            
        except Exception as e:
            # Fallback to mock data if API calls fail
            return await self._create_fallback_weather_response(request, language)
    
    async def _extract_city_with_openai(self, user_input: str) -> str:
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
    
    async def _fetch_weather_data(self, city: str) -> dict:
        """Fetch real weather data from WeatherAPI."""
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            raise ValueError("WEATHER_API_KEY not found in environment variables")
        
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
        
        # Create HTTP client
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    def _format_weather_data(self, weather_response: dict, city: str, language: str = 'en') -> WeatherOutput:
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
        
        # Weather condition descriptions in multiple languages
        weather_descriptions = {
            'rain': {
                'en': 'Rainy weather today',
                'zh': '今日有雨',
                'ja': '今日は雨です'
            },
            'cloud': {
                'en': 'Partly cloudy skies',
                'zh': '部分多云',
                'ja': '部分的に曇り'
            },
            'clear': {
                'en': 'Clear and sunny',
                'zh': '晴朗天气',
                'ja': '晴れて快晴'
            },
            'snow': {
                'en': 'Snowy conditions',
                'zh': '下雪天气',
                'ja': '雪の天気'
            },
            'default': {
                'en': 'Pleasant weather',
                'zh': '宜人天气',
                'ja': '快適な天気'
            }
        }
        
        # Map weather conditions to icons and gradients
        condition_lower = condition_text.lower()
        if "rain" in condition_lower or "drizzle" in condition_lower:
            icon = "🌧️"
            gradient = "linear-gradient(135deg, #636e72 0%, #2d3436 100%)"
            description = weather_descriptions['rain'].get(language, weather_descriptions['rain']['en'])
        elif "cloud" in condition_lower:
            icon = "⛅"
            gradient = "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)"
            description = weather_descriptions['cloud'].get(language, weather_descriptions['cloud']['en'])
        elif "sun" in condition_lower or "clear" in condition_lower:
            icon = "☀️"
            gradient = "linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)"
            description = weather_descriptions['clear'].get(language, weather_descriptions['clear']['en'])
        elif "snow" in condition_lower:
            icon = "❄️"
            gradient = "linear-gradient(135deg, #ddd6fe 0%, #a78bfa 100%)"
            description = weather_descriptions['snow'].get(language, weather_descriptions['snow']['en'])
        else:
            icon = "🌤️"
            gradient = "linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)"
            description = weather_descriptions['default'].get(language, weather_descriptions['default']['en'])
        
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
    
    async def _create_fallback_weather_response(self, request: str, language: str) -> Dict[str, Any]:
        """Create fallback weather response when API calls fail."""
        try:
            city = await self._extract_city_with_openai(request)
        except Exception:
            city = "San Francisco"
        
        # Fallback descriptions in multiple languages
        fallback_descriptions = {
            'en': 'Weather data unavailable, showing sample data',
            'zh': '天气数据不可用，显示示例数据',
            'ja': '天気データが利用できません、サンプルデータを表示'
        }
        
        # Create fallback weather data
        fallback_weather: WeatherOutput = {
            "city": city,
            "temperature": "72°F",
            "condition": "Partly Cloudy",
            "humidity": "65%",
            "windSpeed": "8 mph",
            "icon": "⛅",
            "gradient": "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
            "description": fallback_descriptions.get(language, fallback_descriptions['en'])
        }
        
        ui_component = create_ui_component(self.component_type, fallback_weather)
        
        # Generate fallback response text
        result_text = format_response(
            'weather_fallback', language,
            city=fallback_weather['city'],
            temperature=fallback_weather['temperature'],
            condition=fallback_weather['condition'],
            description=fallback_weather['description']
        )
        
        return create_component_response(result_text, [ui_component])