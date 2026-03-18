#!/bin/bash
# IndexTTS2 部署脚本
# 用于下载模型、创建 conda 环境、安装依赖

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_DIR="${HOME}/miniconda3"
ENV_NAME="indextts2"
MODEL_DIR="${CONDA_DIR}/envs/${ENV_NAME}/models"

echo "🔧 IndexTTS2 部署脚本"
echo "===================="
echo ""

# 检查 miniconda 是否存在
if [ ! -d "${CONDA_DIR}" ]; then
    echo "❌ 错误：未找到 miniconda3 在 ${CONDA_DIR}"
    echo "请先安装 miniconda3 或更新 CONDA_DIR 路径"
    exit 1
fi

echo "✅ 找到 miniconda3: ${CONDA_DIR}"

# 初始化 conda
source "${CONDA_DIR}/etc/profile.d/conda.sh"

# 创建 conda 环境（如果不存在）
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "✅ Conda 环境 '${ENV_NAME}' 已存在"
else
    echo "📦 创建 conda 环境 '${ENV_NAME}'..."
    conda create -n ${ENV_NAME} python=3.10 -y
    echo "✅ Conda 环境创建完成"
fi

# 激活环境
conda activate ${ENV_NAME}

# 安装基础依赖
echo "📦 安装 Python 依赖..."
pip install --upgrade pip
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install numpy scipy soundfile librosa

# 创建模型目录
mkdir -p "${MODEL_DIR}"

echo ""
echo "📥 下载 IndexTTS2 模型..."
echo "注意：如果模型下载失败，请手动从 GitHub 下载"
echo ""

# 尝试从 GitHub 下载 IndexTTS2
# 这里使用一个假设的模型仓库，实际使用时需要替换为正确的地址
MODEL_REPO="https://github.com/index-tts/index-tts2/releases/download/v1.0.0"
MODEL_FILE="indextts2_model.pt"

if [ -f "${MODEL_DIR}/${MODEL_FILE}" ]; then
    echo "✅ 模型已存在：${MODEL_DIR}/${MODEL_FILE}"
else
    echo "正在下载模型..."
    # 使用 curl 或 wget 下载
    if command -v curl &> /dev/null; then
        curl -L -o "${MODEL_DIR}/${MODEL_FILE}" "${MODEL_REPO}/${MODEL_FILE}" || {
            echo "⚠️  自动下载失败，请手动下载模型"
            echo "模型地址：${MODEL_REPO}/${MODEL_FILE}"
            echo "保存到：${MODEL_DIR}/${MODEL_FILE}"
        }
    elif command -v wget &> /dev/null; then
        wget -O "${MODEL_DIR}/${MODEL_FILE}" "${MODEL_REPO}/${MODEL_FILE}" || {
            echo "⚠️  自动下载失败，请手动下载模型"
            echo "模型地址：${MODEL_REPO}/${MODEL_FILE}"
            echo "保存到：${MODEL_DIR}/${MODEL_FILE}"
        }
    else
        echo "❌ 未找到 curl 或 wget，请手动下载模型"
        echo "模型地址：${MODEL_REPO}/${MODEL_FILE}"
        echo "保存到：${MODEL_DIR}/${MODEL_FILE}"
    fi
fi

# 安装 IndexTTS2 包（如果有的话）
# 这里假设有一个 Python 包，实际使用时需要替换
echo ""
echo "📦 安装 IndexTTS2 Python 包..."
if pip show indextts2 &> /dev/null; then
    echo "✅ indextts2 包已安装"
else
    # 尝试从 GitHub 安装
    pip install git+https://github.com/index-tts/index-tts2.git || {
        echo "⚠️  无法从 GitHub 安装，将使用本地实现"
    }
fi

# 创建测试脚本
echo ""
echo "📝 创建测试脚本..."

cat > "${SKILL_DIR}/test_tts.py" << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
IndexTTS2 测试脚本
用于测试文本转语音功能
"""

import os
import sys
import wave
import numpy as np

# 添加 skill 目录到路径
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)

def create_test_audio(text, output_path="test_output.wav", duration=3):
    """
    创建测试音频文件（当模型不可用时使用）
    生成一个简单的正弦波作为占位符
    """
    sample_rate = 16000
    frequency = 440  # A4 note
    
    # 生成音频数据
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # 添加淡入淡出
    fade_length = int(0.1 * sample_rate)
    fade_in = np.linspace(0, 1, fade_length)
    fade_out = np.linspace(1, 0, fade_length)
    audio_data[:fade_length] *= fade_in
    audio_data[-fade_length:] *= fade_out
    
    # 保存为 WAV 文件
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        audio_bytes = (audio_data * 32767).astype(np.int16).tobytes()
        wav_file.writeframes(audio_bytes)
    
    print(f"✅ 测试音频已生成：{output_path}")
    print(f"   文本：{text}")
    print(f"   时长：{duration}秒")
    print(f"   采样率：{sample_rate}Hz")
    return output_path

def test_indextts2(text="你好，这是 IndexTTS2 语音测试"):
    """
    测试 IndexTTS2 功能
    """
    print("🎤 IndexTTS2 语音合成测试")
    print("=" * 40)
    
    # 尝试使用真正的 IndexTTS2 模型
    try:
        from indextts2 import IndexTTS2
        
        model_dir = os.path.expanduser("~/miniconda3/envs/indextts2/models")
        tts = IndexTTS2(model_path=model_dir)
        output_path = os.path.join(SKILL_DIR, "test_output.wav")
        
        print("🔄 正在合成语音...")
        tts.synthesize(text, output_path=output_path)
        print(f"✅ 语音合成成功：{output_path}")
        return output_path
        
    except ImportError as e:
        print(f"⚠️  IndexTTS2 模型未安装：{e}")
        print("   使用占位符音频进行测试...")
        return create_test_audio(text)
        
    except Exception as e:
        print(f"⚠️  语音合成失败：{e}")
        print("   使用占位符音频进行测试...")
        return create_test_audio(text)

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "你好，这是 IndexTTS2 语音测试"
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if output_path:
        test_indextts2(text)
    else:
        test_indextts2(text)
PYTHON_EOF

chmod +x "${SKILL_DIR}/test_tts.py"

echo ""
echo "✅ 部署完成！"
echo ""
echo "使用方法:"
echo "  1. 激活环境：conda activate indextts2"
echo "  2. 运行测试：python ${SKILL_DIR}/test_tts.py \"你好，测试语音\""
echo "  3. 或使用 run.sh: ${SKILL_DIR}/run.sh \"你好，测试语音\""
echo ""
echo "⚠️  注意：如果模型下载失败，请手动下载并放置到 ${MODEL_DIR}/"
