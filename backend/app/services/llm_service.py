import requests


class LLMService:

    def __init__(self):

        self.url = "http://localhost:11434/api/generate"

        self.model = "llama3.2:3b"

    def generate(self, question, chunks):

        context = "\n\n".join(chunks)

        prompt = f"""
Tu es un assistant IA spécialisé dans la recherche documentaire.

Réponds uniquement à partir des informations fournies.

Si la réponse n'est pas présente dans le contexte, réponds :

"Je ne trouve pas cette information dans les documents."

Contexte :

{context}

Question :

{question}

Réponse :
"""

        response = requests.post(

            self.url,

            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }

        )

        return response.json()["response"]