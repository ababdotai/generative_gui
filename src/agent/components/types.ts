/**
 * Type definitions for UI components
 */

// Weather component props
export interface WeatherComponentProps {
  city: string;
}

// Todo component props
export interface TodoComponentProps {
  title: string;
  tasks: string[];
}

// Weather data structure
export interface WeatherData {
  temperature: string;
  condition: string;
  humidity: string;
  windSpeed: string;
  icon: string;
  gradient: string;
  description: string;
}

// Mock weather data type
export type MockWeatherData = {
  [key: string]: WeatherData;
};

// Task item for todo component
export interface TaskItem {
  id: string;
  text: string;
  completed: boolean;
}