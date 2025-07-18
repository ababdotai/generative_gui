import React, { useState, useEffect } from 'react';
import { TodoComponentProps } from './types';

/**
 * Todo component that displays a list of tasks with interactive checkboxes
 * @param props - Component props containing title and tasks array
 * @returns JSX element with todo card
 */
const TodoComponent: React.FC<TodoComponentProps> = ({ title, tasks }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [checkedTasks, setCheckedTasks] = useState<boolean[]>([]);

  useEffect(() => {
    // Trigger animation on mount
    setIsVisible(true);
    // Initialize all tasks as unchecked
    setCheckedTasks(new Array(tasks.length).fill(false));
  }, [tasks.length]);

  /**
   * Toggle the completion status of a task
   * @param index - Index of the task to toggle
   */
  const toggleTask = (index: number) => {
    const newCheckedTasks = [...checkedTasks];
    newCheckedTasks[index] = !newCheckedTasks[index];
    setCheckedTasks(newCheckedTasks);
  };

  const completedCount = checkedTasks.filter(Boolean).length;
  const progressPercentage = tasks.length > 0 ? (completedCount / tasks.length) * 100 : 0;

  return (
    <div className="todo-container">
      <div className={`todo-card ${isVisible ? 'visible' : ''}`}>
        {/* Header */}
        <div className="todo-header">
          <h2 className="todo-title">{title}</h2>
          <div className="todo-stats">
            <span className="progress-text">{completedCount}/{tasks.length} completed</span>
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
          {tasks.map((task, index) => (
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

      <style>{`
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

export default TodoComponent;