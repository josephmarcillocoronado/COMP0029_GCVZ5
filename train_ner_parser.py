import spacy
from spacy.training import Example
from training_data import TRAIN_DATA
from test_data import TEST_DATA
from entity_matchers import Matchers
import matplotlib.pyplot as plt
import os

def add_ner_labels(nlp, train_data):
    # Retrieve the NER component
    ner = nlp.get_pipe("ner")
    for _, annotations in train_data:
        for ent in annotations["entities"]:
            ner.add_label(ent[2])

def prepare_examples(nlp, data):
    return [Example.from_dict(nlp.make_doc(text), annots) for text, annots in data]

def calculate_moving_average(scores, window_size):
    """
    Calculate the moving average over a given window size.

    Parameters:
    - scores (list of tuples): A list of (iteration, score) pairs.
    - window_size (int): The number of previous scores to consider in the average.

    Returns:
    - moving_avg (list of tuples): A list of (iteration, average_score) pairs.
    """
    moving_avg = []
    for i in range(len(scores)):
        start_index = max(0, i - window_size + 1)  # Ensure the starting index is non-negative
        window = [score for _, score in scores[start_index:i + 1]]
        avg = sum(window) / len(window)
        moving_avg.append((scores[i][0], avg))
    return moving_avg

def train_and_evaluate_live(nlp, train_examples, test_examples, iterations, drop, range_size=10):
    """
    Train the spaCy model on the training data and evaluate on the test data every 10 iterations.

    Parameters:
    - nlp (spacy model): The spaCy model to train.
    - train_examples (list): The training data.
    - test_examples (list): The test data.
    - iterations (int): Number of training iterations.
    - drop (float): Dropout rate.
    - range_size (int): The size of the window used for calculating the moving average.

    Returns:
    - f1_scores (list): F1 scores across iterations.
    - accuracy_scores (list): Accuracy scores across iterations.
    - recall_scores (list): Recall scores across iterations.
    - moving_avg_scores (list): Moving average F1 scores.
    - best_avg_iteration (int): Iteration with the best moving average score.
    - best_avg_score (float): The best moving average score.
    """
    optimizer = nlp.resume_training()  # Initialize the optimizer for training
    f1_scores = []
    accuracy_scores = []
    recall_scores = []

    for i in range(iterations):
        losses = {}
        nlp.update(train_examples, drop=drop, losses=losses, sgd=optimizer)

        # Evaluate on the test data every 10 iterations
        if i % 10 == 0:
            scorer = nlp.evaluate(test_examples)
            f1_score = scorer["ents_f"]
            accuracy = scorer["ents_p"]
            recall = scorer["ents_r"]

            f1_scores.append((i, f1_score))
            accuracy_scores.append((i, accuracy))
            recall_scores.append((i, recall))

            print(f"Iteration {i}, Losses: {losses}, Test F1 Score: {f1_score:.3f}, Accuracy: {accuracy:.3f}, Recall: {recall:.3f}")

    # Calculate the moving average F1 score over the last `range_size` iterations
    moving_avg_scores = calculate_moving_average(f1_scores, range_size)

    # Find the iteration with the best moving average score
    best_avg_iteration, best_avg_score = max(moving_avg_scores, key=lambda x: x[1])

    return f1_scores, accuracy_scores, recall_scores, moving_avg_scores, best_avg_iteration, best_avg_score

def plot_metric_combined(scores_dict, metric_name, ylabel):
    for drop, scores in scores_dict.items():
        iterations, metric_values = zip(*scores)
        plt.plot(iterations, metric_values, label=f"Dropout {drop}")

    plt.xlabel("Iterations")
    plt.ylabel(ylabel)
    plt.title(f"{metric_name} vs Iterations per Dropout Rate")
    plt.legend()
    plt.grid(True)
    plt.show()

def train_ner_multiple_drops(train_data, test_data, output_path, iterations, dropout_values):
    f1_scores_dict = {}
    accuracy_scores_dict = {}
    recall_scores_dict = {}
    moving_avg_dict = {}
    best_model = None
    best_avg_score = 0
    best_avg_dropout = None
    best_avg_iteration = 0

    for drop in dropout_values:
        # Load and configure the base model from scratch for each dropout rate
        nlp = spacy.load("en_core_web_md")

        # Prepare training and test examples
        train_examples = prepare_examples(nlp, train_data)
        test_examples = prepare_examples(nlp, test_data)

        # Customize the pipeline
        keep_pipes = {"ner", "parser", "tok2vec"}
        for pipe_name in list(nlp.pipe_names):
            if pipe_name not in keep_pipes:
                nlp.remove_pipe(pipe_name)
        nlp.remove_pipe("senter")
        nlp.add_pipe("modes_entity_matcher", last=True)
        nlp.add_pipe("poses_entity_matcher", last=True)

        # Add NER labels
        add_ner_labels(nlp, train_data)

        # Train and evaluate with this dropout rate
        f1_scores, accuracy_scores, recall_scores, moving_avg_scores, best_iter, avg_score = train_and_evaluate_live(nlp, train_examples, test_examples, iterations, drop)
        f1_scores_dict[drop] = f1_scores
        accuracy_scores_dict[drop] = accuracy_scores
        recall_scores_dict[drop] = recall_scores
        moving_avg_dict[drop] = moving_avg_scores

        # Update the best model based on the highest average F1 score
        if avg_score > best_avg_score:
            best_avg_score = avg_score
            best_model = nlp
            best_avg_dropout = drop
            best_avg_iteration = best_iter

    # Save the best-performing model
    if best_model:
        best_model.to_disk(output_path)
        print(f"The best model was saved with a dropout rate of {best_avg_dropout} at iteration {best_avg_iteration}, based on the highest moving average F1 score.")

    # Plot combined graphs for each metric
    plot_metric_combined(f1_scores_dict, "F1 Score", "F1 Score")
    plot_metric_combined(accuracy_scores_dict, "Accuracy", "Accuracy")
    plot_metric_combined(recall_scores_dict, "Recall", "Recall")

    # Plot the moving average F1 scores for each dropout rate
    plot_metric_combined(moving_avg_dict, "Moving Average F1 Score (Last 10 Iterations)", "Moving Average F1 Score")

def main(output_dir, iterations=1000, dropout_values=[0.1, 0.3, 0.5]):
    # Prepare training and test data
    train_data = TRAIN_DATA
    test_data = TEST_DATA

    # Train with varying dropout rates and plot the results
    output_dir = os.path.abspath(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    train_ner_multiple_drops(train_data, test_data, output_dir, iterations, dropout_values)

if __name__ == "__main__":
    output_folder = "nlp_model"  # Update with your desired folder path
    main(output_folder, iterations=300, dropout_values=[0.3])
