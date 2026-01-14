from anthropic import Anthropic
import os
from typing import List, Dict, Any

class RAGChain:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        # Load system prompt
        with open('./system_prompts/analyst.txt', 'r') as f:
            self.system_prompt = f.read()

    def build_context(self, documents: List[str]) -> str:
        """Build context from retrieved documents"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"--- Match Data {i} ---\n{doc}\n")

        return "\n".join(context_parts)

    def invoke(self, question: str, context: str, history: List[Dict] = None) -> Dict[str, Any]:
        """Run the RAG chain with retrieved context"""

        # Build messages
        messages = []

        # Add conversation history if provided
        if history:
            for msg in history:
                if msg['role'] == 'user':
                    messages.append({
                        "role": "user",
                        "content": msg['content']
                    })
                elif msg['role'] == 'assistant':
                    messages.append({
                        "role": "assistant",
                        "content": msg['content']
                    })

        # Add current question with context
        user_message = f"""Using the following Arsenal FC match data, please answer the question:

RELEVANT MATCH DATA:
{context}

USER QUESTION:
{question}

Please provide a data-driven analysis with specific statistics, match dates, and tactical insights."""

        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call Anthropic API
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=self.system_prompt,
            messages=messages
        )

        answer = response.content[0].text

        return {
            "answer": answer,
            "model": "claude-3-5-sonnet",
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }
