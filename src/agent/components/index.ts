/**
 * Central export file for all UI components
 * This file provides a single entry point for importing components
 * and makes it easy to add new components in the future
 */

import WeatherComponent from './WeatherComponent';
import TodoComponent from './TodoComponent';

// Export individual components
export { WeatherComponent, TodoComponent };

// Export types
export * from './types';

// Default export for component mapping (used by LangGraph)
export default {
  weather: WeatherComponent,
  todo: TodoComponent,
  WeatherComponent,
  TodoComponent,
};