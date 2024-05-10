def add_full_stop_to_lines(file_path):
    """
    Add a full stop at the end of each line in a file that doesn't already have one.

    Parameters:
    - file_path (str): Path to the file to be modified.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        # Remove any trailing newline characters to check the ending
        stripped_line = line.rstrip('\n')

        # Add a period if not already present and maintain the original line ending
        if not stripped_line.endswith('.'):
            updated_line = stripped_line + '.' + '\n'
        else:
            updated_line = line  # Keep the line as-is

        updated_lines.append(updated_line)

    # Write back all the modified and unmodified lines
    with open(file_path, 'w') as f:
        f.writelines(updated_lines)

if __name__ == '__main__':
    # Provide the path to the file to be processed
    file_path = 'train_test_data/training_data.txt'
    add_full_stop_to_lines(file_path)
