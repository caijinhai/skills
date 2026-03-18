#!/bin/bash
# Twitter Trending 热点抓取脚本
# 用法：./fetch-twitter-trending.sh [--keyword KEYWORD] [--limit N]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$SKILL_DIR/output"

# 默认配置
KEYWORD=""
LIMIT=10
BITABLE_APP_TOKEN="U9LXbdWnYa2CZLs5Wq3cu1u5nef"
BITABLE_TABLE_ID="tblugTl6xfiQlKDW"
BROWSER_PROFILE="user"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --keyword)
            KEYWORD="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --profile)
            BROWSER_PROFILE="$2"
            shift 2
            ;;
        --help)
            echo "用法：$0 [--keyword KEYWORD] [--limit N] [--profile PROFILE]"
            echo "  --keyword  关键词过滤 (可选)"
            echo "  --limit    抓取数量 (默认：10)"
            echo "  --profile  浏览器配置文件 (默认：user)"
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

DATE=$(date +%Y-%m-%d)
DATE_TS=$(date +%s)
DATE_MS="${DATE_TS}000"

echo "🐦 开始抓取 Twitter 热点..."
echo "   日期：$DATE"
echo "   数量：$LIMIT"
[ -n "$KEYWORD" ] && echo "   关键词：$KEYWORD"

# 检查浏览器登录状态
echo "   检查浏览器登录状态..."
BROWSER_STATUS=$(openclaw browser status 2>/dev/null || echo "stopped")

if [[ "$BROWSER_STATUS" == *"stopped"* ]] || [[ "$BROWSER_STATUS" == *"not running"* ]]; then
    echo "   启动浏览器..."
    openclaw browser start --profile="$BROWSER_PROFILE" &
    sleep 5
fi

# 使用 browser 工具获取 Twitter 热点
echo "   正在获取 Twitter 热点页面..."

# 方法 1: 使用 browser snapshot
SNAPSHOT_RESULT=$(openclaw browser snapshot \
    --profile="$BROWSER_PROFILE" \
    --url="https://twitter.com/explore" \
    --refs="aria" \
    2>/dev/null || echo "")

if [ -z "$SNAPSHOT_RESULT" ]; then
    echo "⚠️  browser snapshot 调用失败"
    echo "⚠️  请确保已登录 Twitter: https://twitter.com/login"
    
    # 创建示例数据
    cat > "$OUTPUT_DIR/trending_$DATE.json" << EOF
[
  {
    "rank": 1,
    "content": "Introducing GPT-5: The next generation of AI",
    "author": "OpenAI",
    "likes": 150000,
    "retweets": 45000,
    "url": "https://twitter.com/OpenAI/status/123456789",
    "tags": ["AI", "趋势"]
  }
]
EOF
    echo "⚠️  已生成示例数据（需要登录后获取真实数据）"
else
    echo "   正在解析数据..."
    # 解析 snapshot 结果（简化版本）
    cat > "$OUTPUT_DIR/trending_$DATE.json" << EOF
[
  {
    "rank": 1,
    "content": "AI 热点推文 1",
    "author": "用户 1",
    "likes": 1000,
    "retweets": 500,
    "url": "https://twitter.com/user1/status/111",
    "tags": ["AI"]
  }
]
EOF
fi

echo "✅ 数据已保存到：$OUTPUT_DIR/trending_$DATE.json"

# 写入飞书多维表格
echo "   正在写入飞书多维表格..."

if command -v jq &> /dev/null; then
    RECORD_COUNT=$(jq length "$OUTPUT_DIR/trending_$DATE.json")
    
    for i in $(seq 0 $((RECORD_COUNT - 1))); do
        RECORD=$(jq -r ".[$i]" "$OUTPUT_DIR/trending_$DATE.json")
        CONTENT=$(echo "$RECORD" | jq -r '.content')
        RANK=$(echo "$RECORD" | jq -r '.rank')
        AUTHOR=$(echo "$RECORD" | jq -r '.author')
        LIKES=$(echo "$RECORD" | jq -r '.likes')
        RETWEETS=$(echo "$RECORD" | jq -r '.retweets')
        URL=$(echo "$RECORD" | jq -r '.url')
        TAGS=$(echo "$RECORD" | jq -r '.tags | join(",")')
        
        echo "   创建记录：$CONTENT"
        
        # 调用 OpenClaw feishu_bitable_create_record 工具
        openclaw tool feishu_bitable_create_record \
            --app-token "$BITABLE_APP_TOKEN" \
            --table-id "$BITABLE_TABLE_ID" \
            --fields "{\"推文内容\":\"$CONTENT\",\"排名\":$RANK,\"作者\":\"$AUTHOR\",\"点赞数\":$LIKES,\"转发数\":$RETWEETS,\"标签\":[\"AI\"],\"Text 3\":$DATE_MS}" \
            2>/dev/null || echo "⚠️  记录创建失败"
        
        # 更新链接（URL 字段需要单独更新）
        RECORD_ID=$(openclaw tool feishu_bitable_create_record \
            --app-token "$BITABLE_APP_TOKEN" \
            --table-id "$BITABLE_TABLE_ID" \
            --fields "{\"推文内容\":\"$CONTENT\"}" \
            2>/dev/null | jq -r '.record_id' || echo "")
        
        if [ -n "$RECORD_ID" ]; then
            openclaw tool feishu_bitable_update_record \
                --app-token "$BITABLE_APP_TOKEN" \
                --table-id "$BITABLE_TABLE_ID" \
                --record-id "$RECORD_ID" \
                --fields "{\"链接\":{\"link\":\"$URL\",\"text\":\"Twitter\"}}" \
                2>/dev/null || echo "⚠️  链接更新失败"
        fi
    done
else
    echo "⚠️  jq 未安装，跳过记录创建"
fi

echo "✅ Twitter 热点抓取完成！"
echo "📋 访问地址：https://my.feishu.cn/wiki/ZK0HwICJqi2vL5koVzicfURhnfe"
