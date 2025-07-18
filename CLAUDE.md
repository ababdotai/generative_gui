# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Installation
- `pip install -e . "langgraph-cli[inmem]"` - Install dependencies and LangGraph CLI
- `cp .env.example .env` - Copy environment template (add LANGSMITH_API_KEY if needed)

### Running the Application
- `langgraph dev` - Start LangGraph Server for development with hot reload

### Testing
- `make test` or `python -m pytest tests/unit_tests/` - Run unit tests
- `make integration_tests` or `python -m pytest tests/integration_tests/` - Run integration tests
- `make test_watch` - Run unit tests in watch mode
- `make test TEST_FILE=<path>` - Run specific test file

### Code Quality
- `make format` - Format code with ruff
- `make lint` - Run linters (ruff + mypy)
- `python -m ruff check .` - Check code style
- `python -m ruff format .` - Format code
- `python -m mypy --strict src/` - Type checking

## Architecture Overview

This is a **simple weather LangGraph agent** that demonstrates Generative UI components following the official LangGraph documentation tutorial.

### Core Components
- **Weather Agent**: `src/agent/graph.py` - Single-node weather graph that extracts cities and generates responses
- **UI Component**: `src/agent/ui.tsx` - Modern animated weather card component
- **State Management**: Uses LangChain message types (`HumanMessage`, `AIMessage`) with UI state

### Key Files
- `langgraph.json` - LangGraph server configuration with UI component definition
- `src/agent/graph.py` - Weather agent implementation with city detection and UI emission
- `src/agent/ui.tsx` - Weather card component with animations and city-specific styling
- `tests/integration_tests/` - Integration tests for weather functionality

### Implementation Details

#### Weather Agent Flow
1. **Input Processing**: Receives messages with user input about weather requests
2. **City Detection**: Simple keyword matching for cities (London, New York, Tokyo, San Francisco)
3. **Response Generation**: Creates AI message with weather information
4. **UI Emission**: Uses `push_ui_message("weather", {city: "CityName"}, message=message)` to emit weather card

#### Weather Card Features
- **Modern Design**: Glass morphism with city-specific gradient backgrounds
- **Smooth Animations**: Entrance animations, floating clouds, twinkling sparkles
- **Rich Content**: Temperature, weather conditions, humidity, wind speed
- **Responsive**: Adapts to mobile devices
- **City-Specific Styling**:
  - San Francisco: Blue ocean gradient (⛅ 72°F)
  - London: Gray stormy gradient (🌧️ 59°F)
  - New York: Sunny orange gradient (☀️ 68°F)
  - Tokyo: Pink sunset gradient (🌤️ 75°F)

#### Supported Cities
- **San Francisco** (default): "san francisco", "sf"
- **London**: "london"
- **New York**: "new york", "nyc"
- **Tokyo**: "tokyo"

#### Testing the Weather Agent
- Run `langgraph dev` and test through LangGraph Studio
- Try queries like:
  - "weather in london" → Shows London weather card
  - "new york weather" → Shows New York weather card
  - "tokyo weather please" → Shows Tokyo weather card
  - "hello" → Shows default San Francisco weather

### Extending the Weather Agent
- Add new cities by updating keyword detection in `weather()` function
- Modify weather data in `mockWeatherData` object in `ui.tsx`
- Add new weather conditions with different icons and gradients
- Extend animations by adding new keyframes in the component styles