import re


class Chunker:

    @staticmethod
    def clean_text(text: str) -> str:

        text = text.replace("\r", "\n")

        # Remplacer plusieurs espaces par un seul
        text = re.sub(r"[ \t]+", " ", text)

        # Remplacer plusieurs retours à la ligne par un seul
        text = re.sub(r"\n+", "\n", text)

        return text.strip()

    @staticmethod
    def split(
        text: str,
        chunk_size: int = 700,
        overlap: int = 100
    ):

        text = Chunker.clean_text(text)

        # Découpage en phrases
        sentences = re.split(r'(?<=[.!?;:])\s+|\n', text)

        chunks = []

        current = ""

        chunk_id = 1

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            if len(current) + len(sentence) + 1 <= chunk_size:

                if current:
                    current += " "

                current += sentence

            else:

                chunks.append({
                    "id": chunk_id,
                    "text": current,
                    "length": len(current)
                })

                chunk_id += 1

                # overlap
                if overlap > 0 and len(current) > overlap:
                    current = current[-overlap:] + " " + sentence
                else:
                    current = sentence

        if current:

            chunks.append({
                "id": chunk_id,
                "text": current,
                "length": len(current)
            })

        return chunks