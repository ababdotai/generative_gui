import React, { useState, useEffect } from 'react';

// Mock weather data for different cities
const mockWeatherData = {
  'San Francisco': {
    temperature: '72°F',
    condition: 'Partly Cloudy',
    humidity: '65%',
    windSpeed: '8 mph',
    icon: '⛅',
    gradient: 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)',
    description: 'A beautiful day with some clouds'
  },
  'London': {
    temperature: '59°F', 
    condition: 'Rainy',
    humidity: '82%',
    windSpeed: '12 mph',
    icon: '🌧️',
    gradient: 'linear-gradient(135deg, #636e72 0%, #2d3436 100%)',
    description: 'Light rain throughout the day'
  },
  'New York': {
    temperature: '68°F',
    condition: 'Sunny',
    humidity: '58%', 
    windSpeed: '6 mph',
    icon: '☀️',
    gradient: 'linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)',
    description: 'Clear skies and sunshine'
  },
  'Tokyo': {
    temperature: '75°F',
    condition: 'Partly Sunny',
    humidity: '70%',
    windSpeed: '5 mph', 
    icon: '🌤️',
    gradient: 'linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)',
    description: 'Warm with occasional clouds'
  }
};

const WeatherComponent = (props: { city: string }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [weatherData, setWeatherData] = useState(mockWeatherData['San Francisco']);

  useEffect(() => {
    // Trigger animation on mount
    setIsVisible(true);
    
    // Get weather data for the specified city
    const cityData = mockWeatherData[props.city as keyof typeof mockWeatherData];
    if (cityData) {
      setWeatherData(cityData);
    }
  }, [props.city]);

  return (
    <div className="weather-container">
      <div 
        className={`weather-card ${isVisible ? 'visible' : ''}`}
        style={{ background: weatherData.gradient }}
      >
        {/* Header */}
        <div className="weather-header">
          <h2 className="city-name">{props.city}</h2>
          <div className="weather-icon">{weatherData.icon}</div>
        </div>

        {/* Main Temperature */}
        <div className="temperature-section">
          <div className="temperature">{weatherData.temperature}</div>
          <div className="condition">{weatherData.condition}</div>
          <div className="description">{weatherData.description}</div>
        </div>

        {/* Weather Details */}
        <div className="weather-details">
          <div className="detail-item">
            <div className="detail-icon">💧</div>
            <div className="detail-info">
              <span className="detail-label">Humidity</span>
              <span className="detail-value">{weatherData.humidity}</span>
            </div>
          </div>
          
          <div className="detail-item">
            <div className="detail-icon">💨</div>
            <div className="detail-info">
              <span className="detail-label">Wind</span>
              <span className="detail-value">{weatherData.windSpeed}</span>
            </div>
          </div>
        </div>

        {/* Animated Background Elements */}
        <div className="bg-animation">
          <div className="cloud cloud-1">☁️</div>
          <div className="cloud cloud-2">☁️</div>
          <div className="sparkle sparkle-1">✨</div>
          <div className="sparkle sparkle-2">✨</div>
          <div className="sparkle sparkle-3">✨</div>
        </div>
      </div>

      <style jsx>{`
        .weather-container {
          display: flex;
          justify-content: center;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .weather-card {
          position: relative;
          width: 350px;
          height: 450px;
          border-radius: 25px;
          padding: 30px;
          color: white;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
          overflow: hidden;
          transform: translateY(50px);
          opacity: 0;
          transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          backdrop-filter: blur(10px);
        }

        .weather-card.visible {
          transform: translateY(0);
          opacity: 1;
        }

        .weather-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 25px;
          backdrop-filter: blur(10px);
        }

        .weather-header {
          position: relative;
          z-index: 2;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 40px;
        }

        .city-name {
          font-size: 28px;
          font-weight: 300;
          margin: 0;
          letter-spacing: 1px;
          animation: slideInLeft 0.8s ease-out 0.3s both;
        }

        .weather-icon {
          font-size: 60px;
          animation: bounce 2s infinite, slideInRight 0.8s ease-out 0.3s both;
        }

        .temperature-section {
          position: relative;
          z-index: 2;
          text-align: center;
          margin: 60px 0;
        }

        .temperature {
          font-size: 72px;
          font-weight: 100;
          margin: 0;
          line-height: 1;
          animation: scaleIn 1s ease-out 0.6s both;
          text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        .condition {
          font-size: 22px;
          font-weight: 300;
          margin: 10px 0 5px 0;
          opacity: 0.9;
          animation: fadeInUp 0.8s ease-out 0.9s both;
        }

        .description {
          font-size: 16px;
          opacity: 0.8;
          font-weight: 300;
          animation: fadeInUp 0.8s ease-out 1.1s both;
        }

        .weather-details {
          position: relative;
          z-index: 2;
          display: flex;
          justify-content: space-around;
          margin-top: 50px;
        }

        .detail-item {
          display: flex;
          align-items: center;
          gap: 12px;
          animation: fadeInUp 0.8s ease-out 1.3s both;
        }

        .detail-icon {
          font-size: 24px;
          animation: pulse 2s infinite;
        }

        .detail-info {
          display: flex;
          flex-direction: column;
        }

        .detail-label {
          font-size: 14px;
          opacity: 0.8;
          font-weight: 300;
        }

        .detail-value {
          font-size: 18px;
          font-weight: 500;
        }

        /* Background Animations */
        .bg-animation {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
          overflow: hidden;
        }

        .cloud {
          position: absolute;
          font-size: 30px;
          opacity: 0.3;
          animation: float 6s ease-in-out infinite;
        }

        .cloud-1 {
          top: 15%;
          left: 10%;
          animation-delay: 0s;
        }

        .cloud-2 {
          top: 25%;
          right: 15%;
          animation-delay: 3s;
        }

        .sparkle {
          position: absolute;
          font-size: 16px;
          opacity: 0.6;
          animation: twinkle 3s ease-in-out infinite;
        }

        .sparkle-1 {
          top: 30%;
          left: 20%;
          animation-delay: 0s;
        }

        .sparkle-2 {
          top: 60%;
          right: 25%;
          animation-delay: 1s;
        }

        .sparkle-3 {
          bottom: 25%;
          left: 15%;
          animation-delay: 2s;
        }

        /* Keyframe Animations */
        @keyframes slideInLeft {
          from {
            transform: translateX(-50px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        @keyframes slideInRight {
          from {
            transform: translateX(50px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        @keyframes scaleIn {
          from {
            transform: scale(0.5);
            opacity: 0;
          }
          to {
            transform: scale(1);
            opacity: 1;
          }
        }

        @keyframes fadeInUp {
          from {
            transform: translateY(30px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-10px);
          }
          60% {
            transform: translateY(-5px);
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-20px);
          }
        }

        @keyframes twinkle {
          0%, 100% {
            opacity: 0.6;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.2);
          }
        }

        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.1);
          }
        }

        /* Responsive Design */
        @media (max-width: 480px) {
          .weather-card {
            width: 300px;
            height: 400px;
            padding: 25px;
          }

          .temperature {
            font-size: 60px;
          }

          .city-name {
            font-size: 24px;
          }

          .weather-icon {
            font-size: 50px;
          }
        }
      `}</style>
    </div>
  );
};

