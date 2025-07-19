'''
Need to Deduplicate sentences after data cleaning for all txt files are done and merged into one file
    # Initialize a set to keep track of unique sentences
    unique_sentences = set()
    # Remove leading and trailing whitespace from each sentence
            # Only retain sentences with length > 10
            sentences = [s.strip() for s in sentences if len(s) > 10 if s not in unique_sentences]

            # set.update() adds elements from one or more iterable objects (such as sets, lists, or tuples) to the set.
            # De-duplicate sentences
            unique_sentences.update(sentences)
'''
import pickle
import re
import random

import langdetect
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import os
import numpy as np
import pandas as pd
import chardet
from transformers import BertTokenizer


# def find_non_utf8_sig_files(directory: str) -> tuple[list[str], int]:
def find_non_utf8_sig_files(directory):
    """
       Find all text files in a folder whose encoding is not 'utf-8-sig'.

       This function searches for text files in the specified folder, and then
       checks if their encoding is 'utf-8-sig'. If not, the file path is added
       to a list that is returned at the end of the function.

       Args:
           folder_path (str): The path to the folder containing the text files.

       Returns:
           List[str]: A list of file paths with non-'utf-8-sig' encoding.
    """
    non_utf8_sig_files = []
    count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    detected_encoding = chardet.detect(file_content)['encoding']
                    if detected_encoding != 'UTF-8-SIG':
                        non_utf8_sig_files.append(file_path)
                        count += 1
                        print(f"File: {file_path}, Encoding: {detected_encoding}")

    return non_utf8_sig_files, count


def remove_website_links(line: str) -> str:
    """
    Remove website links from a string.

    Args:
        line: A string containing website links.

    Returns:
        A string with website links removed.

    """
    # Define a regular expression pattern to match website links
    # web_regex = r'(http[s]?://|www\.)' \
    #             r'(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' \
    #             r'(?:,\s*)?'
    web_regex = r'http\S+|www.\S+'
    # Use the sub() method to replace all website links with an empty string
    filtered_line = re.sub(web_regex, '', line)

    return filtered_line


def split_string_by_punctuation(line):
# def split_string_by_punctuation(line: str) -> list[str]:
    """
    Splits a given string into a list of strings using terminal punctuation marks (., !, ?, or :) as delimiters.

    This function utilizes regular expression patterns to ensure that abbreviations, honorifics,
    and certain special cases are not considered as sentence delimiters.

    Args:
        line (str): The input string to be split into sentences.

    Returns:
        list: A list of strings representing the sentences obtained after splitting the input string.

    Notes:
        - Non-capturing group is used to exclude abbreviations (e.g., "e.g.", "i.e.", "U.S.A.", "Mr.", "Mrs.", "Dr.",
        "Dept.", "Univ.", "et al.")
        - If a point is not followed by white space and a capital, the preceding word is an abbreviation.
        - If the word has a capital as first letter and has at most 4 letters and is followed by a point, it is also an abbreviation.
        - In all other cases the point is interpreted as ending a sentence.
        - (?=\S): assert that the first character of any match is not white space
        - (?:  |    |   )*: a non-capturing group with three alternate patterns. This can repeat 0 or more times
        - [A-Z][a-z]{0,3}\.: one of the alternatives: a capital followed by at most three lower case letters
        and then a point.
        - [^.?!;:]: one of the alternatives: a character that is not one of .?!;:
        - \.(?!\s+[A-Z]): a point that is not followed by white space and a capital letter
        - .?: any character -- if there is still one. If there is one, we know it is one of .?!;: (otherwise the
        second alternative above would still have been used). If not, we are at the end of the input.
        - a non-capturing group still matches text, it just cannot be referenced with a back reference.
        The word "capture" refers to creating a group for it, not to "matching".
        Using a non-capturing group (?: ...) in this case doesn't mean that the matched content won't be returned.
        It means that the matched content won't be treated as a separate capturing group in the final result.
        - Using a non-capturing group in this case does not prevent the matched content from being returned;
        it only affects how the matched content is organized in the final result.
    """

    punct_regex = r"(?=\S)(?:[A-Z][a-z]{0,3}\.|[^.?!;:]|\.(?!\s+[A-Z]))*.?"
    return re.findall(punct_regex, line)


