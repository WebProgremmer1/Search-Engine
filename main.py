from pathlib import Path
import re
import json


### make a string lowercase, no symbols and split
def tokenize(text):
    lowered_text = text.lower()
    cleaned = re.sub(r'[^a-z0-9\s]', ' ', lowered_text)
    return cleaned.split()

# inverted index 


# form as how many words and which indexes mentioned
def inverted_index(tokenize_words, docID):
    
    for word in tokenize_words:
        if word not in index:
            index[word] = []

        if docID not in index[word]:
            index[word].append(docID)   

        # how many times it appers in document
        count_for_word = term_counts.setdefault(word, {})
        count_for_word[docID] = count_for_word.get(docID, 0) + 1



folder_path = Path(
    "/Users/artem/Desktop/Search Engine/pa1-skeleton/search"
)
cache_path = Path("index.json")
choice = input("Load or rebuild: ").strip().lower()

data = {}

if choice == "load" and cache_path.exists():
    with open("index.json", "r", encoding="utf-8") as file:
        data = json.load(file)

if "term_counts" in data:
    index = data["index"]

###
    documents = {
        int(docID): filename for docID, filename in data["documents"].items()
    }
    term_counts = {
        word: {int(docID): count for docID, count in counts.items()}
        for word, counts in data["term_counts"].items()
    }

###

else:
    index = {}
    documents = {}
    term_counts = {}
    
    for docID, file_path in enumerate(sorted(folder_path.glob("*.txt"))):
        documents[docID] = file_path.name # match every id with name
        inverted_index(tokenize(file_path.read_text(encoding="utf-8")), docID)
        


    with open("index.json", "w", encoding="utf-8") as file:
        json.dump(
            {"index" : index, 
             "documents" : documents, 
             "term_count" : term_counts }, 
             file, 
             indent=4)



def search_and(modified_request):
    if not modified_request:
        return []

    # in case the word is missing
    # get the document id 
    candidates = index.get(modified_request[0], [])

    # start from 1 cuz candidates start with 0
    for word in modified_request[1:]:
        matches = []
        for docID in candidates:
            if docID not in index.get(word, []):
                matches.append(docID)
        candidates = matches

    return candidates


def search_or(modified_request):

    matches = []
    
    for word in modified_request:
        for docID in index.get(word, []):
            if docID not in matches:
                matches.append(docID)

    return sorted(matches)



def search_or_ranked(modified_request):
    scores = {}

    for word in set(modified_request):
        for docID in index.get(word, []):
            count = term_counts[word][docID]
            scores[docID] = scores.get(docID, 0) + 1

    # we use tricl to sort from smallest to largest by using def of negative numbers
    ranked_ids =  sorted(scores, key=lambda docID: (-scores[docID], docID))
    return [(docID, scores[docID]) for docID in ranked_ids]





### AND OR. block 


def first_matching_line(filename, query_words):
    try:
        with (folder_path / filename).open("r", encoding="utf-8") as file:
            for line in file:
                if query_words.intersection(tokenize(line)):
                    return line.rstrip("\r\n")
    except OSError:
        return "Preview unavailable."

    return "No matching line found."

while True:
    user = input("Would you like to search one more ? (YES/NO)").strip().lower()
    if user in ["quit", "no"]: 
        break
      
    request = input("Enter which word you are looking for: ").strip().lower()
    modified_request = tokenize(request)
    and_or = input("Would you to make search AND / OR ").strip().lower()

    # make sure user enter correctly
    if and_or not in ["and", "or"]:
        print("Enter AND or OR.")
        continue

    results = search_or_ranked(modified_request)


    # we implement set to save some time, not to go thorugh the same IDs 
    if and_or == "and":
        matches = set(search_and(modified_request))
        results = [(docID, score) for docID, score in results if docID in matches]

    if not results:
        print("No matches found.")
        continue    

    query = set(modified_request)
    for rank, (docID, score) in enumerate(results, start=1):
        filename = documents[docID]
        print(f"{rank} {docID} -score: {score}")
    if rank <= 5:
        print(f"{first_matching_line(filename, query)}")



# print(file_path.name)
# print(tokenize_words)
print(index)
print(documents)
