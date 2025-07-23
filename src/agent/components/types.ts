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

/**
 * Video editing task item
 */
export interface VideoEditingTask {
  id: string;
  title: string;
  description: string;
  details?: string; // Optional detailed information for the task
  tags?: string[]; // Optional tags for categorization (1-3 tags)
  completed: boolean;
}

/**
 * Video editing todo component props
 */
export interface VideoEditingTodoProps {
  title: string;
  subtractionTasks: VideoEditingTask[];
  additionTasks: VideoEditingTask[];
}