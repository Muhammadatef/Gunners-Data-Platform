from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os

class EmbeddingManager:
    def __init__(self, persist_directory: str = "./data/chroma"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))

        try:
            self.collection = self.chroma_client.get_collection("arsenal_matches")
        except:
            self.collection = self.chroma_client.create_collection(
                name="arsenal_matches",
                metadata={"description": "Arsenal FC match statistics and analysis"}
            )

    def create_match_document(self, match: Dict[str, Any]) -> str:
        """Convert match data to searchable text"""
        venue_text = "Home" if match.get('venue') == 'H' else "Away"
        
        # Safely get values with defaults
        total_shots = match.get('total_shots') or 0
        goals = match.get('goals') or 0
        conversion_rate = (goals / total_shots * 100) if total_shots else 0
        
        arsenal_xg = match.get('arsenal_xg') or 0
        opponent_xg = match.get('opponent_xg') or 0
        arsenal_goals = match.get('arsenal_goals') or 0
        opponent_goals = match.get('opponent_goals') or 0
        shots_on_target = match.get('shots_on_target') or 0
        avg_shot_xg = match.get('avg_shot_xg') or 0
        big_chances = match.get('big_chances') or 0

        text = f"""
        Match: Arsenal vs {match.get('opponent', 'Unknown')} on {match.get('match_date', 'Unknown')} ({match.get('season', 'Unknown')} season)
        Venue: {venue_text}
        Result: {match.get('result', 'Unknown')} ({arsenal_goals}-{opponent_goals})

        Expected Goals (xG):
        - Arsenal xG: {arsenal_xg:.2f}
        - Opponent xG: {opponent_xg:.2f}
        - xG Overperformance: {(arsenal_goals - float(arsenal_xg)):.2f}

        Shot Statistics:
        - Total Shots: {total_shots}
        - Shots on Target: {shots_on_target}
        - Goals Scored: {goals}
        - Conversion Rate: {conversion_rate:.1f}%
        - Average Shot xG: {float(avg_shot_xg):.3f}
        - Big Chances: {big_chances}

        Scorers: {match.get('scorers') or 'None'}
        """

        return text.strip()

    def add_matches(self, matches: List[Dict[str, Any]]):
        """Add matches to ChromaDB with embeddings"""
        documents = []
        metadatas = []
        ids = []

        for match in matches:
            doc_text = self.create_match_document(match)
            documents.append(doc_text)

            metadatas.append({
                "match_date": str(match.get('match_date', '')),
                "season": str(match.get('season', '')),
                "opponent": str(match.get('opponent', '')),
                "result": str(match.get('result', '')),
                "venue": str(match.get('venue', ''))
            })

            ids.append(f"{match.get('match_date', 'unknown')}_{match.get('opponent', 'unknown')}")

        # Add to ChromaDB (it handles embedding automatically)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"✅ Added {len(documents)} matches to vector database")

    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search for relevant matches based on query"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        return {
            "documents": results['documents'][0] if results['documents'] else [],
            "metadatas": results['metadatas'][0] if results['metadatas'] else [],
            "distances": results['distances'][0] if results['distances'] else []
        }

    def clear_collection(self):
        """Clear all embeddings (useful for rebuilding)"""
        self.chroma_client.delete_collection("arsenal_matches")
        self.collection = self.chroma_client.create_collection(
            name="arsenal_matches",
            metadata={"description": "Arsenal FC match statistics and analysis"}
        )
