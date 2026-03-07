"""
Title: Planning Mode Trigger
Abstract: Utility to print the content of planning.md to the console for review.
Dependencies: os, sys
LLM-Hints: Run this script when the user asks to "Review the Plan" or "Show Roadmap".
"""

import os
import sys

def show_plan():
    """Reads and displays the master planning document."""
    plan_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "planning.md")
    
    if os.path.exists(plan_path):
        print(f"--- Loading Master Plan from {plan_path} ---\n")
        with open(plan_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("Error: planning.md not found in project root.")

if __name__ == "__main__":
    show_plan()
