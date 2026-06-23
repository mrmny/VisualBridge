#!/usr/bin/env python3
# HU: Parancssori felület (CLI) a VisualBridge ágenshez
# EN: Command Line Interface (CLI) for the VisualBridge agent
import sys
import argparse
import json
from agents import VisualBridgeAgent

def main():
    parser = argparse.ArgumentParser(
        description="VisualBridge CLI - AI-driven text simplifier and visual mapping agent."
    )
    parser.add_argument(
        "--text",
        type=str,
        required=True,
        help="HU: A feldolgozandó komplex szöveg. | EN: The complex text to be processed."
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="hu",
        choices=["hu", "en"],
        help="HU: Nyelvi kód (hu/en). | EN: Language code (hu/en)."
    )

    args = parser.parse_args()

    print("=" * 60)
    print("VisualBridge Agent CLI")
    print(f"Language: {args.lang.upper()}")
    print(f"Input: {args.text}")
    print("=" * 60)

    print("\nProcessing text via Google ADK Agent...")
    try:
        agent = VisualBridgeAgent()
        result = agent.process_pipeline(args.text, lang=args.lang)

        print("\n[Simplified Sentences & Pictogram Mappings]")
        for i, item in enumerate(result.get("processed_story", [])):
            print(f"\n{i+1}. Sentence: {item['sentence']}")
            print(f"   Keywords: {', '.join(item['keywords'])}")
            print("   Visual Pictograms:")
            if item.get("tokens_with_pics"):
                for token in item["tokens_with_pics"]:
                    print(f"     - {token['word']}: {token['image_url']}")
            else:
                print("     - None matched.")

        print("\nRaw JSON Output:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("=" * 60)

    except Exception as e:
        print(f"\nError occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
