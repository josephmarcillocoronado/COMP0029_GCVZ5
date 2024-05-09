import os
import json
import spacy
from sentence_transformers import SentenceTransformer, util
from entity_matchers import Matchers
from test_data import TEST_DATA
from training_data import TRAIN_DATA
class NamedEntityMatcher:
    """
    A class to match named entities to the most similar file names using a Sentence Transformer model.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2', json_dir=None):
        """
        Initialize the NamedEntityMatcher class.

        Parameters:
        - model_name (str): Name of the pre-trained model to use.
        - json_dir (str): Directory path containing the JSON files to compare. Defaults to None.
        """
        self.model = SentenceTransformer(model_name)
        self.json_dir = json_dir
        self.json_files = []
        if json_dir:
            self.json_files = self._load_json_files(json_dir)

    def set_json_directory(self, json_dir):
        """
        Set or change the directory containing JSON files.

        Parameters:
        - json_dir (str): Directory path containing JSON files.
        """
        self.json_dir = json_dir
        self.json_files = self._load_json_files(json_dir)

    def _load_json_files(self, json_dir):
        """
        Load and clean file names from the JSON directory.

        Parameters:
        - json_dir (str): Directory containing JSON files.

        Returns:
        - A list of cleaned JSON file names.
        """
        def clean_filename(filename):
            base_name = os.path.splitext(filename)[0]  # Strip off the extension
            clean_name = base_name.replace('_', ' ')  # Replace underscores with spaces
            return clean_name

        return [clean_filename(f) for f in os.listdir(json_dir) if f.endswith('.json')]

    def find_best_match(self, entity_embeddings, file_name_embeddings):
        """
        Find the best match for each entity embedding against the file name embeddings.

        Parameters:
        - entity_embeddings (tensor): Embeddings of the entities.
        - file_name_embeddings (tensor): Embeddings of the JSON file names.

        Returns:
        - A dictionary mapping each entity index to a tuple containing the best matching index and cosine similarity score.
        """
        results = {}
        for idx, entity_embedding in enumerate(entity_embeddings):
            cosine_similarities = util.cos_sim(entity_embedding, file_name_embeddings)
            best_match_idx = cosine_similarities.argmax()
            best_score = float(cosine_similarities[0, best_match_idx])  # Convert tensor to float
            results[idx] = (best_match_idx, best_score)

        return results

    def match_entities_to_files(self, named_entities):
        """
        Match named entities to the most similar JSON file names.

        Parameters:
        - named_entities (list of str): List of named entities to compare against JSON file names.

        Returns:
        - A dictionary mapping each named entity to a tuple containing the best matching JSON file name and its cosine similarity score.
        """
        if not self.json_files:
            raise ValueError("No JSON files loaded for comparison.")

        # Encode the JSON file names using the model
        file_name_embeddings = self.model.encode(self.json_files, convert_to_tensor=True)

        # Encode the provided named entities
        entity_embeddings = self.model.encode(named_entities, convert_to_tensor=True)

        # Find the best match for each entity
        match_indices = self.find_best_match(entity_embeddings, file_name_embeddings)

        # Map indices back to their corresponding entity names and JSON file names
        results = {named_entities[entity_idx]: (self.json_files[best_match_idx], score)
                   for entity_idx, (best_match_idx, score) in match_indices.items()}

        return results

    def save_results(self, results, output_file='entity_to_filename_matches.json'):
        """
        Save the matching results to a JSON file.

        Parameters:
        - results (dict): Dictionary containing the results to save.
        - output_file (str): The path to the output JSON file.
        """
        # Convert results to a dictionary suitable for JSON
        results_dict = {entity: {"best_match": match, "cosine_similarity": score}
                        for entity, (match, score) in results.items()}

        with open(output_file, 'w') as f:
            json.dump(results_dict, f, indent=4)

        print(f'Results written to {output_file}')


def load_and_run_ner(nlp_model_dir, test_data, entity_label='POSE'):
    """
    Load the NER model and run it on the provided test data to identify entities with the specified label.

    Parameters:
    - nlp_model_dir (str): Path to the directory containing the NER model.
    - test_data (list of tuples): List of sentences to process, ignoring the annotations.
    - entity_label (str): The target entity label to search for (default is "POSE").

    Returns:
    - A list of named entities extracted from the test data with the specified label.
    """
    # Load the pre-trained NER model using spaCy
    nlp = spacy.load(nlp_model_dir)

    # Extract all named entities matching the specified label from the test data
    entities = []
    for sentence, _ in test_data:
        doc = nlp(sentence)
        for ent in doc.ents:
            if ent.label_ == entity_label:
                entities.append(ent.text)

    return entities


if __name__ == "__main__":
    # Define the path to the NER model directory
    nlp_model_dir = 'nlp_model'

    # Load the NER model and identify entities with the "POSE" label from the test data
    named_entities = load_and_run_ner(nlp_model_dir, TRAIN_DATA)

    # Instantiate the NamedEntityMatcher with an empty JSON directory initially
    matcher = NamedEntityMatcher()

    # Set the JSON directory to load
    matcher.set_json_directory('poses/json')

    # Match the entities labeled "POSE" to the JSON files
    results = matcher.match_entities_to_files(named_entities)

    # Print results to the console, including cosine similarity
    for entity, (match, score) in results.items():
        print(f"Named entity: {entity} -> Best matching file name: {match}, Cosine similarity: {score:.4f}")

    # Save the results to a JSON file
    matcher.save_results(results)
