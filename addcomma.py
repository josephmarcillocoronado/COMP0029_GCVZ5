import json

def convert_to_spacy_format(input_file, output_py_file):
    """
    Converts a training dataset from a custom JSONL format to a Python file with spaCy-compatible training data.

    Parameters:
        input_file (str): Path to the input JSONL file containing the original data.
        output_py_file (str): Path to the output Python file for the formatted spaCy data.
    """
    spacy_training_data = []

    # Load data from the input JSONL file
    with open(input_file, "r") as infile:
        for line in infile:
            entry = json.loads(line.strip())
            text = entry["text"]
            entities = []
            for start, end, label in entry["label"]:
                entities.append((start, end, label))
            spacy_training_data.append((text, {"entities": entities}))

    # Write the formatted data to a Python file
    with open(output_py_file, "w") as outfile:
        outfile.write("TRAIN_DATA = [\n")
        for text, annotations in spacy_training_data:
            outfile.write(f"    ({json.dumps(text)}, {json.dumps(annotations)}),\n")
        outfile.write("]\n")

if __name__ == "__main__":
    # Replace these paths with the actual paths to your input and output files
    input_file_path = "admin.jsonl"  # Update with your input file path
    output_py_file_path = "spacy_training_data.py"    # Update with your desired output Python file path

    # Call the conversion function
    convert_to_spacy_format(input_file_path, output_py_file_path)

    print(f"Training data successfully converted and saved to {output_py_file_path}")
