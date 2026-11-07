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
    for docID, file_path in enumerate(sorted(folder_path.glob("*.txt"))):
        documents[docID] = file_path.name # match every id with name
        text = file_path.read_text(encoding="utf-8")
        tokenize_words = tokenize(text)
        inverted_index(tokenize_words, docID)

    with open("index.json", "w", encoding="utf-8") as file:
        json.dump({"index" : index, "documents" : documents}, file, indent=4)



# print(file_path.name)
# print(tokenize_words)
print(index)
print(documents)






### AND OR. block 


keep_search = True
while keep_search:
    user = input("Would you like to search one more ? ")
    if user == "quit": 
        keep_search = False
    
    else:    
        request = input("Enter which word you are looking for: ") # single word
        modified_request = tokenize(request)

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


        def search_or(modified_request):

            matches = []
            
            for word in modified_request:
                for docID in index.get(word, []):
                    if docID not in matches:
                        matches.append(docID)

            print(sorted(matches))


        search_and(modified_request)
        search_or(modified_request)

