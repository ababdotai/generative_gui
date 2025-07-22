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

This is a **sophisticated multi-agent LangGraph system** that demonstrates advanced Generative UI capabilities with modular component architecture. The system intelligently routes between multiple specialized handlers and generates rich, interactive UI components.

### Core Components
- **Multi-Agent Graph**: `src/agent/graph.py` - Intelligent routing system with LLM-powered decision making
- **Component Handlers**: Modular handlers for different request types (weather, todo, video editing)
- **UI Components**: Modern animated React components with TypeScript support
- **State Management**: Uses LangChain message types with UI state and component registry

### Key Files
- `langgraph.json` - LangGraph server configuration with UI component mapping
- `src/agent/graph.py` - Main agent graph with intelligent routing and component handling
- `src/agent/handlers/` - Modular component handlers (weather, todo, video_editing)
- `src/agent/components/` - React UI components with TypeScript definitions
- `src/agent/utils/` - Language detection and response formatting utilities
- `tests/` - Comprehensive unit and integration test suites

### Implementation Details

#### Multi-Agent System Flow
1. **Input Processing**: Receives user messages and detects language automatically
2. **Intelligent Routing**: LLM analyzes request and determines appropriate handler
3. **Component Processing**: Specialized handlers process requests and generate responses
4. **UI Generation**: Handlers create rich UI components with structured data
5. **Response Assembly**: System combines text responses with UI components

#### Component Handlers

##### Weather Handler (`weather.py`)
- **Real Weather Data**: Integrates with WeatherAPI for live weather information
- **City Detection**: OpenAI-powered city extraction from natural language
- **Rich Weather Cards**: Temperature, conditions, humidity, wind speed with city-specific styling
- **Fallback Support**: Graceful degradation when API is unavailable

##### Todo Handler (`todo.py`)
- **AI Task Planning**: OpenAI-powered task breakdown and planning
- **Interactive Lists**: Checkable todo items with progress tracking
- **Smart Categorization**: Automatic task organization and prioritization
- **Multi-language Support**: Responses in English, Chinese, and Japanese

##### Video Editing Handler (`video_editing.py`)
- **Specialized Workflow**: Dual-column layout for subtraction/addition tasks
- **Professional Features**: Video editing specific task categorization
- **Progress Tracking**: Separate completion tracking for different task types
- **Diff-like Interface**: Side-by-side task visualization

#### UI Components Architecture
- **TypeScript Support**: Full type safety with component props interfaces
- **Modular Design**: Each component is self-contained with its own styling
- **Animation System**: Smooth entrance animations and interactive feedback
- **Responsive Layout**: Mobile-first design with adaptive layouts

#### Testing the Multi-Agent System
- Run `langgraph dev` and test through LangGraph Studio
- Try different types of queries:
  - **Weather**: "weather in london", "what's the temperature in tokyo?"
  - **Todo Planning**: "help me plan a birthday party", "create a checklist for moving"
  - **Video Editing**: "help me edit a promotional video", "video editing workflow for social media"
  - **Multi-language**: Test in English, Chinese (中文), and Japanese (日本語)

### Extending the Multi-Agent System

#### Adding New Component Handlers
1. Create new handler in `src/agent/handlers/` extending `BaseComponentHandler`
2. Implement `process_request()` method and `component_type` property
3. Register handler in `src/agent/handlers/registry.py`
4. Create corresponding React component in `src/agent/components/`
5. Add component mapping in `src/agent/components/index.ts`

#### Customizing Existing Components
- **Weather**: Add new cities, integrate different weather APIs, customize styling
- **Todo**: Modify task generation prompts, add new task categories, enhance UI
- **Video Editing**: Add new task types, customize workflow templates, enhance progress tracking

#### Advanced Features
- **Multi-step Workflows**: Chain multiple handlers for complex tasks
- **Real-time Updates**: Implement WebSocket connections for live data
- **User Preferences**: Add user context and personalization
- **Analytics**: Track component usage and user interactions