def filter_nonenglish_text(line: str) -> str:
    """
    Filter out non-English sentences from a string.

    Args:
        line: A string containing one or more sentences.

    Returns:
        A filtered string containing only English sentences with a probability of at least 0.99.

    Raises:
        LangDetectException: If the language of the input line cannot be detected.

    """
    # Try to detect the language of the line
    try:
        lang = detect(line)
    except LangDetectException:
        lang = None

    # Only retain English text with a probability of at least 0.99
    if lang != "en" or (langdetect.detect_langs(line)[0].prob < 0.99):
        return ""
    else:
        return line


# punct_regex = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!|:)\s")


# def filter_reference_in_text(line: str) -> (str, bool):
#     """
#     Filter out reference text from a string.
#
#     Args:
#         line: A string that may contain reference text.
#
#     Returns:
#         A filtered string with any reference text removed.
#
#     """
#     # Define regular expression patterns to match variants of Reference
#     # reference_regex1 = r"(?<=References).*"
#     # reference_regex2 = r"(?<=References ).*"
#     # reference_regex3 = r"(?<=references).*"
#     #
#     # # Filter out anything after Reference
#     # if re.search(reference_regex1, line) or re.search(reference_regex2, line) or re.search(reference_regex3, line):
#     #     return ""
#     # else:
#     #     return line
#     reference_regex = r"(?<=\n)References.*"
#     if re.search(reference_regex, line):
#         return re.sub(reference_regex, "", line, flags=re.DOTALL), True
#     return line, False


def remove_references_from_files(input_directory: str, output_directory: str) -> None:
    """
    Removes references sections from text files in a directory and saves the cleaned content to a new directory.

    Args:
        input_directory (str): The path of the input directory containing the text files.
        output_directory (str): The path of the output directory where cleaned files will be saved.
    """
    for file_name in os.listdir(input_directory):
        if not file_name.endswith(".txt"):
            continue
        input_file_path = os.path.join(input_directory, file_name)
        output_file_path = os.path.join(output_directory, file_name)
        reference_regex = r"(?<=\n)[Rr]eferences[\s\S]*"
        # with open(input_file_path, "r", encoding="utf8") as input_file:
        with open(input_file_path, "r", encoding="utf-8-sig") as input_file:
            content = input_file.read()
            content = re.sub(reference_regex, "", content, flags=re.DOTALL)
        # with open(output_file_path, "w", encoding="utf8") as output_file:
        with open(output_file_path, "w", encoding="utf-8-sig") as output_file:
            output_file.write(content)


# def filter_too_short_sentences(sentences: list[str]) -> list[str]:
def filter_too_short_sentences(sentences):
    """
    Filter a list of sentences by removing leading and trailing whitespace and only retaining sentences with length > 10.

    Args:
        sentences: A list of sentences.

    Returns:
        A filtered list of sentences.

    """
    # Remove leading and trailing whitespace from each sentence and only retain sentences with length > 10
    filtered_sentences = [s.strip() for s in sentences if len(s) > 10]

    return filtered_sentences


