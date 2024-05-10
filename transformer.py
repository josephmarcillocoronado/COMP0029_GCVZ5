import os
import json
from sentence_transformers import SentenceTransformer, util


class NamedEntityMatcher:
    """
    A class to match named entities to the most similar file names and controls using a Sentence Transformer model.
    """

    def __init__(self, model_path='transformer_model', similarity_threshold=0.8):
        """
        Initialize the NamedEntityMatcher class.

        Parameters:
        - model_path (str): Path to the fine-tuned model directory to use.
        - similarity_threshold (float): Minimum cosine similarity score for a match to be considered.
        """
        self.model = SentenceTransformer(model_path)  # Load the fine-tuned model
        self.similarity_threshold = similarity_threshold

    def find_best_match(self, entity_embeddings, target_embeddings):
        """
        Find the best match for each entity embedding against the target embeddings.

        Parameters:
        - entity_embeddings (tensor): Embeddings of the entities.
        - target_embeddings (tensor): Embeddings of the target items (file names or controls).

        Returns:
        - A dictionary mapping each entity index to a tuple containing the best matching index and cosine similarity score.
        """
        results = {}
        for idx, entity_embedding in enumerate(entity_embeddings):
            cosine_similarities = util.cos_sim(entity_embedding, target_embeddings)
            best_match_idx = cosine_similarities.argmax()
            best_score = float(cosine_similarities[0, best_match_idx])  # Convert tensor to float

            # Only consider matches that meet or exceed the similarity threshold
            if best_score >= self.similarity_threshold:
                results[idx] = (best_match_idx, best_score)

        return results

    def load_controls_from_json(self, directory, mode_name):
        """
        Load control values from a specific JSON file representing the mode.

        Parameters:
        - directory (str): Path to the directory containing the mode file.
        - mode_name (str): The base name of the mode file to load.

        Returns:
        - List of control values from the specified mode file.
        """
        json_file_path = os.path.join(directory, f"{mode_name}.json")
        if not os.path.exists(json_file_path):
            raise ValueError(f"JSON file for mode '{mode_name}' does not exist in the directory.")

        with open(json_file_path, 'r') as f:
            data = json.load(f)

        return [pose['control'] for pose in data.get('poses', [])]

    def match_actions_to_controls(self, directory, mode_name, actions):
        """
        Match action entities to the most similar control values in a specific JSON file.

        Parameters:
        - directory (str): Path to the directory containing the mode file.
        - mode_name (str): The base name of the mode file to compare against.
        - actions (list of str): List of actions to compare against control values.

        Returns:
        - A dictionary mapping each action to a tuple containing the best matching control and its cosine similarity score.
        """
        all_controls = self.load_controls_from_json(directory, mode_name)
        if not all_controls:
            raise ValueError(f"No control values found in the JSON file for mode '{mode_name}'.")

        # Encode the control values using the model
        control_embeddings = self.model.encode(all_controls, convert_to_tensor=True)

        # Encode the provided actions
        action_embeddings = self.model.encode(actions, convert_to_tensor=True)

        # Find the best match for each action
        match_indices = self.find_best_match(action_embeddings, control_embeddings)

        # Map indices back to their corresponding action names and control values
        results = {actions[action_idx]: (all_controls[control_idx], score)
                   for action_idx, (control_idx, score) in match_indices.items()}

        return results


if __name__ == "__main__":
    model_path = 'transformer_model'

    # Instantiate the NamedEntityMatcher with the model
    matcher = NamedEntityMatcher(model_path=model_path, similarity_threshold=0.8)

    # Case 1: Match actions to controls in a mode file located in the "modes" directory
    mode_directory = 'modes'
    mode_name = 'tetris'
    actions = ['move left', 'hold piece', 'rotate']

    # Match actions to the controls in the specified mode file
    mode_action_results = matcher.match_actions_to_controls(mode_directory, mode_name, actions)

    # Print results for actions in "modes" directory
    print("\nResults for mode actions in 'modes' directory:")
    for action, (match, score) in mode_action_results.items():
        print(f"Action: {action} -> Best matching control: {match}, Cosine similarity: {score:.4f}")

    # Case 2: Match actions to controls in a mode file located in the "poses/json" directory
    poses_directory = 'poses/json'
    poses_name = 'yoga'
    poses_actions = ['warrior', 'mountain', 'downward dog']

    # Match actions to the controls in the specified poses file
    poses_action_results = matcher.match_actions_to_controls(poses_directory, poses_name, poses_actions)

    # Print results for actions in "poses/json" directory
    print("\nResults for pose actions in 'poses/json' directory:")
    for action, (match, score) in poses_action_results.items():
        print(f"Action: {action} -> Best matching control: {match}, Cosine similarity: {score:.4f}")
