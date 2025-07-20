# 3xui-shop 开发环境配置

本项目已配置为使用conda环境来解决Poetry与Anaconda Python的兼容性问题。

## 环境信息

- **Python版本**: 3.12.11 (conda)
- **环境名称**: `3xui-shop`
- **包管理**: Poetry + Conda

## 快速开始

### 方法1：使用环境管理脚本（推荐）

```bash
# 测试环境
./env.sh test

# 激活开发环境
./env.sh activate

# 直接运行应用
./env.sh run

# 安装/更新依赖
./env.sh install
```

### 方法2：手动操作

```bash
# 激活环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate 3xui-shop

# 进入项目目录
cd /home/misaka/web3/sales-bot/3xui-shop

# 运行应用
python -m app
```

### 方法3：使用运行脚本

```bash
# 直接运行（自动激活环境）
./run.sh
```

## 依赖管理

在conda环境中，Poetry能正常工作：

```bash
# 激活环境后
poetry install          # 安装依赖
poetry add <package>     # 添加新依赖
poetry remove <package>  # 移除依赖
poetry show             # 查看已安装包
```

## 环境重建

如果需要重建环境：

```bash
# 删除现有环境
conda remove --name 3xui-shop --all

# 重新创建环境
conda create -n 3xui-shop python=3.12
conda activate 3xui-shop
pip install poetry
poetry install
```

## 问题解决

### Poetry版本解析错误

如果遇到"failed to parse CPython sys.version"错误：
1. 使用上述conda环境方案
2. 或者使用系统Python而非Anaconda Python

### 环境激活失败

如果conda activate失败，首先运行：
```bash
conda init bash
# 然后重启终端
```
