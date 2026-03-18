# deepseek-api-search

Call DeepSeek official API with configurable web search and deep thinking modes.

## Installation

This skill is already installed. To use it, you need to set your DeepSeek API key.

## Setup

1. Get your API key from: https://platform.deepseek.com/

2. Set the environment variable:
   ```bash
   export DEEPSEEK_API_KEY="your-api-key-here"
   ```

   Or create a file at `~/.deepseek_api_key` with your key.

## Usage

### Command Line

```bash
# Basic query (uses deepseek-chat by default)
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py "你的问题"

# With web search enabled
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --search "搜索科技新闻"

# Disable search
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --no-search "写一首诗"

# With deep thinking (uses deepseek-reasoner model)
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --thinking "解一道复杂的数学题"

# Show thinking process in output
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --show-thinking "分析这个问题"

# Use specific model
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --model deepseek-coder "写一个快速排序"

# Output as JSON
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --json "问题"

# Save to file
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py -o output.txt "问题"

# Quiet mode (only show final answer)
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --quiet --model deepseek-reasoner "问题"
```

### Options

| Option | Description |
|--------|-------------|
| `--search` | Enable web search |
| `--no-search` | Disable web search (default) |
| `--thinking` | Enable deep thinking mode (uses deepseek-reasoner) |
| `--no-thinking` | Disable deep thinking mode |
| `--model` | Model: `deepseek-chat`, `deepseek-coder`, `deepseek-reasoner`, `deepseek-r1` |
| `--temperature` | Temperature (0-2, default: 0.7) |
| `--max-tokens` | Maximum tokens in response |
| `--show-thinking` | Display the thinking/reasoning process |
| `--quiet` | Only show final answer (hide thinking process) |
| `--json` | Output raw JSON response |
| `-o, --output` | Save response to file |

## Models

| Model | Best For | Thinking Support |
|-------|----------|------------------|
| `deepseek-chat` | General conversation | No |
| `deepseek-coder` | Code generation | No |
| `deepseek-reasoner` | Complex reasoning, math, science | Yes |
| `deepseek-r1` | Advanced reasoning with thinking | Yes |

## Examples

```bash
# Search for latest AI news
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --search "最新的 AI 新闻"

# Get weather information
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --search "北京今天天气怎么样"

# Code generation without search
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --no-search "用 Python 写一个装饰器"

# Math problem with deep thinking
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --thinking "解方程：x^3 - 6x^2 + 11x - 6 = 0"

# Complex analysis with thinking and search
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py --model deepseek-r1 --search "分析量子计算对密码学的影响"
```

## API Reference

See [SKILL.md](SKILL.md) for full API documentation.
