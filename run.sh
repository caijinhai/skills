#!/bin/bash
# IndexTTS2 运行脚本
# 用于将文本转换为语音

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_DIR="${HOME}/miniconda3"
ENV_NAME="indextts2"

# 检查环境
if [ ! -d "${CONDA_DIR}" ]; then
    echo "❌ 错误：未找到 miniconda3 在 ${CONDA_DIR}"
    exit 1
fi

# 检查环境是否已创建
if ! conda env list | grep -q "^${ENV_NAME} "; then
    echo "❌ 错误：Conda 环境 '${ENV_NAME}' 不存在"
    echo "请先运行部署脚本：bash ${SKILL_DIR}/deploy.sh"
    exit 1
fi

# 显示使用说明
if [ $# -eq 0 ]; then
    echo "IndexTTS2 文本转语音"
    echo "===================="
    echo ""
    echo "用法:"
    echo "  $0 \"要转换的文本\" [-o 输出文件] [-v 语音类型]"
    echo ""
    echo "示例:"
    echo "  $0 \"你好，这是测试语音\""
    echo "  $0 \"Hello World\" -o output.wav"
    echo "  $0 \"你好\" -v zh-CN"
    echo ""
    exit 0
fi

# 解析参数
TEXT=""
OUTPUT_FILE=""
VOICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -v|--voice)
            VOICE="$2"
            shift 2
            ;;
        *)
            if [ -z "$TEXT" ]; then
                TEXT="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$TEXT" ]; then
    echo "❌ 错误：请提供要转换的文本"
    exit 1
fi

# 设置默认输出文件
if [ -z "$OUTPUT_FILE" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT_FILE="${SKILL_DIR}/output_${TIMESTAMP}.wav"
fi

# 激活 conda 环境并运行
source "${CONDA_DIR}/etc/profile.d/conda.sh"
conda activate ${ENV_NAME}

echo "🎤 IndexTTS2 语音合成"
echo "===================="
echo "文本：${TEXT}"
echo "输出：${OUTPUT_FILE}"
echo ""

# 运行 Python 脚本
python3 "${SKILL_DIR}/tts_synth.py" "$TEXT" "$OUTPUT_FILE" "$VOICE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 语音合成成功！"
    echo "文件位置：${OUTPUT_FILE}"
    
    # 显示文件信息
    if command -v ffprobe &> /dev/null; then
        echo ""
        echo "音频信息:"
        ffprobe -hide_banner "$OUTPUT_FILE" 2>&1 | grep -E "(Duration|Audio|Stream)"
    fi
else
    echo ""
    echo "❌ 语音合成失败"
    exit 1
fi
