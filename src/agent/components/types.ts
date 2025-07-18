/**
 * Type definitions for UI components
 */

// Weather component props
export interface WeatherComponentProps {
  city: string;
  temperature: string;
  condition: string;
  humidity: string;
  windSpeed: string;
  icon: string;
  gradient: string;
  description: string;
}

// Todo component props
export interface TodoComponentProps {
  title: string;
  tasks: string[];
}

/**
 * Task item for todo component
 */
export interface TaskItem {
  id: string;
  text: string;
  completed: boolean;
}