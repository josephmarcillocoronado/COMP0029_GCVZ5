import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Load the CSV data
def load_data_from_csv(file_path):
    """
    Load sentence pairs and labels from a CSV file.

    Parameters:
    - file_path (str): Path to the CSV file.

    Returns:
    - A list of InputExample objects.
    """
    # Replace these with the appropriate column names in your CSV file
    sentence1_col = 'sentence1'
    sentence2_col = 'sentence2'
    label_col = 'label'

    df = pd.read_csv(file_path)

    # Convert DataFrame rows to a list of InputExample objects
    examples = [
        InputExample(texts=[row[sentence1_col], row[sentence2_col]], label=float(row[label_col]))
        for _, row in df.iterrows()
    ]

    return examples

# Fine-tune and save the transformer model
def train_and_save_model(train_data, model_name='all-MiniLM-L6-v2', output_dir='transformer_model', batch_size=8, epochs=1, warmup_steps=100):
    """
    Fine-tune the transformer model and save it to the specified output directory.

    Parameters:
    - train_data (list): A list of InputExample objects for training.
    - model_name (str): The pre-trained model name to use (default: 'all-MiniLM-L6-v2').
    - output_dir (str): The directory where the fine-tuned model will be saved.
    - batch_size (int): Batch size for training (default: 8).
    - epochs (int): Number of epochs for training (default: 1).
    - warmup_steps (int): Number of warm-up steps during training (default: 100).
    """
    # Load the pre-trained transformer model
    model = SentenceTransformer(model_name)

    # Prepare the DataLoader for training
    train_dataloader = DataLoader(train_data, shuffle=True, batch_size=batch_size)

    # Use cosine similarity loss for fine-tuning
    train_loss = losses.CosineSimilarityLoss(model)

    # Train the model
    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=epochs, warmup_steps=warmup_steps)

    # Save the fine-tuned model
    model.save(output_dir)
    print(f'Model saved to {output_dir}')

# Main function to run the training process
if __name__ == "__main__":
    # Provide the path to your CSV file here
    csv_file_path = 'train_test_data/transformer_sentences.csv'

    # Load training data from the CSV file
    train_examples = load_data_from_csv(csv_file_path)

    # Train and save the model
    train_and_save_model(train_data=train_examples, output_dir='transformer_model', epochs=3, batch_size=16, warmup_steps=100)
