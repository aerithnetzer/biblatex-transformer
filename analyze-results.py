import pandas as pd
import json
import matplotlib.pyplot as plt
import os
import glob


def main():
    # Directory containing the results CSV files
    results_dir = 'results/'

    # Get a list of all CSV files in the results directory
    csv_files = glob.glob(os.path.join(results_dir, '*.csv'))

    if not csv_files:
        print(f"No CSV files found in directory '{results_dir}'.")
        return

    # Read and append all CSV files into a single DataFrame
    df_list = []
    for file in csv_files:
        df_list.append(pd.read_csv(file))

    df = pd.concat(df_list, ignore_index=True)

    # Check if 'Model' column exists
    if 'Model' not in df.columns:
        print(
            "The CSV files must contain a 'Model' column to differentiate between models.")
        return

    # Get the list of unique models
    models = df['Model'].unique()
    print(f"Found models: {', '.join(models)}\n")

    # Initialize dictionaries to store statistics per model
    model_stats = {}

    for model in models:
        model_stats[model] = {
            'total_fields': 0,
            'total_matching_fields': 0,
            'field_accuracy': {}
        }

    # Iterate over each row to extract field comparison data
    for index, row in df.iterrows():
        model = row['Model']
        field_comparisons_json = row.get('FieldComparisons', '{}')
        try:
            field_comparisons = json.loads(str(field_comparisons_json))
        except json.JSONDecodeError:
            print(f"Error decoding JSON at index {index} for model '{model}'")
            continue

        # Count matching fields for the current model
        for field, comparison in field_comparisons.items():
            model_stats[model]['total_fields'] += 1
            match = comparison.get('Match', False)
            model_stats[model]['total_matching_fields'] += int(match)

            # Update per-field accuracy stats for the current model
            if field not in model_stats[model]['field_accuracy']:
                model_stats[model]['field_accuracy'][field] = {
                    'total': 0, 'matches': 0}
            model_stats[model]['field_accuracy'][field]['total'] += 1
            model_stats[model]['field_accuracy'][field]['matches'] += int(
                match)

    # Compute and display overall accuracy per model
    overall_accuracy = {}
    for model, stats in model_stats.items():
        total = stats['total_fields']
        matches = stats['total_matching_fields']
        accuracy = (matches / total) * 100 if total > 0 else 0
        overall_accuracy[model] = accuracy
        print(f"Model '{model}' - Overall Field Accuracy: {accuracy:.2f}%")

    print("\n")

    # Compute and display per-field accuracy per model
    per_field_accuracy = {}
    all_fields = set()
    for model, stats in model_stats.items():
        per_field_accuracy[model] = {}
        for field, field_stats in stats['field_accuracy'].items():
            accuracy = (field_stats['matches'] / field_stats['total']
                        ) * 100 if field_stats['total'] > 0 else 0
            per_field_accuracy[model][field] = accuracy
            print(
                f"Model '{model}' - Field '{field}': {accuracy:.2f}% accuracy")
            all_fields.add(field)

    print("\n")

    # Plot overall accuracy comparison
    plt.figure(figsize=(10, 6))
    models = list(overall_accuracy.keys())
    accuracies = [overall_accuracy[model] for model in models]
    bars = plt.bar(models, accuracies, color=[
                   'skyblue', 'salmon', 'lightgreen', 'orange', 'violet'])
    plt.ylabel('Accuracy (%)')
    plt.title('Overall Field Accuracy by Model')
    plt.ylim(0, 100)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add accuracy labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height:.2f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('overall_accuracy_comparison.png')
    plt.show()

    # Plot per-field accuracy comparison
    fields = sorted(list(all_fields))
    index = range(len(fields))
    bar_width = 0.8 / len(models)  # Adjust bar width based on number of models
    # Generate a list of colors
    colors = plt.cm.get_cmap('tab10', len(models)).colors

    plt.figure(figsize=(14, 8))

    for i, model in enumerate(models):
        accuracies = [per_field_accuracy[model].get(
            field, 0) for field in fields]
        plt.bar([x + i * bar_width for x in index], accuracies,
                bar_width, label=model, color=colors[i])

    plt.xlabel('Fields')
    plt.ylabel('Accuracy (%)')
    plt.title('Per-Field Accuracy Comparison by Model')
    plt.xticks([x + bar_width * (len(models)-1) /
               2 for x in index], fields, rotation=45)
    plt.ylim(0, 100)
    plt.legend(title='Models')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('per_field_accuracy_comparison.png')
    plt.show()


if __name__ == '__main__':
    main()
