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
 


folder_path = Path(
    "/Users/artem/Desktop/Search Engine/pa1-skeleton/search"
)
cache_path = Path("index.json")
choice = input("Load or rebuild: ").strip().lower()

score = 0

if choice == "load" and cache_path.exists():
    with open("index.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    
    index = data["index"]

    documents ={}
    for docID, filename in data["documents"].items():
        documents[int(docID)] = filename



else:
    index = {}
    documents = {}
    term_counts = {}
    for docID, file_path in enumerate(sorted(folder_path.glob("*.txt"))):
        documents[docID] = file_path.name # match every id with name
        text = file_path.read_text(encoding="utf-8")
        tokenize_words = tokenize(text)
        inverted_index(tokenize_words, docID)


    with open("index.json", "w", encoding="utf-8") as file:
        json.dump({"index" : index, "documents" : documents, "term_count" : term_counts }, file, indent=4)



# print(file_path.name)
# print(tokenize_words)
print(index)
print(documents)






def search_or_ranked(modified_request):
    scores = {}

    for word in set(modified_request):
        for docID in index.get(word, []):
            scores[docID] = scores.get(docID, 0) + 1

    print( sorted(scores, key=lambda docID: (-scores[docID], docID)))






### AND OR. block 

keep_search = True
while keep_search:
    user = input("Would you like to search one more ? ").strip().lower()
    if user in ["quit", "no"]: 
        keep_search = False
    
    else:    
        request = input("Enter which word you are looking for: ").strip().lower()
        modified_request = tokenize(request)
        search_or_ranked(modified_request)
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

            print(candidates)
            

        def search_or(modified_request):

            matches = []
            
            for word in modified_request:
                for docID in index.get(word, []):
                    if docID not in matches:
                        matches.append(docID)

            print(sorted(matches))

    and_or = input("Would you to make search AND / OR ").strip().lower()
    if and_or == "and":
        search_and(modified_request)
    elif and_or == "or":  
        for docID, score in search_or_ranked(modified_request):
            print(f"{documents[docID]} — score: {score}")



