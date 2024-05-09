import json

def convert_to_spacy_format(input_file, output_py_file, variable_name):
    """
    Converts a dataset from a custom JSONL format to a Python file with spaCy-compatible training data.

    Parameters:
        input_file (str): Path to the input JSONL file containing the original data.
        output_py_file (str): Path to the output Python file for the formatted spaCy data.
        variable_name (str): The name of the variable to be used in the output Python file.
    """
    spacy_data = []

    # Load data from the input JSONL file
    with open(input_file, "r") as infile:
        for line in infile:
            entry = json.loads(line.strip())
            text = entry["text"]
            entities = []
            for start, end, label in entry["label"]:
                entities.append((start, end, label))
            spacy_data.append((text, {"entities": entities}))

    # Write the formatted data to a Python file
    with open(output_py_file, "w") as outfile:
        outfile.write(f"{variable_name} = [\n")
        for text, annotations in spacy_data:
            outfile.write(f"    ({json.dumps(text)}, {json.dumps(annotations)}),\n")
        outfile.write("]\n")


if __name__ == "__main__":
    # Replace these paths with the paths to your input and output files
    test_data_file_path = "test_data2.jsonl"  # Update with your input testing file path
    test_data_output_py_file_path = "test_data.py"    # Update with your desired output Python file path

 #   training_data_file_path = "training_data.jsonl"  # Update with your input training file path
  #  training_data_output_py_file_path = "training_data.py"    # Update with your desired output Python file path

    # Convert test data and save with "TEST_DATA" variable name
    convert_to_spacy_format(test_data_file_path, test_data_output_py_file_path, "TEST_DATA")
    # Convert training data and save with "TRAIN_DATA" variable name
   # convert_to_spacy_format(training_data_file_path, training_data_output_py_file_path, "TRAIN_DATA")

    #print(f"Training data successfully converted and saved to {training_data_output_py_file_path}")
    print(f"Test data successfully converted and saved to {test_data_output_py_file_path}")
