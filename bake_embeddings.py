import json
import numpy as np
from ollama import Client
from ieml_api import dic


client = Client()
EMBED_MODEL = "nomic-embed-text"

en_map = dic.translations.get("en", {})
codes   = list(en_map.keys())
glosses = list(en_map.values())

resp = client.embed(model=EMBED_MODEL, input=glosses)

embeddings = resp.embeddings  

with open("gloss_embeddings.json", "w", encoding="utf8") as f:
    json.dump({"codes": codes, "embeddings": embeddings}, f)

np.savez("gloss_embeddings.npz",
         codes=codes,
         embeddings=np.array(embeddings, dtype=float))

print(f"Saved {len(codes)} embeddings to gloss_embeddings.npz")
