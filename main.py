from pathlib import Path
import json
import re


folder_path = Path(__file__).resolve().parent
cache_path = folder_path.parent / "index.json"
index = {}
documents = {}
term_counts = {}


def tokenize(text):
    """Lowercase text, replace punctuation with spaces, and split into words."""
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return cleaned.split()


def inverted_index(tokenize_words, docID):
    for word in tokenize_words:
        if word not in index:
            index[word] = []
        if docID not in index[word]:
            index[word].append(docID)

        count_for_word = term_counts.setdefault(word, {})
        count_for_word[docID] = count_for_word.get(docID, 0) + 1


def rebuild_index():
    index.clear()
    documents.clear()
    term_counts.clear()
    for docID, file_path in enumerate(sorted(folder_path.glob("*.txt"))):
        documents[docID] = file_path.name
        inverted_index(tokenize(file_path.read_text(encoding="utf-8")), docID)

    with cache_path.open("w", encoding="utf-8") as file:
        json.dump(
            {"index": index, "documents": documents, "term_counts": term_counts},
            file,
            indent=4,
        )


def load_index():
    global index, documents, term_counts
    with cache_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # Accept the spelling used by older caches, too.
    saved_counts = data.get("term_counts", data.get("term_count"))
    if saved_counts is None:
        raise ValueError("The saved index has no term counts.")

    index = {word: [int(docID) for docID in ids]
             for word, ids in data["index"].items()}
    documents = {int(docID): filename
                 for docID, filename in data["documents"].items()}
    term_counts = {
        word: {int(docID): count for docID, count in counts.items()}
        for word, counts in saved_counts.items()
    }


def search_and(modified_request):
    if not modified_request:
        return []

    candidates = set(index.get(modified_request[0], []))
    for word in modified_request[1:]:
        candidates.intersection_update(index.get(word, []))
    return sorted(candidates)


def search_or(modified_request):
    matches = set()
    for word in modified_request:
        matches.update(index.get(word, []))
    return sorted(matches)


def search_or_ranked(modified_request):
    scores = {}
    for word in set(modified_request):
        for docID in index.get(word, []):
            count = term_counts[word][docID]
            scores[docID] = scores.get(docID, 0) + count

    ranked_ids = sorted(scores, key=lambda docID: (-scores[docID], docID))
    return [(docID, scores[docID]) for docID in ranked_ids]


def main():
    choice = input("Load or rebuild: ").strip().lower()
    if choice == "load":
        try:
            load_index()
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            print("Saved index is missing or incompatible; rebuilding.")
            rebuild_index()
    else:
        rebuild_index()

    print(f"Indexed {len(documents)} documents.")
    while True:
        user = input("Would you like to search one more? (yes/no): ").strip().lower()
        if user in {"quit", "no", "exit"}:
            break

        request = input("Enter which word you are looking for: ")
        modified_request = tokenize(request)
        if not modified_request:
            print("Please enter at least one word.")
            continue

        and_or = input("Search AND / OR: ").strip().lower()
        if and_or == "and":
            matches = search_and(modified_request)
            for docID in matches:
                print(documents[docID])
        elif and_or == "or":
            matches = search_or_ranked(modified_request)
            for docID, score in matches:
                print(f"{documents[docID]} — score: {score}")
        else:
            print("Please choose AND or OR.")
            continue

        if not matches:
            print("No matching documents.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
 
