"""
Title: Findings Reporter
Abstract: Generates a human-readable summary of the indexing process (Findings & Suggestions).
Why: Provides actionable insights on duplicates, anomalies, and semantic clusters.
Dependencies: json, collections
"""
import os
import json
from collections import Counter, defaultdict
from typing import Dict, Any

class FindingsReporter:
    """
    Analyzes the sidecar.json manifest to generate a value-added report.
    """
    
    def __init__(self, manifest_path: str = "sidecar.json"):
        self.manifest_path = manifest_path

    def generate_report(self, output_path: str = "findings.md") -> None:
        """
        Reads the manifest and writes a Markdown report.
        """
        if not os.path.exists(self.manifest_path):
            return
            
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Analysis
        total_files = len(data)
        duplicates = [path for path, meta in data.items() if meta.get("duplicate_of")]
        anomalies = [path for path, meta in data.items() if meta.get("cluster_hint", {}).get("is_anomaly")]
        
        # Topic Analysis
        all_tags = []
        for meta in data.values():
            all_tags.extend(meta.get("tags", []))
        top_tags = Counter(all_tags).most_common(5)
        
        # Write Report
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# 🔎 Sidecar-Tagger Findings Report\n\n")
            f.write(f"**Total Files Processed:** {total_files}\n")
            f.write(f"**Duplicates Avoided:** {len(duplicates)} (saved processing time)\n\n")
            
            f.write("## 💡 Key Insights\n")
            f.write(f"* **Top Themes:** {', '.join([t[0] for t in top_tags])}\n")
            f.write(f"* **Semantic Anomalies:** {len(anomalies)} files detected as outliers in their folders.\n\n")
            
            if duplicates:
                f.write("## ♻️ Duplicate Files (Clean-up Candidates)\n")
                for dup in duplicates[:10]:
                    original = data[dup].get("duplicate_of")
                    f.write(f"- `{dup}` is a copy of `{original}`\n")
                if len(duplicates) > 10:
                    f.write(f"- ... and {len(duplicates) - 10} more.\n")

if __name__ == "__main__":
    reporter = FindingsReporter()
    reporter.generate_report()
    print("Report generated: findings.md")
