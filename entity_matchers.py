# matchers.py
import os
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.util import filter_spans
from spacy.tokens import Span

def get_patterns_from_directory(directory_path):
    """
    Create spaCy matcher patterns based on filenames in a directory and log the results to a text file.

    Parameters:
        directory_path (str): Path to the directory containing JSON files.

    Returns:
        List of spaCy matcher patterns.
    """
    patterns = []
    with open("patterns_output.txt", "w") as log_file:  # Output file for patterns
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                # Strip the .json extension and replace underscores with spaces
                entity_name = filename[:-5].replace("_", " ").lower()
                # Create a pattern that matches each word
                pattern = [{"LOWER": token} for token in entity_name.split()]
                patterns.append(pattern)
                # Log the pattern to the output file
                log_file.write(f"Pattern for '{filename}': {pattern}\n")

    return patterns


class Matchers:
    @staticmethod
    @Language.component("poses_entity_matcher")
    def poses_entity_matcher(doc):
        matcher = Matcher(doc.vocab)
        poses_directory = "poses/json"  # Update with the directory path
        poses_patterns = get_patterns_from_directory(poses_directory)
        matcher.add("POSE", poses_patterns)
        matches = matcher(doc)
        spans = [doc[start:end] for _, start, end in matches]
        filtered_spans = filter_spans(spans)

        # Collect existing entities that do not overlap with matcher spans
        existing_ents = [ent for ent in doc.ents if not any(
            ent.start <= span.start < ent.end or ent.start < span.end <= ent.end for span in filtered_spans)]

        # Add matcher-found spans as new entities
        new_ents = [Span(doc, span.start, span.end, label="POSE") for span in filtered_spans]

        # Combine and update Doc.ents
        doc.ents = existing_ents + new_ents

        return doc
    @staticmethod
    @Language.component("gesture_entity_matcher")
    def poses_entity_matcher(doc):
        matcher = Matcher(doc.vocab)
        gestures_directory = "gestures/json"  # Update with the directory path
        gesture_patterns = get_patterns_from_directory(gestures_directory)
        matcher.add("GESTURE", gesture_patterns)
        matches = matcher(doc)
        spans = [doc[start:end] for _, start, end in matches]
        filtered_spans = filter_spans(spans)

        # Collect existing entities that do not overlap with matcher spans
        existing_ents = [ent for ent in doc.ents if not any(
            ent.start <= span.start < ent.end or ent.start < span.end <= ent.end for span in filtered_spans)]

        # Add matcher-found spans as new entities
        new_ents = [Span(doc, span.start, span.end, label="GESTURE") for span in filtered_spans]

        # Combine and update Doc.ents
        doc.ents = existing_ents + new_ents

        return doc

    @staticmethod
    @Language.component("modes_entity_matcher")
    def modes_entity_matcher(doc):
        matcher = Matcher(doc.vocab)
        modes_directory = "modes"  # Update with the directory path
        modes_patterns = get_patterns_from_directory(modes_directory)
        matcher.add("MODE", modes_patterns)
        matches = matcher(doc)
        spans = [doc[start:end] for _, start, end in matches]
        filtered_spans = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in filtered_spans:
                retokenizer.merge(span)
                span.label_ = "MODE"  # Overwrites any existing entity label

        return doc
