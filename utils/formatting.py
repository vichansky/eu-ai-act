import pandas as pd
import re

class DataFrameProcessor:
    def __init__(self, dataframe):
        self.df = dataframe

    # Rid the 'Content' column of redundant text
    def clean_content_column(self):
        self.df['Content-Clean'] = self.df['Content'].apply(self.clean_text)

    # Extract information regarding any related articles or recitals
    def split_text_column(self):
        self.df['Split-Text'] = self.df.apply(self.split_text_by_article_or_recitals, axis=1)

        # Remove all instances of 'Suitable Recitals' from 'Split_Text' column
        self.df['Split-Text'] = self.df['Split-Text'].apply(
            lambda x: [item for item in x if 'Suitable Recitals' not in item]
        )

    # Expand the list of related and suitable recitals into separate columns
    def expand_split_text(self):
        split_df = pd.DataFrame(self.df['Split-Text'].tolist(), index=self.df.index)

        # Combine the original DataFrame with the new columns into 'result_df' and drop redundant columns
        self.df = pd.concat(objs=[self.df, split_df], axis=1).drop(columns=['Content', 'Content-Clean', 'Split-Text'])

    # Fill empty cells with 'None' to avoid issues with empty cells after stripping scraped text
    def clean_dataframe(self):
        self.df = self.df.where(pd.notnull(self.df), other=None)
        self.df = self.df.applymap(lambda x: None if x == '' else x)

        # Convert column names to strings
        self.df.columns = self.df.columns.astype(str)

    # Rename the first integer column '0' to become the final version of the 'Content' column
    def rename_first_column(self):
        self.df.rename(columns={"0": "Content"}, inplace=True)

    # For Recitals which point (reference) to Articles, keep only the numbers and add a preceding 'A'
    def apply_recital_rows(self):
        self.df = self.apply_to_recital_rows(self.df)

    # Modify ID column type
    def modify_id_column(self):
        self.df['ID'] = self.df.apply(self.modify_id, axis=1)

    # Extract any extra information when Articles text reference other Articles in the law
    def extract_from_articles(self):
        self.df['Article-Numbers'] = self.df.apply(self.extract_article_numbers, axis=1)

        # Expand the list into separate columns
        article_df = pd.DataFrame(self.df['Article-Numbers'].tolist(), index=self.df.index)

        # Rename the new columns to avoid overlap with existing columns because all are integers
        max_existing_col = max([int(col) for col in self.df.columns if col.isdigit()])
        new_columns = {i: str(max_existing_col + 1 + i) for i in range(article_df.shape[1])}
        article_df.rename(columns=new_columns, inplace=True)

        # Combine the original DataFrame with the new columns
        self.df = pd.concat(objs=[self.df, article_df], axis=1).drop(columns=['Article-Numbers'])

    # Function to clean text
    def clean_text(self, text):
        # Remove everything before and including 'Copy URL'
        text = re.sub(r'.*Copy URL\s*\n?', '', text, flags=re.DOTALL)

        # Remove everything before and including 'official translations.\n'
        text = re.sub(r'.*official translations\.\s*\n?', '', text, flags=re.DOTALL)

        # Remove everything after and including 'Feedback\n'
        text = re.sub(r'Feedback\s*\n?.*', '', text, flags=re.DOTALL)

        return text

    # Define the function to split text by 'Article ##' or 'Suitable Recitals ##'
    def split_text_by_article_or_recitals(self, row):
        text = row['Content-Clean']
        if row['Type'] == 'Article':
            # Split the text by 'Suitable Recitals' and the numbers following it
            recitals_split = re.split(r'(Suitable Recitals\s*\n(?:\d+\s*\n*)+)', text)

            columns = []
            for i in range(1, len(recitals_split), 2):
                columns.append(recitals_split[i] + recitals_split[i + 1])

            if recitals_split[0].strip():
                columns.insert(0, recitals_split[0].strip())

            # Further split the numbers into separate columns and add 'R' prefix
            final_columns = []
            for col in columns:
                if 'Suitable Recitals' in col:
                    parts = re.split(r'\n+', col)
                    for part in parts:
                        if part.isdigit():
                            final_columns.append('R' + part)
                        else:
                            final_columns.append(part)
                else:
                    final_columns.append(col)

            return final_columns

        elif row['Type'] == 'Recital':
            # Split the text by 'Article ##'
            parts = re.split(r'(Article \d+:)', text)

            columns = []
            for i in range(1, len(parts), 2):
                columns.append(parts[i] + parts[i + 1])

            if parts[0].strip():
                columns.insert(0, parts[0].strip())

            return columns

    # Apply function to Recital which points to Articles
    def keep_only_numbers(self, value):
        if value is None:
            return value

        # Use regular expression to find numbers in the value
        match = re.search(r'\d+', value)

        if match:
            # Add a preceding 'A' to signify Articles
            return 'A' + match.group(0)

        return value

    # Add the referenced articles to separate columns
    def apply_to_recital_rows(self, df):
        # Get all column names starting from '1' and beyond
        columns_to_process = [col for col in df.columns if col.isdigit() and int(col) >= 1]

        # Apply the function to keep only the referenced articles numbers
        for col in columns_to_process:
            df.loc[df['Type'] == 'Recital', col] = df.loc[df['Type'] == 'Recital', col].apply(self.keep_only_numbers)

        return df

    # Function to modify the ID based on the Type
    def modify_id(self, row):
        if row['Type'] == 'Article':
            return f"A{row['ID']}"
        elif row['Type'] == 'Recital':
            return f"R{row['ID']}"
        else:
            return row['ID']

    # From the 'Content' column extract any other references to other Articles and append to DataFrame
    def extract_article_numbers(self, row):

        text = row['Content']

        # Regular expression to match different patterns of article references
        article_numbers = re.findall(r'Articles? (\d+(?:, \d+)*(?: and \d+)?)', text)

        # Flatten the list of matches and split by comma and 'and'
        article_numbers = [num for sublist in article_numbers for num in re.split(r', | and ', sublist)]

        # Make sure to filter out references to articles with the numbers greater than 113, as these are not part of EU AI Act
        article_numbers = [num for num in article_numbers if num.isdigit() and int(num) <= 113]

        # For each article number add a preceding 'A'
        article_numbers_with_prefix = ['A' + num for num in article_numbers]

        return article_numbers_with_prefix

    def process(self):
        self.clean_content_column()
        self.split_text_column()
        self.expand_split_text()
        self.clean_dataframe()
        self.rename_first_column()
        self.apply_recital_rows()
        self.modify_id_column()
        self.extract_from_articles()

        print("\n Processing of articles & recitals DataFrame is finished! \n")

        return self.df


