"""
Gemini Model Discovery Script - Simplified for Sidecar Tagger

Tests recommended models from Google Gemini API and shows which are available.

Usage:
    python list_models.py              # Quick test (count_tokens - no quota used)
    python list_models.py --mode full  # Full test (uses quota, shows real response)
"""

import os
import sys
import argparse

from dotenv import load_dotenv
from google import genai


RECOMMENDED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.5-flash-image",
]


def get_model_info_from_api(client) -> dict:
    """Get model info from API including supported actions."""
    model_info = {}
    for model in client.models.list():
        name = model.name.replace("models/", "") if model.name else ""
        model_info[name] = {
            "actions": model.supported_actions or [],
            "description": model.description or "",
        }
    return model_info


def infer_capabilities(actions: list) -> str:
    """Infer capabilities from supported actions."""
    caps = []
    if "generateContent" in actions:
        caps.append("text")
    if "predict" in actions or "generateContent" in actions:
        caps.append("image/video/audio")
    return ", ".join(caps) if caps else "text"


def load_api_key() -> str | None:
    """Load GEMINI_API_KEY from .env file."""
    load_dotenv()
    return os.getenv("GEMINI_API_KEY")


def quick_test(client, model_name: str) -> bool:
    """Quick test using count_tokens - no quota used."""
    try:
        client.models.count_tokens(model=model_name, contents="hi")
        return True
    except Exception:
        return False


def full_test(client, model_name: str) -> tuple[bool, str]:
    """Full test using generate_content - uses quota."""
    try:
        response = client.models.generate_content(
            model=model_name, contents="Reply with exactly: OK"
        )
        return True, response.text[:30]
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg:
            return False, "QUOTA_EXHAUSTED"
        if "404" in error_msg or "not found" in error_msg:
            return False, "NOT_FOUND"
        return False, error_msg[:40]


def main() -> None:
    parser = argparse.ArgumentParser(description="Test recommended Gemini models")
    parser.add_argument(
        "--mode",
        choices=["quick", "full"],
        default="quick",
        help="quick=count_tokens (no quota), full=generate_content",
    )
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        sys.exit(1)

    print("Testing recommended models for Sidecar Tagger...\n")

    client = genai.Client(api_key=api_key)

    # Get model info from API
    api_models = get_model_info_from_api(client)
    results = []

    print(f"{'Model':<30} {'Status':<20} {'Capabilities'}")
    print("-" * 75)

    for model_name in RECOMMENDED_MODELS:
        info = api_models.get(model_name, {})
        actions = info.get("actions", [])
        capabilities = infer_capabilities(actions)

        print(f"{model_name:<30} ", end="")

        if args.mode == "quick":
            success = quick_test(client, model_name)
            status = "OK" if success else "FAIL"
            print(f"{status:<20} {capabilities}")
            results.append((model_name, success))
        else:
            success, response = full_test(client, model_name)
            if success:
                print(f"{'OK':<20} {capabilities}")
            elif response == "QUOTA_EXHAUSTED":
                print(f"{'QUOTA REACHED':<20} {capabilities}")
            else:
                print(f"{'FAIL':<20} {capabilities}")
            results.append((model_name, success))

    working = [name for name, ok in results if ok]

    print("-" * 75)
    print(f"\nAvailable for use: {', '.join(working) if working else 'None'}")

    if working:
        print(f"\nRecommended: GEMINI_MODEL={working[0]}")
    else:
        print("\nNo models available. Check API key and quota.")


if __name__ == "__main__":
    main()
