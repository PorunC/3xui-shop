# 3X-UI Shop 中文本地化

## 概述
此项目已添加完整的中文（简体）支持。用户的语言将根据其 Telegram 客户端设置自动检测。

## 支持的语言
- 🇬🇧 English (en)
- 🇷🇺 Русский (ru) 
- 🇨🇳 中文简体 (zh)

## 文件结构
```
app/locales/
├── en/LC_MESSAGES/
│   ├── bot.po    # 英文翻译源文件
│   └── bot.mo    # 编译后的英文翻译文件
├── ru/LC_MESSAGES/
│   ├── bot.po    # 俄文翻译源文件
│   └── bot.mo    # 编译后的俄文翻译文件
└── zh/LC_MESSAGES/
    ├── bot.po    # 中文翻译源文件
    └── bot.mo    # 编译后的中文翻译文件
```

## 如何工作
1. **自动检测**: 机器人会自动检测用户 Telegram 客户端的语言设置
2. **数据库存储**: 用户的语言偏好存储在 `users.language_code` 字段中
3. **动态切换**: 消息会根据用户的语言设置显示相应的翻译

## 开发说明

### 编译翻译文件
```bash
# 编译所有语言的翻译文件
poetry run pybabel compile -d app/locales -D bot

# 仅编译中文翻译
poetry run pybabel compile -d app/locales -l zh -D bot
```

### 更新翻译文件
如果添加了新的文本需要翻译：

1. 提取新的可翻译字符串：
```bash
poetry run pybabel extract -F babel.cfg -k _ -k __ -o messages.pot .
```

2. 更新现有翻译文件：
```bash
poetry run pybabel update -i messages.pot -d app/locales -D bot
```

3. 手动翻译新添加的字符串

4. 重新编译：
```bash
poetry run pybabel compile -d app/locales -D bot
```

### 添加新语言
要添加新语言支持：

1. 初始化新语言翻译文件：
```bash
poetry run pybabel init -i messages.pot -d app/locales -l <语言代码> -D bot
```

2. 翻译 `app/locales/<语言代码>/LC_MESSAGES/bot.po` 文件

3. 编译翻译文件：
```bash
poetry run pybabel compile -d app/locales -D bot
```

## 部署
Docker 容器启动时会自动编译所有翻译文件：
```yaml
command: sh -c " 
  poetry run pybabel compile -d /app/locales -D bot && 
  poetry run alembic -c /app/db/alembic.ini upgrade head && 
  poetry run python /app/__main__.py"
```

## 翻译覆盖率
- ✅ 主菜单界面
- ✅ 管理工具
- ✅ 订阅管理
- ✅ 个人资料
- ✅ 推荐系统
- ✅ 支持页面
- ✅ 支付系统
- ✅ 优惠码系统
- ✅ 服务器管理
- ✅ 通知系统
- ✅ 邀请链接管理
- ✅ 下载页面

## 注意事项
- 中文翻译文件使用简体中文
- 复数形式遵循中文语法规则（`nplurals=1; plural=0;`）
- HTML 标签和格式化代码保持不变
- 变量占位符（如 `{name}`, `{duration}` 等）保持原样
