import os
import time
import openai
import tiktoken as tiktoken

openai.api_key = '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'
model_gpt35 = 'gpt-3.5-turbo-16k-0613' # for tokenization
model_gpt4 = 'gpt-4.1-mini'
max_num_tokens_gpt35 = 128000
def BasicGeneration(userPrompt):
    completion = openai.chat.completions.create(
        model = model_gpt4,
        messages=[

            {"role": "user", "content": userPrompt}
        ]
    )
    return completion.choices[0].message.content

def num_tokens(text: str, model: str = model_gpt4) -> int:
    """Return the number of tokens in a paper."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
def RoleGeneration(userPrompt):
    completion = openai.chat.completions.create(
        model = model_gpt4,
        messages=[
            {"role": "system", "content": "You are a expert in asset and construction management domain."},
            {"role": "user", "content": userPrompt}
        ]
    )
    return completion.choices[0].message.content

input_directory = '../../tcm/collected_dataset/additional_data/cleaned_papers_without_ref/'
output_directory = '../../tcm/collected_dataset/additional_data/summarized_topics/'

# List to store filenames that exceed the max token count
filenames_exceeding_max_tokens = []

# Iterate through each file in the folder
for filename in os.listdir(input_directory):
    if filename.endswith('.txt'):
        print("Summarizing file", filename)
        with open(os.path.join(input_directory, filename), 'r', encoding='utf-8', errors='replace') as file:
            # Read the file content
            file_contents = file.read()

            # if any paper that have a token count greater than the specified max_num_tokens_gpt35, skip summarization
            # and record the names of papers in a file
            if num_tokens(file_contents, model_gpt35) > max_num_tokens_gpt35:
                print(filename)
                filenames_exceeding_max_tokens.append(filename)
                continue

            # Create a prompt for the summarization
            base_prompt = f"Summarize the main topics in less than 10 keywords in the following journal paper in asset and construction management: {file_contents}."
            base_prompt_cot = f"Summarize the main topics in less than 10 keywords in the following journal paper in asset and construction management: {file_contents}. Think step by step."
            base_prompt_role = f"Summarize the main topics in less than 10 keywords in the following journal paper in asset and construction management: {file_contents}."
            base_prompt_role_cot = f"Write background and introduction part for the research proposal named 'Build a Question Answering System for TRCA's Technical Reports Using Large Language Models' according to this journal paper: {file_contents}. Think step by step."

            feedback_prompt_role_cot = f"Please identify and summarize the main topics of the following journal paper focused on asset and construction management. " \
                                    f"Use up to 10 keywords, each consisting of no more than 3 words, and separate the keywords with commas. " \
                                    f"Topics example: 'topics:  Construction project management, Unstructured data, " \
                                    f"Semantic network analysis, Knowledge capture and re-use, Social BIM, " \
                                    f"Blockmodeling, energy management' \n" \
                                    f"Paper content: {file_contents}."


            # one_shot_prompt = f"""
            # Journal paper: This study explores the performance regime of different classification algorithms as they are applied to the analysis of asphalt pavement deterioration data. The aim is to examine how different algorithms deal with the typically limited and low-quality data sets in the infrastructure asset management domain, and whether better configurations of relevant algorithms help overcome these limitations. Furthermore, the emphasis on choosing the most affordable attributes (e.g., temperature and precipitation levels) makes the results reproducible to smaller municipalities. This analysis used the data of more than 3,000 examples of road sections, which were retrieved from the Long-Term Pavement Performance (LTPP) database. The algorithms examined in this study include two types of decision trees, naïve Bayes classifier, naïve Bayes coupled with kernels, logistic regression, k-nearest neighbors (k-NN), random forest, and gradient boosted trees. The performance of these algorithms is compared, and their weaknesses and strengths are discussed. They were all applied to predict the deterioration of pavement condition index (PCI). Of specific importance is the positive role of ensemble learning. It is shown how using higher efficiencies by using ensemble learning can compensate for data shortcomings. The accuracy of some of the models in predicting the PCI after 3 years exceeded 90%. Suggestions are made to improve the performance of some algorithms. For instance, the naïve Bayes classifier was coupled with kernel estimates to achieve a better accuracy. It is demonstrated that using kernel estimates can increase the accuracy of the naïve Bayes classifier dramatically. Further, the study examines the impact of data segmentation. Data were divided into four different climatic regions. The accuracy of prediction was sufficiently high after segmentation, with the highest accuracy in the dry and nonfreeze zone and the lowest performance in the region with a wet and freezing climate.
            # Summarization the main topics in less than 10 keywords: Machine learning; Ensemble learning; Transportation asset management; Pavement condition index; Highwaymaintenance; Data preparation.
            # Journal paper: {file_contents}
            # Summarization the main topics in less than 10 keywords:
            # """

            # Use OpenAI API for summarization
            try:
                response = RoleGeneration(feedback_prompt_role_cot)

                # Write the summarized content to the same file
                with open(os.path.join(output_directory, filename), 'w') as outfile:
                    outfile.write(response)
                time.sleep(10)

            except openai.error.InvalidRequestError as e:
                print(f"Error for file '{filename}': {e}")


# Save the filenames to the output file
with open(os.path.join(output_directory, 'files_exceed_max_token.txt'), 'w', encoding="utf-8-sig") as output_file:
    for fname in filenames_exceeding_max_tokens:
        output_file.write(fname + '\n')
