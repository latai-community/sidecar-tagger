"""
Title: Cluster Manager (Layer 2)
Abstract: Handles dynamic file grouping based on name similarity and neighborhood patterns.
Why: Reduces AI costs by inheriting metadata from 'cluster leaders' and provides 'neighborhood context' to the LLM.
Dependencies: difflib, typing, sdk.models.metadata
"""
import os
import difflib
from typing import List, Dict, Tuple
from collections import defaultdict
from sdk.models.metadata import ClusterHint

class ClusterManager:
    """
    Implements 'Canopy Clustering' logic to group files by name similarity
    before deep processing begins.
    """
    
    def __init__(self, similarity_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold
        # Stores computed clusters: {cluster_id: [file_paths]}
        self.clusters: Dict[str, List[str]] = {} 
        # Stores hints for each file: {file_path: ClusterHint}
        self.hints: Dict[str, ClusterHint] = {}

    def analyze_neighborhood(self, file_paths: List[str]) -> None:
        """
        Main entry point. Groups the provided files into semantic clusters.
        Populates self.hints with the results.
        """
        # 1. Group by Parent Directory first (Hard constraint)
        # Because files in different folders rarely share direct semantic context
        dir_groups = defaultdict(list)
        for f in file_paths:
            dir_groups[os.path.dirname(f)].append(f)
            
        # 2. Apply Fuzzy Clustering within each directory
        for parent_dir, files in dir_groups.items():
            self._cluster_directory(parent_dir, files)

    def get_hint(self, file_path: str) -> ClusterHint:
        """Returns the pre-calculated hint for a specific file."""
        return self.hints.get(file_path, ClusterHint(is_anomaly=True))

    def _cluster_directory(self, parent_dir: str, files: List[str]) -> None:
        """
        Internal logic to cluster files within a single folder.
        Uses SequenceMatcher (Levenshtein-like) to find groups.
        """
        if not files:
            return
            
        # Sort files to help the "leader" selection (e.g., File_1, File_2)
        sorted_files = sorted(files)
        
        # Simple greedy clustering
        # Pick first file as leader of Cluster A.
        # Check all others. If similar > threshold, add to A.
        # Repeat with remaining files.
        
        remaining = sorted_files[:]
        cluster_idx = 0
        
        while remaining:
            leader = remaining.pop(0)
            leader_name = os.path.basename(leader)
            
            # Start new cluster
            cluster_id = f"{os.path.basename(parent_dir)}_C{cluster_idx}"
            cluster_members = [leader]
            
            # Find followers
            non_matches = []
            for candidate in remaining:
                candidate_name = os.path.basename(candidate)
                similarity = difflib.SequenceMatcher(None, leader_name, candidate_name).ratio()
                
                if similarity >= self.similarity_threshold:
                    cluster_members.append(candidate)
                    # Generate Hint immediately
                    self.hints[candidate] = ClusterHint(
                        cluster_id=cluster_id,
                        similarity_score=similarity,
                        is_anomaly=False
                    )
                else:
                    non_matches.append(candidate)
            
            # Also set hint for leader (similarity 1.0)
            self.hints[leader] = ClusterHint(
                cluster_id=cluster_id,
                similarity_score=1.0,
                is_anomaly=False
            )
            
            # Register cluster
            self.clusters[cluster_id] = cluster_members
            
            # Prepare next iteration
            remaining = non_matches
            cluster_idx += 1

if __name__ == "__main__":
    # Test simulation
    manager = ClusterManager()
    test_files = [
        "/docs/Vaccine_Report_v1.pdf",
        "/docs/Vaccine_Report_v2.pdf",
        "/docs/Vaccine_Report_Final.pdf",
        "/docs/Random_Meme.jpg",
        "/docs/Budget_2024.xls",
        "/docs/Budget_2025.xls"
    ]
    
    print("--- Running Clustering Simulation ---")
    manager.analyze_neighborhood(test_files)
    
    for f in test_files:
        hint = manager.get_hint(f)
        print(f"File: {os.path.basename(f)} -> Cluster: {hint.cluster_id} (Sim: {hint.similarity_score:.2f})")
