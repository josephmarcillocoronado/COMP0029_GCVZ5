import spacy
from spacy import displacy
from spacy.training import Example
from test_data import TEST_DATA

def test_and_save_combined_visualization(model_path, test_data, output_html="combined_entities_and_dependencies.html"):
    """
    Load a trained spaCy model, run it on test data, and save a combined visualization file.

    Parameters:
        model_path (str): Path to the folder containing the trained model.
        test_data (list): List of tuples, where each tuple contains a text and expected entities.
        output_html (str): Name of the output HTML file.
    """
    # Load the trained model
    nlp = spacy.load(model_path)

    # Initialize HTML structure
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>NER and Dependency Visualization</title>
        <style>/* Add some custom styles if desired */</style>
    </head>
    <body>
    <h1>Combined NER and Dependency Parsing Visualizations</h1>
    """

    for index, (text, _) in enumerate(test_data):
        doc = nlp(text)

        # Render named entities and append to the combined HTML
        entity_html = displacy.render(doc, style="ent", jupyter=False)
        html_content += f"<h2>Entities for Test Sentence {index + 1}</h2>"
        html_content += entity_html

        # Render dependency parsing and append to the combined HTML
        dep_html = displacy.render(doc, style="dep", jupyter=False)
        html_content += f"<h2>Dependencies for Test Sentence {index + 1}</h2>"
        html_content += dep_html

    # Close HTML structure
    html_content += "</body></html>"

    # Save the combined visualization to an HTML file
    with open(output_html, "w") as file:
        file.write(html_content)

    print(f"Combined visualization file '{output_html}' saved.")
from test_data import TEST_DATA

def evaluate_ner_model(model_path, test_data):
    """
    Evaluate a trained spaCy NER model using test data and print performance scores.

    Parameters:
        model_path (str): Path to the folder containing the trained model.
        test_data (list): List of tuples, where each tuple contains a text and a dictionary of expected entities.
    """
    # Load the trained model
    nlp = spacy.load(model_path)

    # Create a list to store Example objects for evaluation
    examples = []

    # Convert test data to spaCy Example objects
    for text, annotations in test_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        examples.append(example)

    # Evaluate the NER component on the test examples
    scorer = nlp.evaluate(examples)

    # Print evaluation metrics
    print("NER Evaluation Results:")
    print(f"Precision: {scorer['ents_p']:.3f}")
    print(f"Recall: {scorer['ents_r']:.3f}")
    print(f"F1 Score: {scorer['ents_f']:.3f}")
    print(f"Number of Tokenization Issues: {scorer['token_acc']:.3f}")

if __name__ == "__main__":
    # Path to the folder containing the trained model
    model_directory = "nlp_model"  # Replace with your trained model's path

    # Run the combined visualization function using the imported test data
    test_and_save_combined_visualization(model_directory, TEST_DATA)
    evaluate_ner_model(model_directory, TEST_DATA)