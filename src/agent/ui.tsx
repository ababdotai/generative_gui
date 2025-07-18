/**
 * Main UI entry point for LangGraph Generative UI
 * This file imports and re-exports all UI components from the components directory
 * 
 * To add a new component:
 * 1. Create the component file in ./components/
 * 2. Add the component to ./components/index.ts
 * 3. The component will automatically be available here
 */

// Import all components from the components directory
import components from './components';

// Re-export components from the components directory
const { WeatherComponent, TodoComponent } = components;

// Export individual components for direct import
export { WeatherComponent, TodoComponent };

// Default export for LangGraph component mapping
export default components;