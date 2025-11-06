import numpy as np
from sklearn.preprocessing import normalize
from sentence_transformers import SentenceTransformer, util

def clean_name(name):
    return name.replace("(", "").replace(")", "").replace(" ", "").lower()

def get_top_candidates(model, ingredient, node_names, node_embeds, k=10):
    query_vec = model.encode([ingredient], normalize_embeddings=True)
    sims = util.cos_sim(query_vec, node_embeds)[0]
    top_idx = sims.topk(k).indices
    return [node_names[i] for i in top_idx]

def combine_user_vector(base_vec, pref_vec):
    if base_vec is None:
        combined = pref_vec
    elif pref_vec is None:
        combined = base_vec
    else:
        combined = (base_vec * 0.5) + (pref_vec * 0.5)
    return normalize(combined.reshape(1, -1))[0]
