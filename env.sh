#!/bin/bash

# 3xui-shop 开发环境管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ENV_NAME="3xui-shop"

case "$1" in
    "activate"|"")
        echo "激活 $ENV_NAME 环境..."
        source ~/miniconda3/etc/profile.d/conda.sh
        conda activate $ENV_NAME
        cd "$SCRIPT_DIR"
        echo "环境已激活，当前目录: $SCRIPT_DIR"
        echo "可用命令："
        echo "  poetry install          - 安装/更新依赖"
        echo "  python -m app          - 运行应用"
        echo "  ./run.sh               - 直接运行应用"
        echo "  ./env.sh test          - 测试环境"
        exec bash
        ;;
    "test")
        echo "测试环境..."
        source ~/miniconda3/etc/profile.d/conda.sh
        conda activate $ENV_NAME
        cd "$SCRIPT_DIR"
        python -c "import app; print('✅ 项目导入成功')"
        python -c "import sys; print(f'✅ Python版本: {sys.version}')"
        python -c "import aiogram; print(f'✅ AioGram版本: {aiogram.__version__}')"
        ;;
    "run")
        echo "运行应用..."
        ./run.sh
        ;;
    "install")
        echo "安装依赖..."
        source ~/miniconda3/etc/profile.d/conda.sh
        conda activate $ENV_NAME
        cd "$SCRIPT_DIR"
        poetry install
        ;;
    "help")
        echo "3xui-shop 环境管理脚本"
        echo ""
        echo "用法: ./env.sh [命令]"
        echo ""
        echo "命令："
        echo "  activate, (无参数)  激活开发环境"
        echo "  test               测试环境是否正常"
        echo "  run                运行应用"
        echo "  install            安装/更新依赖"
        echo "  help               显示此帮助"
        ;;
    *)
        echo "未知命令: $1"
        echo "使用 './env.sh help' 查看帮助"
        exit 1
        ;;
esac
