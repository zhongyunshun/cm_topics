# Read the text data from the file or source
# The .. navigates one level up from the scripts directory to /Users/yunshunzhong/VirtualEnvironments/pythonProject/tcm
# GCP running directory
# input_directory_with_ref = "../tcm/collected_dataset/downloaded_papers/txt/all_txt"
# input_directory_without_ref = "../tcm/collected_dataset/downloaded_papers/txt/all_txt_without_ref"
# output_directory_with_ref = "../tcm/collected_dataset/cleaned_papers_with_ref"
# output_directory_without_ref = "../tcm/collected_dataset/cleaned_papers_without_ref"

# mac directory
input_directory_with_ref = '../../tcm/collected_dataset/additional_data/additional_txt'
input_directory_without_ref = '../../tcm/collected_dataset/additional_data/additional_txt_without_ref'
# output_directory_with_ref = '/Users/yunshunzhong/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/PhD Project/Prompt Engineering/Experiment/cleaned_papers_with_ref'
output_directory_without_ref = '../../tcm/collected_dataset/additional_data/cleaned_papers_without_ref'


import sys
from tcm.preprocessing.journal_paper_data_cleaning_functions import *

# Create output_directory if it doesn't exist
# if not os.path.exists(output_directory_with_ref):
#     os.makedirs(output_directory_with_ref)

if not os.path.exists(output_directory_without_ref):
    os.makedirs(output_directory_without_ref)

# Find if any non utf-8-sig files exists. If so, terminate program
non_utf8_sig_files, count = find_non_utf8_sig_files(input_directory_with_ref)
if count != 0:
    print(f"\nTotal files not encoded in utf-8-sig: {count}")
    print(f"Files not encoded in utf-8-sig: {non_utf8_sig_files}")
    sys.exit()
else:
    print(f"\nAll files are encoded in utf-8-sig")

# Clean references from the text
remove_references_from_files(input_directory_with_ref, input_directory_without_ref)

# Loop through each file in input_directory
for file_name in os.listdir(input_directory_without_ref):
    if not file_name.endswith(".txt"):
        continue

    # Get the full path of the input file
    input_file_path = os.path.join(input_directory_without_ref, file_name)

    # Get the output file path with the same name as the input file + english_line
    output_file_path = os.path.join(output_directory_without_ref, file_name)

    # Open the input file and read its contents line by line
    with open(input_file_path, "r", encoding="utf-8-sig") as input_file:
        lines = input_file.readlines()


    # If sentence is not in `unique_sentences`, add in to cleaned_sentences
    cleaned_lines_in_txt_file = []

    # just for debugging purpose
    line_num = 0

    # Filter out non-English sentences and write the English sentences to the output file
    with open(output_file_path, "w", encoding="utf-8-sig") as output_file:
        for line in lines:

            line_num += 1

            # Remove leading and trailing whitespace
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Try to detect the language of the line, an empty string is a falsy value in Python
            line = filter_nonenglish_text(line)
            if not line:
                continue

            # Use the sub() method to replace all website links with an empty string
            line = remove_website_links(line)

            # Split the line into sentences
            sentences = split_string_by_punctuation(line)

            # Remove leading and trailing whitespace from each sentence
            # Only retain sentences with length > 10
            sentences = filter_too_short_sentences(sentences)

            # Concatenate sentences (a list of strings) back to one line
            cleaned_line = ' '.join(sentences)


            # Add a cleaned line to a list of cleaned lines
            cleaned_lines_in_txt_file.append(cleaned_line)

        # print(line_num)

        # After data cleaning, write the cleaned sentences to the output file
        for line in cleaned_lines_in_txt_file:
            output_file.write(line + "\n")

# report the word count before and after data cleaning
result_df = word_count_report(input_directory_without_ref, output_directory_without_ref)
result_df