# Define the run function which will perform data processing and formatting
def run_dataframe_processor(dataframe):
    # Initialise the DataFrameProcessor Class()
    processor = DataFrameProcessor(dataframe)
    result_df = processor.process()

    # Save the processed dataframe
    result_df.to_csv('./data/processed_and_formatted.csv')

    print("The .csv was saved to location /data/processed_and_formatted.csv")

    return result_df


# Function to extract the numeric part from a node name in a PyVis network
def alphanumeric_sort_key(node):
    # Match the leading letters and the number parts
    numeric_part = re.match(r"([A-Za-z]+)(\d+)", node)

    # If numeric parts exists
    if numeric_part:
        # Return a tuple (alphabetic part, numeric part) for correct sorting
        return (numeric_part.group(1), int(numeric_part.group(2)))

    # If no numeric part, just return the node itself
    else:
        return (node, 0)


# Function to format the output and URL links to neighbouring nodes in a PyVis network
def format_node_output(node):
    # If an Article
    if node.startswith('A'):
        article_number = node[1:]  # Remove the 'A' and retrieve the number
        link = f"https://artificialintelligenceact.eu/article/{article_number}/"
        formatted_link_output = f"Article {article_number} - [go to article]({link})"

    # If a Recital
    elif node.startswith('R'):
        recital_number = node[1:]  # Remove the 'R' and retrieve the number
        link = f"https://artificialintelligenceact.eu/recital/{recital_number}/"
        formatted_link_output = f"Recital {recital_number} - [go to recital]({link})"

    return formatted_link_output
