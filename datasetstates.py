import pandas as pd
import matplotlib.pyplot as plt


def get_unique_citation_styles(file_path):
    df = pd.read_csv(file_path)
    citation_styles = df["Plain Text Citation Style"].unique()
    return citation_styles


def get_proportion_of_styles(file_path):
    df = pd.read_csv(file_path)
    citation_styles = df["Plain Text Citation Style"]
    style_counts = citation_styles.value_counts()
    total_styles = len(citation_styles)
    style_proportions = style_counts / total_styles

    # Plotting the pie chart
    plt.figure(figsize=(10, 7))
    style_proportions.plot.pie(autopct="%1.1f%%", startangle=140)
    plt.title("Proportion of Plain Text Citation Styles")
    plt.ylabel("")  # Hide the y-label
    plt.show()
    return style_proportions


file_path = "./input_dataset.csv"
unique_styles = get_unique_citation_styles(file_path)
print(get_proportion_of_styles(file_path))
for style in unique_styles:
    print(style)
