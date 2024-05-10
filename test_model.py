import spacy
from spacy import displacy
from spacy.training import Example
from train_test_data.test_data import TEST_DATA


def save_ner_visualization(nlp_model, test_data, output_html):
    """
    Use a loaded spaCy model, run it on test data, and save a combined NER visualization file.

    Parameters:
        nlp_model (Language): A spaCy language model loaded in memory.
        test_data (list): List of tuples, where each tuple contains a text and expected entities.
        output_html (str): Name of the output HTML file for NER visualization.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>NER Visualization</title>
    </head>
    <body>
    <h1>NER Visualizations</h1>
    """

    for index, (text, _) in enumerate(test_data):
        doc = nlp(text)
        entity_html = displacy.render(doc, style="ent", jupyter=False)
        html_content += f"<h2>Entities for Test Sentence {index + 1}</h2>"
        html_content += entity_html

    html_content += "</body></html>"

    with open(output_html, "w") as file:
        file.write(html_content)

    print(f"NER visualization file '{output_html}' saved.")


def save_dependency_visualization(nlp_model, test_data, output_html):
    """
    Use a loaded spaCy model, run it on test data, and save a combined dependency parsing visualization file.

    Parameters:
        nlp_model (Language): A spaCy language model loaded in memory.
        test_data (list): List of tuples, where each tuple contains a text and expected entities.
        output_html (str): Name of the output HTML file for dependency parsing visualization.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Dependency Parsing Visualization</title>
    </head>
    <body>
    <h1>Dependency Parsing Visualizations</h1>
    """

    for index, (text, _) in enumerate(test_data):
        doc = nlp(text)
        dep_html = displacy.render(doc, style="dep", jupyter=False)
        html_content += f"<h2>Dependencies for Test Sentence {index + 1}</h2>"
        html_content += dep_html

    html_content += "</body></html>"

    with open(output_html, "w") as file:
        file.write(html_content)

    print(f"Dependency parsing visualization file '{output_html}' saved.")


def evaluate_ner_model(nlp_model, test_data):
    """
    Evaluate a trained spaCy NER model using test data and print performance scores.

    Parameters:
        nlp_model (Language): A spaCy language model loaded in memory.
        test_data (list): List of tuples, where each tuple contains a text and a dictionary of expected entities.
    """
    examples = []
    for text, annotations in test_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        examples.append(example)

    scorer = nlp.evaluate(examples)

    print("NER Evaluation Results:")
    print(f"Precision: {scorer['ents_p']:.3f}")
    print(f"Recall: {scorer['ents_r']:.3f}")
    print(f"F1 Score: {scorer['ents_f']:.3f}")
    print(f"Number of Tokenization Issues: {scorer['token_acc']:.3f}")


if __name__ == "__main__":
    # Load the trained model once
    model_directory = "nlp_model"  # Replace with your trained model's path
    nlp = spacy.load(model_directory)

    # Save NER and dependency parsing visualizations with all components active
    save_ner_visualization(nlp, TEST_DATA, "ner_entities.html")
    save_dependency_visualization(nlp, TEST_DATA, "dependency_parsing.html")

    # Temporarily disable NER and visualize matcher-only entities
    with nlp.select_pipes(disable=["ner"]):
        save_ner_visualization(nlp, TEST_DATA, "matcher_only_entities.html")
        save_dependency_visualization(nlp, TEST_DATA, "matcher_only_dependency.html")


    # Evaluate the NER model with all components active
    evaluate_ner_model(nlp, TEST_DATA)

    doc = nlp("Perform the thwip mode.")
    for ent in doc.ents:
        print(f"Entity: {ent.text}, Label: {ent.label_}")

