/**
 * Central export file for all UI components
 * This file provides a single entry point for importing components
 * and makes it easy to add new components in the future
 */

import WeatherComponent from './WeatherComponent';
import TodoComponent from './TodoComponent';
import VideoEditingTodoComponent from './VideoEditingTodoComponent';

// Export individual components
export { WeatherComponent, TodoComponent, VideoEditingTodoComponent };

// Export types
export * from './types';

// Default export for component mapping (used by LangGraph)
export default {
  weather: WeatherComponent,
  todo: TodoComponent,
  videoEditingTodo: VideoEditingTodoComponent,
  WeatherComponent,
  TodoComponent,
  VideoEditingTodoComponent,
};