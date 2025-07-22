"""Language detection and response template utilities."""

import re
from typing import Dict, Any


def detect_language(text: str) -> str:
    """Detect the language of the input text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Language code: 'zh' for Chinese, 'ja' for Japanese, 'en' for English
    """
    # Japanese characters detection (Hiragana, Katakana) - check first
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return 'ja'
    
    # Chinese characters detection (CJK Unified Ideographs)
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh'
    
    # Default to English
    return 'en'


# Multi-language response templates
RESPONSE_TEMPLATES = {
    'weather': {
        'en': "Here's the current weather for {city}: {temperature}, {condition}. {description}",
        'zh': "这是{city}的当前天气：{temperature}，{condition}。{description}",
        'ja': "{city}の現在の天気：{temperature}、{condition}。{description}"
    },
    'weather_fallback': {
        'en': "Here's the weather information for {city}: {temperature}, {condition}. {description}",
        'zh': "这是{city}的天气信息：{temperature}，{condition}。{description}",
        'ja': "{city}の天気情報：{temperature}、{condition}。{description}"
    },
    'todo_success': {
        'en': "I've created a task plan titled '{title}' with {count} actionable steps to help you achieve your goal.",
        'zh': "我已经创建了一个名为'{title}'的任务计划，包含{count}个可执行步骤来帮助您实现目标。",
        'ja': "'{title}'というタスクプランを作成しました。目標達成のために{count}个の実行可能なステップが含まれています。"
    },
    'video_editing_success': {
        'en': "I've created a video editing plan titled '{title}' with {removal_count} removal tasks and {addition_count} addition tasks ({total_count} total tasks) to help you complete your video editing project.",
        'zh': "我已经创建了一个名为'{title}'的视频编辑计划，包含{removal_count}个移除任务和{addition_count}个添加任务（共{total_count}个任务）来帮助您完成视频编辑项目。",
        'ja': "'{title}'というビデオ編集プランを作成しました。{removal_count}個の削除タスクと{addition_count}個の追加タスク（合計{total_count}個のタスク）でビデオ編集プロジェクトの完成をサポートします。"
    },
    'video_editing_fallback': {
        'en': "I've created a general video editing plan with removal and addition tasks to help you with your video editing project.",
        'zh': "我已经创建了一个通用的视频编辑计划，包含移除和添加任务来帮助您的视频编辑项目。",
        'ja': "ビデオ編集プロジェクトをサポートするために、削除と追加のタスクを含む一般的なビデオ編集プランを作成しました。"
    }
}


def get_response_template(template_key: str, language: str = 'en') -> str:
    """Get response template for given key and language.
    
    Args:
        template_key: Template key from RESPONSE_TEMPLATES
        language: Language code ('en', 'zh', 'ja')
        
    Returns:
        Template string
    """
    return RESPONSE_TEMPLATES.get(template_key, {}).get(language, 
        RESPONSE_TEMPLATES.get(template_key, {}).get('en', ''))


def format_response(template_key: str, language: str, **kwargs) -> str:
    """Format response using template and provided arguments.
    
    Args:
        template_key: Template key from RESPONSE_TEMPLATES
        language: Language code ('en', 'zh', 'ja')
        **kwargs: Template formatting arguments
        
    Returns:
        Formatted response string
    """
    template = get_response_template(template_key, language)
    return template.format(**kwargs)