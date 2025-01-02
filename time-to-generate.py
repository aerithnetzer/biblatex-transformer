import pandas as pd
import matplotlib.pyplot as plt
import glob

# Step 1: Load all CSV files from the 'results/' directory
file_paths = glob.glob('results/*.csv')

# Combine all CSV files into a single DataFrame
dataframes = [pd.read_csv(file_path) for file_path in file_paths]
combined_df = pd.concat(dataframes, ignore_index=True)

# Step 2: Generate the box-and-whisker plot
plt.figure(figsize=(10, 6))
combined_df.boxplot(column='TimeToGeneration', by='Model', grid=False)

# Step 3: Customize the plot
plt.title('Time to Generation by Model')
plt.suptitle('')  # Remove the default pandas boxplot title
plt.xlabel('Model')
plt.ylabel('Time to Generation (seconds)')
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

# Show the plot
plt.tight_layout()
plt.savefig("./article/time-to-generation.png", dpi=120)

# Calculate median and standard deviation
stats = combined_df.groupby('Model')['TimeToGeneration'].agg(['median', 'std'])

# Print markdown table
print("| Model | Median Time to Generation (seconds) | Standard Deviation (seconds) |")
print("|-------|-------------------------------------|------------------------------|")
for model, row in stats.iterrows():
    print(f"| {model} | {row['median']:.2f} | {row['std']:.2f} |")