const TodoComponent = (props: { title: string; tasks: string[] }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [checkedTasks, setCheckedTasks] = useState<boolean[]>([]);

  useEffect(() => {
    // Trigger animation on mount
    setIsVisible(true);
    // Initialize all tasks as unchecked
    setCheckedTasks(new Array(props.tasks.length).fill(false));
  }, [props.tasks.length]);

  const toggleTask = (index: number) => {
    const newCheckedTasks = [...checkedTasks];
    newCheckedTasks[index] = !newCheckedTasks[index];
    setCheckedTasks(newCheckedTasks);
  };

  const completedCount = checkedTasks.filter(Boolean).length;
  const progressPercentage = props.tasks.length > 0 ? (completedCount / props.tasks.length) * 100 : 0;

  return (
    <div className="todo-container">
      <div className={`todo-card ${isVisible ? 'visible' : ''}`}>
        {/* Header */}
        <div className="todo-header">
          <h2 className="todo-title">{props.title}</h2>
          <div className="todo-stats">
            <span className="progress-text">{completedCount}/{props.tasks.length} completed</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Task List */}
        <div className="task-list">
          {props.tasks.map((task, index) => (
            <div 
              key={index} 
              className={`task-item ${checkedTasks[index] ? 'completed' : ''}`}
              onClick={() => toggleTask(index)}
            >
              <div className="task-checkbox">
                <div className="checkbox-inner">
                  {checkedTasks[index] && <span className="checkmark">✓</span>}
                </div>
              </div>
              <span className="task-text">{task}</span>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="todo-footer">
          <div className="completion-badge">
            {progressPercentage === 100 ? (
              <span className="badge-complete">🎉 All Done!</span>
            ) : (
              <span className="badge-progress">📝 In Progress</span>
            )}
          </div>
        </div>
      </div>

      <style jsx>{`
        .todo-container {
          display: flex;
          justify-content: center;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .todo-card {
          width: 400px;
          max-width: 90vw;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 20px;
          padding: 25px;
          color: white;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
          transform: translateY(50px);
          opacity: 0;
          transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          backdrop-filter: blur(10px);
          position: relative;
          overflow: hidden;
        }

        .todo-card.visible {
          transform: translateY(0);
          opacity: 1;
        }

        .todo-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 20px;
          backdrop-filter: blur(10px);
        }

        .todo-header {
          position: relative;
          z-index: 2;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .todo-title {
          font-size: 24px;
          font-weight: 600;
          margin: 0;
          animation: slideInLeft 0.8s ease-out 0.3s both;
        }

        .todo-stats {
          animation: slideInRight 0.8s ease-out 0.3s both;
        }

        .progress-text {
          font-size: 14px;
          opacity: 0.9;
          background: rgba(255, 255, 255, 0.2);
          padding: 4px 8px;
          border-radius: 12px;
        }

        .progress-container {
          position: relative;
          z-index: 2;
          margin-bottom: 25px;
          animation: fadeInUp 0.8s ease-out 0.6s both;
        }

        .progress-bar {
          width: 100%;
          height: 8px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
          border-radius: 4px;
          transition: width 0.5s ease;
          animation: shimmer 2s infinite;
        }

        .task-list {
          position: relative;
          z-index: 2;
          margin-bottom: 20px;
        }

        .task-item {
          display: flex;
          align-items: center;
          padding: 12px 0;
          cursor: pointer;
          transition: all 0.3s ease;
          animation: fadeInUp 0.6s ease-out both;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .task-item:nth-child(1) { animation-delay: 0.8s; }
        .task-item:nth-child(2) { animation-delay: 0.9s; }
        .task-item:nth-child(3) { animation-delay: 1.0s; }
        .task-item:nth-child(4) { animation-delay: 1.1s; }
        .task-item:nth-child(5) { animation-delay: 1.2s; }

        .task-item:hover {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding-left: 8px;
          padding-right: 8px;
        }

        .task-item.completed .task-text {
          text-decoration: line-through;
          opacity: 0.6;
        }

        .task-checkbox {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255, 255, 255, 0.5);
          border-radius: 50%;
          margin-right: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
        }

        .task-item.completed .task-checkbox {
          background: #4facfe;
          border-color: #4facfe;
        }

        .checkbox-inner {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .checkmark {
          font-size: 12px;
          font-weight: bold;
          animation: checkmarkPop 0.3s ease;
        }

        .task-text {
          flex: 1;
          font-size: 16px;
          line-height: 1.4;
        }

        .todo-footer {
          position: relative;
          z-index: 2;
          display: flex;
          justify-content: center;
          animation: fadeInUp 0.8s ease-out 1.3s both;
        }

        .completion-badge {
          padding: 8px 16px;
          border-radius: 20px;
          background: rgba(255, 255, 255, 0.2);
          font-size: 14px;
          font-weight: 500;
        }

        .badge-complete {
          animation: bounce 1s ease infinite;
        }

        /* Keyframe Animations */
        @keyframes slideInLeft {
          from {
            transform: translateX(-50px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        @keyframes slideInRight {
          from {
            transform: translateX(50px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        @keyframes fadeInUp {
          from {
            transform: translateY(30px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes checkmarkPop {
          0% {
            transform: scale(0);
          }
          50% {
            transform: scale(1.2);
          }
          100% {
            transform: scale(1);
          }
        }

        @keyframes shimmer {
          0% {
            background-position: -200px 0;
          }
          100% {
            background-position: calc(200px + 100%) 0;
          }
        }

        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
          }
          40% {
            transform: translateY(-5px);
          }
          60% {
            transform: translateY(-3px);
          }
        }

        /* Responsive Design */
        @media (max-width: 480px) {
          .todo-card {
            width: 350px;
            padding: 20px;
          }

          .todo-title {
            font-size: 20px;
          }

          .task-text {
            font-size: 14px;
          }
        }
      `}</style>
    </div>
  );
};

export default {
  weather: WeatherComponent,
  todo: TodoComponent,
};