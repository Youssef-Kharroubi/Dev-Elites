import re
import pandas as pd
from thefuzz import fuzz

df = pd.read_csv('../../models/dataset_names.csv')
name_list = df['names'].dropna().astype(str).tolist()

def match_word_to_names(word, name_list, threshold=70):
    matches = []
    for name in name_list:
        similarity = fuzz.ratio(word.lower(), name.lower())
        if similarity >= threshold:
            matches.append((name, similarity))
    return matches

def clean_and_match_name(name_string, threshold=70):
    cleaned = re.sub(r'[^a-zA-Z\s]', '', name_string)
    name_parts = [word for word in cleaned.split() if word]

    for part in name_parts:
        predictions = match_word_to_names(part, name_list, threshold=threshold)
        predictions = sorted(predictions, key=lambda x: x[1], reverse=True)

        print(f"Matches for \033[1m{part}\033[0m")
        if predictions:
            for matched_name, similarity in predictions:
                print(f"\033[1m'{matched_name}'\033[0m (Similarity: {similarity}%)")
        else:
            print(f"No match for {part}")
        print("\n")

#call of the code
clean_and_match_name("leila", 70)