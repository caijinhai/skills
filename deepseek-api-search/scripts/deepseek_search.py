#!/usr/bin/env python3
"""
DeepSeek API Client with Search and Deep Thinking Support

Usage:
    python deepseek_search.py "your query here"
    python deepseek_search.py --search "your query here"
    python deepseek_search.py --no-search "your query here"
    python deepseek_search.py --thinking "your query here"
    python deepseek_search.py --no-thinking "your query here"
    python deepseek_search.py --model deepseek-reasoner "your query"
    python deepseek_search.py --show-thinking "your query"
"""

import os
import sys
import json
import argparse
from typing import Optional


try:
    import requests
except ImportError:
    print("Installing requests library...")
    os.system("pip install requests")
    import requests


DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Models that support deep thinking (reasoning)
THINKING_MODELS = {"deepseek-reasoner"}

# Default model for different use cases
DEFAULT_MODELS = {
    "chat": "deepseek-chat",
    "coder": "deepseek-coder",
    "reasoning": "deepseek-reasoner",
}


def get_api_key() -> str:
    """Get API key from environment or prompt user."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # Try to read from config file
        config_paths = [
            os.path.expanduser("~/.deepseek_api_key"),
            os.path.expanduser("~/.config/deepseek/api_key"),
        ]
        for path in config_paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    api_key = f.read().strip()
                    if api_key:
                        break

    if not api_key:
        print("Error: DEEPSEEK_API_KEY environment variable not set.")
        print("Please set it or create a file at ~/.deepseek_api_key")
        print("Get your API key from: https://platform.deepseek.com/")
        sys.exit(1)

    return api_key


def call_deepseek(
    query: str,
    model: str = "deepseek-chat",
    enable_search: bool = False,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
) -> dict:
    """
    Call DeepSeek API with configurable options.

    Args:
        query: The user's query/question
        model: Model ID (deepseek-chat, deepseek-coder, deepseek-reasoner, deepseek-r1)
        enable_search: Whether to enable web search
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens in response
        stream: Whether to stream the response

    Returns:
        API response as dictionary
    """
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Build messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
    ]

    # Build payload
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }

    # Only add enable_search if explicitly requested (not all models support it)
    if enable_search:
        payload["enable_search"] = True

    if temperature is not None:
        payload["temperature"] = temperature

    if max_tokens:
        payload["max_tokens"] = max_tokens

    response = requests.post(
        DEEPSEEK_API_URL,
        headers=headers,
        json=payload,
        timeout=120  # Increased timeout for reasoning models
    )

    if response.status_code == 401:
        print("Error: Invalid API key. Please check your DEEPSEEK_API_KEY.")
        sys.exit(1)
    elif response.status_code == 429:
        print("Error: Rate limit exceeded. Please wait and try again.")
        sys.exit(1)
    elif response.status_code != 200:
        print(f"Error: API request failed with status {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

    return response.json()


def format_response(data: dict, show_thinking: bool = False) -> str:
    """
    Format API response for display.

    Args:
        data: API response dictionary
        show_thinking: Whether to show the thinking/reasoning process

    Returns:
        Formatted string output
    """
    if "choices" not in data or len(data["choices"]) == 0:
        return "No response generated."

    choice = data["choices"][0]
    message = choice.get("message", {})
    content = message.get("content", "")
    reasoning_content = message.get("reasoning_content", "")

    output = []

    # Show thinking process if available and requested
    if reasoning_content and show_thinking:
        output.append("=" * 60)
        output.append("THINKING PROCESS:")
        output.append("=" * 60)
        output.append(reasoning_content)
        output.append("")

    # Show final answer
    output.append("=" * 60)
    output.append("ANSWER:")
    output.append("=" * 60)
    output.append(content)

    # Add usage info
    if "usage" in data:
        usage = data["usage"]
        output.append("")
        output.append("=" * 60)
        output.append("USAGE:")
        output.append(f"  Prompt tokens: {usage.get('prompt_tokens', 0)}")
        output.append(f"  Completion tokens: {usage.get('completion_tokens', 0)}")
        output.append(f"  Total tokens: {usage.get('total_tokens', 0)}")

        # Show cached tokens if available
        if "prompt_tokens_details" in usage:
            cached = usage["prompt_tokens_details"].get("cached_tokens", 0)
            if cached > 0:
                output.append(f"  Cached tokens: {cached}")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Call DeepSeek API with web search and deep thinking support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s "What is the weather today?"
    %(prog)s --search "Latest AI news"
    %(prog)s --no-search "Write a poem"
    %(prog)s --model deepseek-reasoner "Solve: x^2 + 5x + 6 = 0"
    %(prog)s --thinking "Analyze this complex problem"
    %(prog)s --show-thinking "Explain your reasoning step by step"
    %(prog)s --json "Explain quantum computing"
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Your query/question"
    )
    parser.add_argument(
        "--search",
        action="store_true",
        default=False,
        help="Enable web search"
    )
    parser.add_argument(
        "--no-search",
        action="store_true",
        help="Disable web search (default)"
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        default=None,
        help="Enable deep thinking mode (uses deepseek-reasoner model)"
    )
    parser.add_argument(
        "--no-thinking",
        action="store_true",
        help="Disable deep thinking mode"
    )
    parser.add_argument(
        "--model",
        choices=["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
        default=None,
        help="Model to use (default: auto-select based on --thinking flag)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature (0-2, default: 0.7)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum tokens in response"
    )
    parser.add_argument(
        "--show-thinking",
        action="store_true",
        help="Display the thinking/reasoning process in output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save response to file"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only output the final answer (no thinking process)"
    )

    args = parser.parse_args()

    # Handle query from stdin if not provided
    if not args.query:
        if not sys.stdin.isatty():
            args.query = sys.stdin.read().strip()
        else:
            parser.print_help()
            sys.exit(1)

    # Determine model selection
    if args.model:
        model = args.model
    elif args.thinking:
        # If --thinking is explicitly set, use reasoning model
        model = DEFAULT_MODELS["reasoning"]
    else:
        # Default to chat model
        model = DEFAULT_MODELS["chat"]

    # Determine search setting
    enable_search = args.search and not args.no_search

    # Print status
    is_thinking_model = model in THINKING_MODELS
    print(f"Calling DeepSeek API (model: {model}, search: {enable_search}, thinking: {is_thinking_model})...")

    try:
        response_data = call_deepseek(
            query=args.query,
            model=model,
            enable_search=enable_search,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )

        if args.json:
            output = json.dumps(response_data, indent=2)
        else:
            # Show thinking by default for reasoning models unless --quiet
            show_thinking = args.show_thinking or (is_thinking_model and not args.quiet)
            output = format_response(response_data, show_thinking=show_thinking)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Response saved to: {args.output}")
        else:
            print(output)

    except requests.exceptions.Timeout:
        print("Error: Request timed out. Please try again.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Network error - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
