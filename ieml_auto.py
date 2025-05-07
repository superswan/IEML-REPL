import json
import textwrap
import re
import numpy as np
import logging
from sklearn.neighbors import NearestNeighbors
from ollama import Client
from ieml_api import dic, term

# Ollama setup
client = Client()
EMBED_MODEL = "nomic-embed-text"
COMP_MODEL = "gemma3"

# Load embeddings 
_data = np.load("gloss_embeddings.npz", allow_pickle=True)
_codes = _data["codes"].tolist()
_gloss_embeddings = _data["embeddings"].astype(float)
_nbrs = NearestNeighbors(n_neighbors=min(len(_codes), 32),
                         metric="cosine", algorithm="brute")
_nbrs.fit(_gloss_embeddings)


def _clean_code(c: str) -> str:
    return c.strip(" ,\"'")


def top_primitives(concept: str, k: int = 15) -> list[str]:
    valid = []
    attempted = set()
    offset = 0

    while len(valid) < k and offset < len(_codes):
        resp = client.embed(model=EMBED_MODEL, input=[concept])
        vec = np.array(resp.embeddings, dtype=float).reshape(1, -1)

        _, idxs = _nbrs.kneighbors(vec, n_neighbors=len(_codes))
        raw = [_codes[i] for i in idxs[0][offset:]]

        for rc in raw:
            code = _clean_code(rc)
            if code in attempted:
                continue
            attempted.add(code)
            try:
                term(code)
                valid.append(code)
                if len(valid) == k:
                    break
            except:
                continue
        offset += len(raw)

    return valid[:k]

def compose_ieml_raw(concept: str, candidates: list[str]) -> str:
    en_map = dic.translations.get("en", {})
    primitives = [{"code": c, "gloss": en_map.get(c, '')} for c in candidates]

    prompt = f"""
You are an IEML expert. Given the concept and primitives provided, select any number of primitives necessary
that best represent the concept. Return your selection in JSON format with only the 
chosen primitives and their glosses, no additional text. 

Concept: "{concept}"

Available primitives:
{json.dumps(primitives, indent=2)}

Response format examples and explanation:

<Minimum> 1-3 terms (only for very concrete things) 
[
  {{"code": "primitive_code", "gloss": "primitive_gloss"}}
]

<Practical default> 3-5 terms—rich enough for search & reasoning, still human‑readable 

[
  {{"code": "primitive_code", "gloss": "primitive_gloss"}},
  {{"code": "primitive_code", "gloss": "primitive_gloss"}},
  {{"code": "primitive_code", "gloss": "primitive_gloss"}}
]

<Upper limit>: 5–6 terms (nuanced/vague/multiplicative concepts)
[
  {{"code": "primitive_code", "gloss": "primitive_gloss"}},
  {{"code": "primitive_code", "gloss": "primitive_gloss"}},
  {{"code": "primitive_code", "gloss": "primitive_gloss"}},
  {{"code": "primitive_code", "gloss": "primitive_gloss"}},
  {{"code": "primitive_code", "gloss": "primitive_gloss"}}
]

"""

    resp_obj = client.generate(model=COMP_MODEL, prompt=prompt)
    return resp_obj.dict().get("response", "")


import textwrap

def reverse_ieml(concept: str):
    logging.getLogger("httpx").setLevel(logging.WARNING)

    cands = top_primitives(concept)
    en_map = dic.translations.get("en", {})

    glosses = [en_map.get(code, '') for code in cands]
    max_len = max((len(g) for g in glosses), default=0)

    print(f"{concept}")
    print("Candidates:")
    for code, gloss in zip(cands, glosses):
        print(f"    {gloss:<{max_len}} → {code}")

    raw = compose_ieml_raw(concept, cands)
    print("\nAuto suggestion:\n")
    print(raw)
    print()

    return raw

