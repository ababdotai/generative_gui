/**
 * Internationalization utilities for all UI components
 * Supports Chinese, English, and Japanese languages
 */

export type SupportedLanguage = 'zh' | 'en' | 'ja';

/**
 * Language detection based on text content
 * @param text - Input text to analyze
 * @returns Detected language code
 */
export const detectLanguage = (text: string): SupportedLanguage => {
  // Chinese characters (CJK Unified Ideographs)
  const chineseRegex = /[\u4e00-\u9fff]/;
  // Japanese characters (Hiragana, Katakana, Kanji)
  const japaneseRegex = /[\u3040-\u309f\u30a0-\u30ff]/;
  
  if (japaneseRegex.test(text)) {
    return 'ja';
  }
  if (chineseRegex.test(text)) {
    return 'zh';
  }
  return 'en'; // Default to English
};

/**
 * Translation strings for all components
 */
export const translations = {
  zh: {
    // Video editing component
    subtractionTasks: '素材选择计划',
    additionTasks: '效果添加计划',
    subtractionDescription: '环境分析、关键信息提取、冗余移除、素材预处理',
    additionDescription: '添加文字、音频、视觉效果、交互元素和最终合成',
    completed: '已完成',
    videoReady: '🎬 视频制作完成！',
    editingInProgress: '🎞️ 剪辑进行中',
    
    // Todo component
    allDone: '🎉 全部完成！',
    inProgress: '📝 进行中',
    
    // Weather component
    humidity: '湿度',
    wind: '风速'
  },
  en: {
    // Video editing component
    subtractionTasks: 'Subtraction Tasks',
    additionTasks: 'Addition Tasks',
    subtractionDescription: 'Environment analysis, key information extraction, redundancy removal, material preprocessing',
    additionDescription: 'Adding text, audio, visuals, interactions, and final composition',
    completed: 'completed',
    videoReady: '🎬 Video Ready!',
    editingInProgress: '🎞️ Editing in Progress',
    
    // Todo component
    allDone: '🎉 All Done!',
    inProgress: '📝 In Progress',
    
    // Weather component
    humidity: 'Humidity',
    wind: 'Wind'
  },
  ja: {
    // Video editing component
    subtractionTasks: '削減タスク',
    additionTasks: '追加タスク',
    subtractionDescription: '環境分析、重要情報抽出、冗長性除去、素材前処理',
    additionDescription: 'テキスト、音声、視覚効果、インタラクション要素、最終合成の追加',
    completed: '完了',
    videoReady: '🎬 動画完成！',
    editingInProgress: '🎞️ 編集中',
    
    // Todo component
    allDone: '🎉 完了！',
    inProgress: '📝 進行中',
    
    // Weather component
    humidity: '湿度',
    wind: '風速'
  }
};

/**
 * Get translations for a specific language
 * @param language - Target language code
 * @returns Translation object for the specified language
 */
export const getTranslations = (language: SupportedLanguage) => {
  return translations[language];
};

/**
 * Auto-detect language from title and return appropriate translations
 * @param title - Component title to analyze
 * @returns Translation object based on detected language
 */
export const getAutoTranslations = (title: string) => {
  const detectedLang = detectLanguage(title);
  return getTranslations(detectedLang);
};