---
name: deepseek-api-search
description:
  Call DeepSeek official API with configurable web search and deep thinking
  modes. Use this skill whenever the user needs to search the web, perform
  complex reasoning, or get real-time data with thinking process visibility.
  Supports deepseek-chat, deepseek-coder, and deepseek-reasoner models.
license: MIT
metadata:
  author: user
  version: '2.0.0'
---

# DeepSeek API with Search and Deep Thinking

This skill enables calling DeepSeek's official API with configurable web search
and deep thinking (reasoning) functionality. It supports all DeepSeek models
including `deepseek-chat`, `deepseek-coder`, and `deepseek-reasoner` (R1), with
the ability to enable web search for real-time information retrieval and deep
thinking for complex reasoning tasks with visible thought processes.

## When to Use

Use this skill when:
- User asks to search the web for information
- Need real-time or current event data
- User wants to verify facts or find sources
- Looking up documentation, news, or recent information
- Complex reasoning tasks requiring step-by-step thinking
- Math, science, or logic problems that benefit from deep thinking
- Any task requiring internet search or reasoning capabilities

## Configuration Options

This skill supports two main configurable features:

| Option | Parameter | Default | Description |
|--------|-----------|---------|-------------|
| **Web Search** | `enable_search` | `false` | Enable web search for real-time information |
| **Deep Thinking** | `enable_thinking` | `true` | Enable deep reasoning mode (R1 models) |

### Model Selection

| Model | Best For | Thinking Support |
|-------|----------|------------------|
| `deepseek-chat` | General conversation | No |
| `deepseek-coder` | Code generation | No |
| `deepseek-reasoner` | Complex reasoning, math, science | Yes |
| `deepseek-r1` | Advanced reasoning with thinking | Yes |

**Note:** Deep thinking mode is only available with `deepseek-reasoner` and `deepseek-r1` models.

## API Endpoints

### Base URL
```
https://api.deepseek.com
```

### Chat Completions Endpoint
```
POST https://api.deepseek.com/v1/chat/completions
```

## Authentication

Set the `Authorization` header with your API key:
```
Authorization: Bearer YOUR_DEEPSEEK_API_KEY
```

Get your API key from: https://platform.deepseek.com/

## Request Format

### Basic Request
```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  "stream": false
}
```

### Request with Search Enabled
```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "user",
      "content": "What's the latest news about AI?"
    }
  ],
  "enable_search": true,
  "stream": false
}
```

### Request with Deep Thinking (Reasoning)
```json
{
  "model": "deepseek-reasoner",
  "messages": [
    {
      "role": "user",
      "content": "Solve this math problem: ..."
    }
  ],
  "stream": false
}
```

### Request with Both Search and Thinking
```json
{
  "model": "deepseek-r1",
  "messages": [
    {
      "role": "user",
      "content": "Research and analyze the impact of quantum computing on cryptography"
    }
  ],
  "enable_search": true,
  "stream": false
}
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID: `deepseek-chat`, `deepseek-coder`, `deepseek-reasoner`, `deepseek-r1` |
| `messages` | array | Yes | Array of message objects |
| `enable_search` | boolean | No | Enable web search (default: false) |
| `stream` | boolean | No | Enable streaming response |
| `temperature` | number | No | Sampling temperature (0-2) |
| `max_tokens` | integer | No | Max tokens in response |
| `top_p` | number | No | Nucleus sampling parameter |

**Note:** Deep thinking is automatically enabled when using `deepseek-reasoner` or `deepseek-r1` models.

### Message Format

```json
{
  "role": "user",
  "content": "Your question here"
}
```

Supported roles: `system`, `user`, `assistant`

## Response Format

### Standard Response
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response content here"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### Response with Search Results
When `enable_search: true`, the response may include search quotes in the content.

### Response with Deep Thinking (Reasoning Models)
When using `deepseek-reasoner` or `deepseek-r1`, the response includes a thinking process:

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "model": "deepseek-reasoner",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Final answer here",
        "reasoning_content": "Step-by-step thinking process..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 500,
    "total_tokens": 520,
    "prompt_tokens_details": {
      "cached_tokens": 0
    }
  }
}
```

The `reasoning_content` field contains the model's deep thinking process before the final answer.

## Usage Examples

### Example 1: Simple Query
```bash
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Example 2: With Search Enabled
```bash
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "What happened in the tech industry this week?"}],
    "enable_search": true
  }'
```

### Example 3: With Deep Thinking (Reasoning)
```bash
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-reasoner",
    "messages": [{"role": "user", "content": "Solve: x^2 + 5x + 6 = 0"}]
  }'
```

### Example 4: With Both Search and Thinking
```bash
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-r1",
    "messages": [{"role": "user", "content": "Analyze the latest developments in fusion energy"}],
    "enable_search": true
  }'
```

### Example 3: Python
```python
import os
import requests

api_key = os.getenv("DEEPSEEK_API_KEY")

# With search enabled
response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Search for latest AI news"}],
        "enable_search": True
    }
)
print(response.json()["choices"][0]["message"]["content"])

# With deep thinking (reasoning model)
response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "deepseek-reasoner",
        "messages": [{"role": "user", "content": "Solve a complex math problem"}]
    }
)
result = response.json()["choices"][0]["message"]
print("Thinking:", result.get("reasoning_content"))
print("Answer:", result.get("content"))
```

## Rate Limits

- Free tier: Limited requests per minute
- Paid tier: Higher limits based on plan

Check your quota at: https://platform.deepseek.com/usage

## Error Handling

### Common Errors

| Status Code | Error | Solution |
|-------------|-------|----------|
| 401 | Invalid API key | Check your API key |
| 429 | Rate limit exceeded | Wait and retry |
| 500 | Server error | Retry later |
| 400 | Bad request | Check request format |

## Scripts

Use the bundled Python script for easy API calls:

```bash
python ~/.claude/skills/deepseek-api-search/scripts/deepseek_search.py "your query here"
```

## Related Resources

- [DeepSeek Platform](https://platform.deepseek.com/)
- [DeepSeek API Documentation](https://platform.deepseek.com/api-docs/)
- [Model Pricing](https://platform.deepseek.com/pricing)
