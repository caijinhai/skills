#!/bin/bash
# IndexTTS2 部署脚本（代理版）
# 用于下载模型、创建 conda 环境、安装依赖

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_DIR="${HOME}/miniconda3"
ENV_NAME="indextts2"
MODEL_DIR="${CONDA_DIR}/envs/${ENV_NAME}/checkpoints"

echo "🔧 IndexTTS2 部署脚本（代理加速版）"
echo "=================================="
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

# 使用代理安装 PyTorch
echo "📦 安装 PyTorch (通过代理)..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
echo "📦 安装其他依赖..."
pip install numpy scipy soundfile librosa
pip install transformers
pip install hydra-core omegaconf
pip install einops

# 克隆 IndexTTS2 仓库
echo ""
echo "📥 克隆 IndexTTS2 仓库..."
REPO_DIR="${SKILL_DIR}/index-tts"

if [ -d "${REPO_DIR}" ]; then
    echo "✅ 仓库已存在，更新中..."
    cd "${REPO_DIR}"
    git pull
else
    echo "正在克隆仓库..."
    git clone https://github.com/iszhanjiawei/indexTTS2.git "${REPO_DIR}"
fi

cd "${REPO_DIR}"

# 安装 IndexTTS2 包
echo ""
echo "📦 安装 IndexTTS2 Python 包..."
pip install -e .

# 创建模型目录
mkdir -p "${MODEL_DIR}"

echo ""
echo "📥 下载 IndexTTS2 模型文件..."

# 设置 HuggingFace 镜像（加速中国用户）
export HF_ENDPOINT="https://hf-mirror.com"

# 下载模型文件
MODEL_FILES=(
    "config.yaml"
    "bigvgan_discriminator.pth"
    "bigvgan_generator.pth"
    "bpe.model"
    "dvae.pth"
    "gpt.pth"
    "unigram_12000.vocab"
)

for file in "${MODEL_FILES[@]}"; do
    if [ -f "${MODEL_DIR}/${file}" ]; then
        echo "✅ 已存在：${file}"
    else
        echo "📥 下载：${file}"
        curl -L -o "${MODEL_DIR}/${file}" \
            "https://huggingface.co/IndexTeam/IndexTTS-1.5/resolve/main/${file}"
    fi
done

echo ""
echo "✅ 模型下载完成！"
echo "模型位置：${MODEL_DIR}"

# 创建测试脚本
echo ""
echo "📝 创建测试脚本..."

cat > "${SKILL_DIR}/test_indextts2.py" << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
IndexTTS2 真实模型测试脚本
"""

import os
import sys

# 添加 IndexTTS2 仓库到路径
REPO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index-tts")
sys.path.insert(0, REPO_DIR)

def test_indextts2():
    """
    测试 IndexTTS2 模型
    """
    print("🎤 IndexTTS2 真实模型测试")
    print("=" * 50)
    
    try:
        from indextts.infer_indextts2 import IndexTTS2
        
        skill_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.expanduser("~/miniconda3/envs/indextts2/checkpoints")
        
        print(f"📂 模型目录：{model_dir}")
        
        # 检查模型文件
        required_files = [
            "config.yaml",
            "gpt.pth",
            "dvae.pth",
            "bigvgan_generator.pth",
            "bigvgan_discriminator.pth",
            "bpe.model",
            "unigram_12000.vocab"
        ]
        
        for file in required_files:
            file_path = os.path.join(model_dir, file)
            if os.path.exists(file_path):
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} (缺失)")
        
        print("")
        print("🔄 初始化模型...")
        tts = IndexTTS2(
            cfg_path=os.path.join(model_dir, "config.yaml"),
            model_dir=model_dir,
            is_fp16=False,
            use_cuda_kernel=False
        )
        
        text = "这是一个有很好情感表现力的自回归 TTS 大模型，它还可以控制合成语音的时长。"
        output_path = os.path.join(skill_dir, "indextts2_output.wav")
        
        # 使用测试音频作为说话人参考
        test_audio = os.path.join(REPO_DIR, "test_data", "input.wav")
        if not os.path.exists(test_audio):
            print(f"⚠️  测试音频不存在：{test_audio}")
            print("   将使用默认说话人")
            test_audio = None
        
        print(f"📝 文本：{text}")
        print(f"🎵 合成中...")
        
        if test_audio:
            tts.infer(
                spk_audio_prompt=test_audio,
                text=text,
                output_path=output_path,
                verbose=True
            )
        else:
            tts.infer(
                text=text,
                output_path=output_path,
                verbose=True
            )
        
        print(f"✅ 语音合成成功！")
        print(f"📁 输出文件：{output_path}")
        
        # 显示文件信息
        import subprocess
        try:
            result = subprocess.run(
                ["ffprobe", "-hide_banner", output_path],
                capture_output=True, text=True
            )
            for line in result.stderr.split('\n'):
                if 'Duration' in line or 'Audio' in line or 'Stream' in line:
                    print(f"   {line.strip()}")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_indextts2()
    sys.exit(0 if success else 1)
PYTHON_EOF

chmod +x "${SKILL_DIR}/test_indextts2.py"

echo ""
echo "✅ 部署完成！"
echo ""
echo "使用方法:"
echo "  1. 激活环境：conda activate indextts2"
echo "  2. 运行测试：python ${SKILL_DIR}/test_indextts2.py"
echo "  3. 或使用 run.sh: ${SKILL_DIR}/run.sh \"你好，测试语音\""
echo ""
echo "📂 模型位置：${MODEL_DIR}"
echo "📂 代码位置：${REPO_DIR}"
