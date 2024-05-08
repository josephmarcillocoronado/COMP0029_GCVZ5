import spacy
from spacy.training import Example
import os
from spacy_training_data import TRAIN_DATA
def prepare_training_data():
    # Example training data (dummy)
    train_data = [
        ("Apple is looking at buying U.K. startup for $1 billion", {"entities": [(0, 5, "ORG")]}),
        ("San Francisco considers banning sidewalk delivery robots", {"entities": [(0, 13, "GPE")]}),
    ]
    train_data = TRAIN_DATA
    return train_data

def add_ner_labels(nlp, train_data):
    # Retrieve the NER component
    ner = nlp.get_pipe("ner")

    # Add labels for NER training
    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

def train_ner_only(nlp, train_data, output_path):
    # Add NER labels from the training data
    add_ner_labels(nlp, train_data)

    # Convert data into spaCy's training format
    examples = []
    for text, annots in train_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annots)
        examples.append(example)

    # Initialize the NER model for training if required
    optimizer = nlp.resume_training()

    # Train the NER component only
    for i in range(2000):  # Adjust the number of iterations as necessary
        losses = {}
        nlp.update(examples, drop=0.3, losses=losses, sgd=optimizer)
        print(f"Losses at iteration {i}: {losses}")

    # Save the updated model to disk
    nlp.to_disk(output_path)

def main(output_dir):
    # Load an existing English model (e.g., 'en_core_web_md') or start from blank (e.g., 'en')
    nlp = spacy.load("en_core_web_md")  # Replace with the model you're using

    # Retain only the NER and parser components, and remove other pipes
    keep_pipes = {"ner", "parser", "tok2vec"}
    for pipe_name in list(nlp.pipe_names):
        if pipe_name not in keep_pipes:
            nlp.remove_pipe(pipe_name)
    nlp.remove_pipe("senter")
    # Prepare training data
    train_data = prepare_training_data()

    # Train only the NER component while keeping the parser intact
    output_dir = os.path.abspath(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    train_ner_only(nlp, train_data, output_dir)

if __name__ == "__main__":
    output_folder = "nlp_model"  # Update with your desired folder path
    main(output_folder)
