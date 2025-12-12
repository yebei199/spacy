import argparse
import sys
from src.scripts.spa_1 import SpaCy1

def main():
    parser = argparse.ArgumentParser(description="Generate colorful SpaCy dependency graph in browser.")
    parser.add_argument("text", nargs='+', help="The text to analyze.")
    args = parser.parse_args()
    
    # Combine args into a single sentence if multiple words provided
    text = " ".join(args.text)
    
    print(f"Analyzing: {text}")
    app = SpaCy1()
    app.generate_dependency_graph(text)

if __name__ == "__main__":
    main()