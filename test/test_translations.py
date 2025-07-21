#!/usr/bin/env python3
"""
简单的翻译测试脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import gettext
import os

def test_translations():
    print("=== 翻译测试 ===\n")
    
    # 测试不同语言
    languages = ["en", "ru", "zh"]
    test_keys = [
        "main_menu:message:main",
        "admin_tools:message:main", 
        "subscription:button:buy",
        "profile:message:main",
        "support:message:main"
    ]
    
    locales_dir = project_root / "app/locales"
    
    for lang in languages:
        print(f"--- {lang.upper()} ---")
        
        try:
            # 设置语言环境
            lang_translation = gettext.translation(
                'bot', 
                localedir=str(locales_dir), 
                languages=[lang], 
                fallback=True
            )
            _ = lang_translation.gettext
            
            for key in test_keys:
                try:
                    translation = _(key).format(name="用户")
                    # 截断长文本以便显示
                    if len(translation) > 100:
                        translation = translation[:100] + "..."
                    print(f"{key}: {translation}")
                except Exception as e:
                    print(f"{key}: ERROR - {e}")
        except Exception as e:
            print(f"Language {lang} ERROR: {e}")
        print()

if __name__ == "__main__":
    test_translations()
