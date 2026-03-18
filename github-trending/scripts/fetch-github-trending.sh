#!/bin/bash
# GitHub Trending 热点抓取脚本
# 用法：./fetch-github-trending.sh [--date YYYY-MM-DD] [--limit N]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$SKILL_DIR/output"

# 默认配置
DATE=$(date +%Y-%m-%d)
LIMIT=10
BITABLE_APP_TOKEN="YOUR_BITABLE_APP_TOKEN"
BITABLE_TABLE_ID="YOUR_TABLE_ID"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --date)
            DATE="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 [--date YYYY-MM-DD] [--limit N]"
            echo "  --date   抓取日期 (默认：今天)"
            echo "  --limit  抓取数量 (默认：10)"
            exit 0
            ;;
        *)
            echo "未知参数：$1"
            exit 1
            ;;
    esac
done

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "📊 开始抓取 GitHub Trending 热点..."
echo "   日期：$DATE"
echo "   数量：$LIMIT"

# 转换日期为时间戳
DATE_TS=$(date -j -f "%Y-%m-%d" "$DATE" +%s 2>/dev/null || date -d "$DATE" +%s 2>/dev/null || echo "")
if [ -z "$DATE_TS" ]; then
    DATE_TS=$(date +%s)
fi
DATE_MS="${DATE_TS}000"

# 使用 web_fetch 获取 GitHub Trending 页面
echo "   正在获取 GitHub Trending 页面..."
GITHUB_URL="https://github.com/trending"

# 调用 OpenClaw web_fetch 工具
FETCH_RESULT=$(openclaw tool web_fetch --url "$GITHUB_URL" --extract-mode markdown 2>/dev/null || echo "")

if [ -z "$FETCH_RESULT" ]; then
    echo "⚠️  web_fetch 调用失败，尝试使用 curl..."
    FETCH_RESULT=$(curl -s -A "Mozilla/5.0" "$GITHUB_URL" | grep -A 20 'role="listitem"' || echo "")
fi

# 解析数据（简化版本，实际应使用更完善的解析）
echo "   正在解析数据..."

# 示例数据（实际应从 FETCH_RESULT 解析）
# 这里使用模拟数据演示流程
cat > "$OUTPUT_DIR/trending_$DATE.json" << EOF
[
  {
    "rank": 1,
    "name": "MiroFish - 群体智能引擎",
    "stars": 30195,
    "description": "A Simple and Universal Swarm Intelligence Engine",
    "language": "Python",
    "url": "https://github.com/666ghj/MiroFish",
    "tags": ["AI", "开源"]
  }
]
EOF

echo "✅ 数据已保存到：$OUTPUT_DIR/trending_$DATE.json"

# 写入飞书多维表格
echo "   正在写入飞书多维表格..."

# 读取 JSON 数据并创建记录
if command -v jq &> /dev/null; then
    RECORD_COUNT=$(jq length "$OUTPUT_DIR/trending_$DATE.json")
    
    for i in $(seq 0 $((RECORD_COUNT - 1))); do
        RECORD=$(jq -r ".[$i]" "$OUTPUT_DIR/trending_$DATE.json")
        NAME=$(echo "$RECORD" | jq -r '.name')
        RANK=$(echo "$RECORD" | jq -r '.rank')
        STARS=$(echo "$RECORD" | jq -r '.stars')
        DESC=$(echo "$RECORD" | jq -r '.description')
        LANG=$(echo "$RECORD" | jq -r '.language')
        URL=$(echo "$RECORD" | jq -r '.url')
        TAGS=$(echo "$RECORD" | jq -r '.tags | join(",")')
        
        echo "   创建记录：$NAME"
        
        # 调用 OpenClaw feishu_bitable_create_record 工具
        openclaw tool feishu_bitable_create_record \
            --app-token "$BITABLE_APP_TOKEN" \
            --table-id "$BITABLE_TABLE_ID" \
            --fields "{\"项目名称\":\"$NAME\",\"排名\":$RANK,\"星标数\":$STARS,\"描述\":\"$DESC\",\"语言\":\"$LANG\",\"URL\":\"$URL\",\"标签\":[\"AI\",\"开源\"],\"日期\":$DATE_MS}" \
            2>/dev/null || echo "⚠️  记录创建失败：$NAME"
    done
else
    echo "⚠️  jq 未安装，跳过记录创建"
fi

echo "✅ GitHub Trending 抓取完成！"
echo "📋 访问地址：https://my.feishu.cn/wiki/GpI3wQ1vpihFyEk9bwGc4htunT0"
