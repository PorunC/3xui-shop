#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# 激活conda环境并运行3xui-shop
echo "Activating 3xui-shop conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate 3xui-shop

echo "Environment activated. Changing to project directory..."
cd "$SCRIPT_DIR"

echo "Running 3xui-shop..."
python -m app

# 如果直接运行这个脚本，保持环境激活
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "To keep using this environment, run:"
    echo "  source ~/miniconda3/etc/profile.d/conda.sh"
    echo "  conda activate 3xui-shop"
    echo "  cd $SCRIPT_DIR"
fi
