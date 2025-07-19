import os

import openai

openai.api_key = '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'
model_gpt35 = 'gpt-3.5-turbo-16k-0613'
model_gpt4 = 'gpt-4-0613'
def BasicGeneration(userPrompt):
    completion = openai.ChatCompletion.create(
        model = model_gpt35,
        messages=[

            {"role": "user", "content": userPrompt}
        ]
    )
    return completion.choices[0].message.content

def RoleGeneration(userPrompt):
    completion = openai.ChatCompletion.create(
        model = model_gpt35,
        messages=[
            {"role": "system", "content": "You are a expert in asset and construction management domain."},
            {"role": "user", "content": userPrompt}
        ]
    )
    return completion.choices[0].message.content

input_directory = '/Users/yunshunzhong/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/PhD Project/Prompt Engineering/Experiment/cleaned_papers_without_ref'
output_directory = '/Users/yunshunzhong/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/PhD Project/Prompt Engineering/Experiment/topic_result/summarize_cot_role/summarized_papers'

# Iterate through each file in the folder
for filename in os.listdir(input_directory):
    if filename.endswith('.txt'):
        with open(os.path.join(input_directory, filename), 'r') as file:
            # Read the file content
            file_contents = file.read()

            # Create a prompt for the summarization
            base_prompt = f"Summarize the main topics in less than 10 keywords in the following journal paper in asset and construction management: {file_contents}."
            base_prompt_cot = f"Summarize the main topics in less than 10 keywords in the following journal paper in asset and construction management: {file_contents}. Think step by step."
            base_prompt_role = f"Summarize the main topics in less than 10 keywords in the following journal paper in asset and construction management: {file_contents}."
            base_prompt_role_cot = f"Summarize the main topics in less than 10 keywords in the following journal paper in asset and construction management: {file_contents}. Think step by step."

            base_prompt_role_cot2 = f"Please identify and summarize the key topics of the following journal paper in asset and construction management, using no more than 10 keywords and seperating keywords by comma. Consider each section of the paper as you proceed: {file_contents}."

            # Summarize the paper first then extract topics
            summarize_prompt = f"Summarize the following journal paper in asset and construction management: {file_contents} in less than 1000 words. Think step by step."

            # one_shot_prompt = f"""
            # Journal paper: This study explores the performance regime of different classification algorithms as they are applied to the analysis of asphalt pavement deterioration data. The aim is to examine how different algorithms deal with the typically limited and low-quality data sets in the infrastructure asset management domain, and whether better configurations of relevant algorithms help overcome these limitations. Furthermore, the emphasis on choosing the most affordable attributes (e.g., temperature and precipitation levels) makes the results reproducible to smaller municipalities. This analysis used the data of more than 3,000 examples of road sections, which were retrieved from the Long-Term Pavement Performance (LTPP) database. The algorithms examined in this study include two types of decision trees, naïve Bayes classifier, naïve Bayes coupled with kernels, logistic regression, k-nearest neighbors (k-NN), random forest, and gradient boosted trees. The performance of these algorithms is compared, and their weaknesses and strengths are discussed. They were all applied to predict the deterioration of pavement condition index (PCI). Of specific importance is the positive role of ensemble learning. It is shown how using higher efficiencies by using ensemble learning can compensate for data shortcomings. The accuracy of some of the models in predicting the PCI after 3 years exceeded 90%. Suggestions are made to improve the performance of some algorithms. For instance, the naïve Bayes classifier was coupled with kernel estimates to achieve a better accuracy. It is demonstrated that using kernel estimates can increase the accuracy of the naïve Bayes classifier dramatically. Further, the study examines the impact of data segmentation. Data were divided into four different climatic regions. The accuracy of prediction was sufficiently high after segmentation, with the highest accuracy in the dry and nonfreeze zone and the lowest performance in the region with a wet and freezing climate.
            # Summarization the main topics in less than 10 keywords: Machine learning; Ensemble learning; Transportation asset management; Pavement condition index; Highwaymaintenance; Data preparation.
            # Journal paper: {file_contents}
            # Summarization the main topics in less than 10 keywords:
            # """

            # Use OpenAI API for summarization
            try:
                response = RoleGeneration(summarize_prompt)

                # Write the summarized content to the same file
                with open(os.path.join(output_directory, filename), 'w') as outfile:
                    outfile.write(response)

            except openai.error.InvalidRequestError as e:
                print(f"Error for file '{filename}': {e}")


output_directory2 = "/Users/yunshunzhong/Library/Mobile Documents/3L68KQB4HG~com~readdle~CommonDocuments/Documents/PhD Project/Prompt Engineering/Experiment/topic_result/summarize_cot_role"

# Extract topics form summarized papers
for filename in os.listdir(output_directory):
    if filename.endswith('.txt'):
        with open(os.path.join(input_directory, filename), 'r') as file:
            # Read the file content
            file_contents = file.read()

            # Summarize the paper first then extract topics
            topic_prompt = f"Summarize the main topics in less than 10 keywords in the following summarized journal paper in construction management: {file_contents}. Think step by step."

            # Use OpenAI API for summarization
            try:
                response = RoleGeneration(topic_prompt)

                # Write the summarized content to the same file
                with open(os.path.join(output_directory2, filename), 'w') as outfile:
                    outfile.write(response)

            except openai.error.InvalidRequestError as e:
                print(f"Error for file '{filename}': {e}")


print("Summarization completed for all papers.")