def word_count_report(input_directory, output_directory):
    file_names = []
    input_word_counts = []
    # Loop through each file in input_directory
    for file_name in os.listdir(input_directory):
        if file_name.endswith(".txt"):
            # Add the file name to the list of file names
            file_names.append(file_name)
            # Get the full path of the input file
            input_file_path = os.path.join(input_directory, file_name)

            # Open the file and read its contents
            with open(input_file_path, "r", encoding="utf-8-sig") as file:
                file_contents = file.read()

            # Split the contents into words and count them
            word_count = len(file_contents.split())
            input_word_counts.append(word_count)

    output_word_counts = []
    # Loop through each file in input_directory
    for file_name in os.listdir(output_directory):
        if file_name.endswith(".txt"):
            # Get the output file path with the same name as the input file + english_line
            output_file_path = os.path.join(output_directory, file_name)

            # Open the file and read its contents
            with open(output_file_path, "r", encoding="utf-8-sig") as file:
                file_contents = file.read()

            # Split the contents into words and count them
            word_count = len(file_contents.split())
            output_word_counts.append(word_count)

    word_diff = []
    for i in range(len(input_word_counts)):
        word_diff.append(input_word_counts[i] - output_word_counts[i])

    for file_name, input_word_count, output_word_count in zip(file_names, input_word_counts, output_word_counts):
        print(f"The input file name is {file_name}.")
        print(f"It contains {input_word_count} words before data cleaning.")
        print(f"It contains {output_word_count} words after data cleaning.")
        print(f"The difference is {word_diff} words.")
        print(f"----------------------------------------")

        # save the results to a Pandas DataFrame
        df = pd.DataFrame(
            {"file_name": file_names, "input_word_count": input_word_counts, "output_word_count": output_word_counts,
             "word_diff": word_diff})

    print(f"The number of words removed on average is {np.mean(word_diff)} words.")
    print(f"The percentage of words removed on average is {np.mean(word_diff) / np.mean(input_word_counts) * 100}%.")

    return df

def concatenate_strings(input_list, tokenizer, max_tokens):
    concatenated_strings = []
    current_string = ""
    current_tokens = 0

    for text in input_list:
        token_length = len(tokenizer.tokenize(text))
        if current_tokens + token_length <= max_tokens:
            current_string += " " + text
            current_tokens += token_length
        else:
            concatenated_strings.append(current_string.strip())
            current_string = text
            current_tokens = token_length

    if current_string:
        concatenated_strings.append(current_string.strip())

    return concatenated_strings

def txt2list(input_directory, output_directory, output_file_name):
    """
    This function/script can output a list of strings that can be used as input for the pre-training model.
    By changing input_directory, this function can output two lists of strings:
    1. cleaned_papers_without_ref with original sentence length
    2. cleaned_papers_with_ref
    """
    input_text = []
    for file_name in os.listdir(input_directory):
        if not file_name.endswith(".txt"):
            continue

        # Get the full path of the input file
        input_file_path = os.path.join(input_directory, file_name)
        with open(input_file_path, "r", encoding="utf-8-sig") as input_file:
            lines = input_file.readlines()
            input_text.extend(lines)

    file_path = os.path.join(output_directory, output_file_name)

    with open(file_path, "wb") as file:
        pickle.dump(input_text, file)


def mask_tokens(inputs, tokenizer, mlm_probability=0.15):
    """
    Mask 15% of all WordPiece tokens in each sequence at random, as described in the BERT paper.

    Args:
        inputs (dict): A dictionary of input tensors containing the "input_ids", "token_type_ids", and "attention_mask".
        tokenizer (BertTokenizer): The BERT tokenizer used to encode the input sequences.
        mlm_probability (float): The probability of replacing a token with the [MASK] token.

    Returns:
        A dictionary of input tensors with masked tokens.
    """
    masked_input_ids = inputs.clone()

    for i in range(masked_input_ids.shape[0]):
        # Get a list of indices of WordPiece tokens to be masked
        mask_indices = [j for j in range(len(masked_input_ids[i]))
                        if masked_input_ids[i][j] != tokenizer.cls_token_id and
                        masked_input_ids[i][j] != tokenizer.sep_token_id and random.random() < mlm_probability]
        vocabulary_list = list(tokenizer.vocab.values())
        for index in mask_indices:
            # Randomly choose one of three options: mask token, replace with random token, or keep unchanged
            if random.random() < 0.8:
                masked_input_ids[i][index] = tokenizer.mask_token_id
            elif random.random() < 0.5:
                masked_input_ids[i][index] = random.choice(vocabulary_list)
            else:
                continue

    return masked_input_ids
