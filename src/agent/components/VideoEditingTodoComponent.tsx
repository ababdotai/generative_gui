import React, { useState, useEffect } from 'react';
import { VideoEditingTodoProps } from './types';
import { getAutoTranslations } from './i18n';

/**
 * Video editing todo component with side-by-side diff-like layout
 * Left side shows subtraction tasks (removing/processing), right side shows addition tasks (adding content)
 * @param props - Component props containing title and task arrays
 * @returns JSX element with video editing todo interface
 */
const VideoEditingTodoComponent: React.FC<VideoEditingTodoProps> = ({ 
  title, 
  subtractionTasks, 
  additionTasks 
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [subtractionChecked, setSubtractionChecked] = useState<boolean[]>([]);
  const [additionChecked, setAdditionChecked] = useState<boolean[]>([]);
  
  // Auto-detect language from title and get translations
  const t = getAutoTranslations(title);

  useEffect(() => {
    // Trigger animation on mount
    setIsVisible(true);
    // Initialize all tasks as unchecked
    setSubtractionChecked(new Array(subtractionTasks.length).fill(false));
    setAdditionChecked(new Array(additionTasks.length).fill(false));
  }, [subtractionTasks.length, additionTasks.length]);

  /**
   * Toggle the completion status of a subtraction task
   * @param index - Index of the task to toggle
   */
  const toggleSubtractionTask = (index: number) => {
    const newChecked = [...subtractionChecked];
    newChecked[index] = !newChecked[index];
    setSubtractionChecked(newChecked);
  };

  /**
   * Toggle the completion status of an addition task
   * @param index - Index of the task to toggle
   */
  const toggleAdditionTask = (index: number) => {
    const newChecked = [...additionChecked];
    newChecked[index] = !newChecked[index];
    setAdditionChecked(newChecked);
  };

  const subtractionCompleted = subtractionChecked.filter(Boolean).length;
  const additionCompleted = additionChecked.filter(Boolean).length;
  const totalTasks = subtractionTasks.length + additionTasks.length;
  const totalCompleted = subtractionCompleted + additionCompleted;
  const overallProgress = totalTasks > 0 ? (totalCompleted / totalTasks) * 100 : 0;

  return (
    <div className="video-editing-container">
      <div className={`video-editing-card ${isVisible ? 'visible' : ''}`}>
        {/* Header */}
        <div className="video-editing-header">
          <h2 className="video-editing-title">{title}</h2>
          <div className="video-editing-stats">
            <span className="progress-text">{totalCompleted}/{totalTasks} {t.completed}</span>
          </div>
        </div>

        {/* Overall Progress Bar */}
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${overallProgress}%` }}
            ></div>
          </div>
        </div>

        {/* Side-by-side Task Sections */}
        <div className="task-sections">
          {/* Subtraction Tasks (Left Side) */}
          <div className="task-section subtraction-section">
            <div className="section-header">
              <h3 className="section-title">
                <span className="section-icon">−</span>
                {t.subtractionTasks}
              </h3>
              <span className="section-progress">{subtractionCompleted}/{subtractionTasks.length}</span>
            </div>
            <div className="section-description">
              {t.subtractionDescription}
            </div>
            <div className="task-list">
              {subtractionTasks.map((task, index) => (
                <div 
                  key={task.id} 
                  className={`task-item subtraction-task ${subtractionChecked[index] ? 'completed' : ''}`}
                  onClick={() => toggleSubtractionTask(index)}
                >
                  <div className="task-checkbox">
                    <div className="checkbox-inner">
                      {subtractionChecked[index] && <span className="checkmark">✓</span>}
                    </div>
                  </div>
                  <div className="task-content">
                    <div className="task-title">{task.title}</div>
                    <div className="task-description">{task.details || task.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Addition Tasks (Right Side) */}
          <div className="task-section addition-section">
            <div className="section-header">
              <h3 className="section-title">
                <span className="section-icon">+</span>
                {t.additionTasks}
              </h3>
              <span className="section-progress">{additionCompleted}/{additionTasks.length}</span>
            </div>
            <div className="section-description">
              {t.additionDescription}
            </div>
            <div className="task-list">
              {additionTasks.map((task, index) => (
                <div 
                  key={task.id} 
                  className={`task-item addition-task ${additionChecked[index] ? 'completed' : ''}`}
                  onClick={() => toggleAdditionTask(index)}
                >
                  <div className="task-checkbox">
                    <div className="checkbox-inner">
                      {additionChecked[index] && <span className="checkmark">✓</span>}
                    </div>
                  </div>
                  <div className="task-content">
                    <div className="task-title">{task.title}</div>
                    <div className="task-description">{task.details || task.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="video-editing-footer">
          <div className="completion-badge">
            {overallProgress === 100 ? (
              <span className="badge-complete">{t.videoReady}</span>
            ) : (
              <span className="badge-progress">{t.editingInProgress}</span>
            )}
          </div>
        </div>
      </div>

      <style>{`
        .video-editing-container {
          display: flex;
          justify-content: center;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .video-editing-card {
          width: 900px;
          max-width: 95vw;
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          border-radius: 20px;
          padding: 30px;
          color: #2c3e50;
          box-shadow: 0 25px 50px rgba(0, 0, 0, 0.1);
          transform: translateY(50px);
          opacity: 0;
          transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          backdrop-filter: blur(10px);
          position: relative;
          overflow: hidden;
        }

        .video-editing-card.visible {
          transform: translateY(0);
          opacity: 1;
        }

        .video-editing-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 255, 255, 0.8);
          border-radius: 20px;
          backdrop-filter: blur(10px);
        }

        .video-editing-header {
          position: relative;
          z-index: 2;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 25px;
        }

        .video-editing-title {
          font-size: 28px;
          font-weight: 700;
          margin: 0;
          background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: slideInLeft 0.8s ease-out 0.3s both;
        }

        .video-editing-stats {
          animation: slideInRight 0.8s ease-out 0.3s both;
        }

        .progress-text {
          font-size: 14px;
          opacity: 0.9;
          background: rgba(52, 73, 94, 0.1);
          padding: 6px 12px;
          border-radius: 15px;
          font-weight: 500;
        }

        .progress-container {
          position: relative;
          z-index: 2;
          margin-bottom: 30px;
          animation: fadeInUp 0.8s ease-out 0.6s both;
        }

        .progress-bar {
          width: 100%;
          height: 10px;
          background: rgba(52, 73, 94, 0.1);
          border-radius: 5px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #ff6b6b 0%, #4ecdc4 100%);
          border-radius: 5px;
          transition: width 0.5s ease;
          animation: shimmer 2s infinite;
        }

        .task-sections {
          position: relative;
          z-index: 2;
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 25px;
          margin-bottom: 25px;
        }

        .task-section {
          border-radius: 15px;
          padding: 20px;
          animation: fadeInUp 0.8s ease-out both;
        }

        .subtraction-section {
          background: rgba(255, 107, 107, 0.15);
          border: 2px solid rgba(255, 107, 107, 0.4);
          animation-delay: 0.8s;
        }

        .addition-section {
          background: rgba(78, 205, 196, 0.15);
          border: 2px solid rgba(78, 205, 196, 0.4);
          animation-delay: 0.9s;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }

        .section-title {
          font-size: 18px;
          font-weight: 600;
          margin: 0;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .section-icon {
          font-size: 20px;
          font-weight: bold;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .subtraction-section .section-icon {
          background: rgba(255, 107, 107, 0.3);
          color: #e74c3c;
        }

        .addition-section .section-icon {
          background: rgba(78, 205, 196, 0.3);
          color: #16a085;
        }

        .section-progress {
          font-size: 12px;
          opacity: 0.8;
          background: rgba(52, 73, 94, 0.1);
          padding: 4px 8px;
          border-radius: 10px;
        }

        .section-description {
          font-size: 12px;
          opacity: 0.7;
          margin-bottom: 15px;
          line-height: 1.4;
        }

        .task-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .task-item {
          display: flex;
          align-items: flex-start;
          padding: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
          border-radius: 10px;
          animation: fadeInUp 0.6s ease-out both;
        }

        .task-item:nth-child(1) { animation-delay: 1.0s; }
        .task-item:nth-child(2) { animation-delay: 1.1s; }
        .task-item:nth-child(3) { animation-delay: 1.2s; }
        .task-item:nth-child(4) { animation-delay: 1.3s; }
        .task-item:nth-child(5) { animation-delay: 1.4s; }

        .subtraction-task:hover {
          background: rgba(255, 107, 107, 0.25);
        }

        .addition-task:hover {
          background: rgba(78, 205, 196, 0.25);
        }

        .task-item.completed .task-content {
          opacity: 0.6;
        }

        .task-item.completed .task-title {
          text-decoration: line-through;
        }

        .task-checkbox {
          width: 18px;
          height: 18px;
          border: 2px solid rgba(52, 73, 94, 0.4);
          border-radius: 50%;
          margin-right: 12px;
          margin-top: 2px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
          flex-shrink: 0;
        }

        .subtraction-task.completed .task-checkbox {
          background: #ff6b6b;
          border-color: #ff6b6b;
        }

        .addition-task.completed .task-checkbox {
          background: #4ecdc4;
          border-color: #4ecdc4;
        }

        .checkbox-inner {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .checkmark {
          font-size: 10px;
          font-weight: bold;
          animation: checkmarkPop 0.3s ease;
        }

        .task-content {
          flex: 1;
        }

        .task-title {
          font-size: 14px;
          font-weight: 500;
          margin-bottom: 4px;
          line-height: 1.3;
        }

        .task-description {
          font-size: 12px;
          opacity: 0.7;
          line-height: 1.4;
        }

        .video-editing-footer {
          position: relative;
          z-index: 2;
          display: flex;
          justify-content: center;
          animation: fadeInUp 0.8s ease-out 1.5s both;
        }

        .completion-badge {
          padding: 10px 20px;
          border-radius: 25px;
          background: rgba(52, 73, 94, 0.1);
          font-size: 16px;
          font-weight: 600;
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
        @media (max-width: 768px) {
          .video-editing-card {
            width: 100%;
            padding: 20px;
          }

          .task-sections {
            grid-template-columns: 1fr;
            gap: 20px;
          }

          .video-editing-title {
            font-size: 22px;
          }

          .section-title {
            font-size: 16px;
          }

          .task-title {
            font-size: 13px;
          }

          .task-description {
            font-size: 11px;
          }
        }
      `}</style>
    </div>
  );
};

export default VideoEditingTodoComponent;