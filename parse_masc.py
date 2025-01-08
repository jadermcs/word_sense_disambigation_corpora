import xml.etree.ElementTree as ET
import json
from collections import defaultdict
from glob import glob

def process_xml(file_path, sense_mapping):
    """
    Process the XML file to extract sentences and replace senses.

    Args:
        file_path (str): Path to the XML file.
        sense_mapping (dict): Dictionary to map original senses to WordNet mappings.

    Returns:
        list: List of dictionaries with sentences and their replaced senses.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    sentences = []
    current_sentence = ""
    senses_in_sentence = []
    count = defaultdict(int)

    for word in root.findall("word"):
        text = word.get("text")
        break_level = word.get("break_level")
        sense = word.get("sense")

        # If the word has a sense, replace it using the mapping
        sense = sense_mapping.get(sense, None)
        if sense:
            senses_in_sentence.append(sense)
            count[sense.split('%')[0]] += 1

        current_sentence += ("" if break_level == "NO_BREAK" else " ") + text

        # Handle sentence boundaries
        if text in {".", "\n"}:
            # Keep only elements that occur once
            senses_in_sentence = [item for item in senses_in_sentence if count[item.split('%')[0]] == 1]
            sentences.append({
                "sentence": current_sentence,
                "senses": senses_in_sentence,
            })
            current_sentence = ""
            senses_in_sentence = []
            count = defaultdict(int)

    # Handle any remaining sentence
    if current_sentence:
        # Keep only elements that occur once
        senses_in_sentence = [item for item in senses_in_sentence if count[item.split('%')[0]] == 1]
        sentences.append({
            "sentence": current_sentence,
            "senses": senses_in_sentence,
        })

    return sentences


if __name__ == "__main__":
    # Dictionary for sense mapping
    sense_mapping = {}
    with open("manual_map.txt") as fin:
        for line in fin.readlines():
            sense, mapping = line.strip().split("\t")
            mapping = mapping.split(',')[0]
            sense_mapping[sense] = mapping
    data = []
    for file_path in glob("masc/**/*.xml", recursive=True):
        print(file_path)
        # Process the XML file
        result = process_xml(file_path, sense_mapping)

        # Print the result
        for item in result:
            for sense in item["senses"]:
                data.append({
                    "usage": item["sentence"],
                    "sense_key": sense,
                })

    print(len(data))
    with open("masc.json", "w") as fout:
        json.dump(data, fout, indent=2)
