import pandas as pd


def get_unique_citation_styles(file_path):
    df = pd.read_csv(file_path)
    citation_styles = df['Plain Text Citation Style'].unique()
    return citation_styles


file_path = 'output copy.csv'
unique_styles = get_unique_citation_styles(file_path)
for style in unique_styles:
    print(style)
