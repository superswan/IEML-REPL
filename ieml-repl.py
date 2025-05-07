#!/usr/bin/env python3

import logging
import unicodedata
from difflib import get_close_matches
from ieml.dictionary import term, Dictionary
from ieml_api import dic, term, adj_matrix
from ieml_auto import reverse_ieml 




logging.basicConfig(level=logging.INFO)

def normalize_code(code_str):
    # Normalize term codes. Apply Unicode NFKC, convert curly quotes and dashes.
    s = unicodedata.normalize('NFKC', code_str)
    s = s.replace('’', "'").replace('‘', "'")
    s = s.replace('–', '-').replace('—', '-')
    return s

def parse_term(code):
    try:
        t = term(code)
        code_str = str(t)
        print(f"Term: {code_str}")
        idx = getattr(t, 'index', None)
        if idx is not None:
            print(f"  Index:\t{idx}")
        layer = getattr(t, 'layer', None)
        if layer is not None:
            print(f"  Layer:\t{layer}")
        trans = getattr(t, 'translations', None)
        if trans:
            en = getattr(trans, 'en', None)
            if en:
                print(f"  English:\t{en}")
        rels = getattr(t, 'relations', None)
        neighs = getattr(rels, 'neighbours', None) if rels else None
        if neighs is not None:
            print(f"  Neighbours: {len(neighs)}")

    except Exception as e:
        print(f"Invalid IEML term: {e}")
        # Fuzzy-search against all valid codes when term is invalid
        all_codes = [str(term_obj) for term_obj in Dictionary().terms]
        suggestions = get_close_matches(code, all_codes, n=5, cutoff=0.6)
        if suggestions:
            print("Did you mean?:")
            for s in suggestions:
                print(f"  • {s}")
        else:
            print("No close matches found.")

def parse_by_index(index_str):
    # Lookup a term by its numeric index and display details
    try:
        idx = int(index_str)
    except ValueError:
        print(f"Invalid index: {index_str}")
        return
    match = None
    for t_obj in Dictionary().index:
        if getattr(t_obj, 'index', None) == idx:
            match = t_obj
            break
    if not match:
        print(f"No term found with index {idx}")
        return
    parse_term(str(match))

def list_neighbors(code):
    try:
        t = term(code)
        neighs = getattr(t.relations, 'neighbours', [])
        if not neighs:
            print(f"No neighbours found for {code}")
            return

        print(f"[{code}]")
        neigh_list = []
        for item in neighs:
            nbr = item[0] if isinstance(item, (tuple, list)) else item
            code_str = str(nbr)
            trans = getattr(nbr, 'translations', None)
            en = getattr(trans, 'en', None) if trans else None
            en_str = f" ({en})" if en else ''
            neigh_list.append((code_str, en_str))

        max_len = max(len(code_str) for code_str, _ in neigh_list)

        for code_str, en_str in neigh_list:
            padding = ' ' * (max_len - len(code_str))
            print(f"{code_str}{padding}  {en_str}")

    except Exception as e:
        print(f"Error fetching neighbors: {e}")

def check_relation(code1, code2):
    try:
        t1 = term(code1)
        t2 = term(code2)
        exists = bool(adj_matrix[t1.index, t2.index])
        print(f"{str(t1)} ↔ {str(t2)}: {exists}")
    except Exception as e:
        print(f"Error checking relation: {e}")

def search_by_english(query):
    en_map = dic.translations.get('en', {})
    if not en_map:
        print("No English translations found in dic.translations['en']")
        return

    matches = [(code, gloss) for code, gloss in en_map.items()
               if gloss and query.lower() in gloss.lower()]

    if not matches:
        print(f"No terms found matching '{query}'")
        return
    
    enhanced = []
    for code, gloss in matches:
        try:
            t = term(code)
            idx = getattr (t, 'index', None)
        except Exception:
            idx = None
        enhanced.append((code, idx, gloss))

    max_code_len = max(len(code) for code, _, _ in enhanced)
    max_idx_len = max(len(str(idx)) for _, idx, _ in enhanced if idx is not None)

    for code, idx, gloss in sorted(enhanced, key=lambda x: x[0]):
        code_pad = ' ' * (max_code_len - len(code))
        idx_str = str(idx) if idx is not None else ''
        idx_pad = ' ' * (max_idx_len - len(idx_str))
        print(f"{code}{code_pad}  [{idx_str}]{idx_pad}  → {gloss}")

def repl():
    print("IEML REPL")
    print("Type 'help' for commands and 'exit' to quit.")
    while True:
        try:
            raw = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not raw.strip():
            continue
        raw = normalize_code(raw)
        parts = raw.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "help":
            print("Commands:")
            print("  parse <TERM>               Validate & show term details")
            print("  index <NUM>                Get term by index number")
            print("  neighbors <TERM>           List semantic neighbors")
            print("  relation <TERM1> <TERM2>   Compute semantic relation distance")
            print("  search <TERM>              Search the dictionary for a term in natural language")
            print("  auto <TERM>                Automatically distill concept using AI")
            print("  exit                       Quit the REPL")
        elif cmd == "parse" and len(args) == 1:
            parse_term(args[0])
        elif cmd == "index" and len(args) == 1:
            parse_by_index(args[0])
        elif cmd in ("neighbours", "neighbors") and len(args) == 1:
            list_neighbors(args[0])
        elif cmd in ("relation") and len(args) == 2:
            check_relation(args[0], args[1])
        elif cmd == "exit":
            print("Goodbye!")
            break
        elif cmd == "search" and len(args) >= 1:
            search_by_english(" ".join(args))
        elif cmd == "auto" and args:
            reverse_ieml(" ".join(args))
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    repl()
