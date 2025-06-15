import tensorflow_hub as hub
import tensorflow as tf

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

def get_match_score(resume: str, job_description: str) -> float:
    embeddings = embed([resume, job_description])
    similarity = tf.keras.losses.cosine_similarity(embeddings[0], embeddings[1]).numpy()
    score = (1 - abs(similarity)) * 100
    return round(score, 2)
