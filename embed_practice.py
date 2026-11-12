from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "I can't log in to my account",
    "Unable tos ign in",
    "I was charged twice for my order",
]

embeddings = model.encode(sentences)

print(embeddings.shape)
print(util.cos_sim(embeddings[0], embeddings[1]))
print(util.cos_sim(embeddings[0], embeddings[2]))