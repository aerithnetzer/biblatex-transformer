import os
import glob
import json
import pandas as pd
import matplotlib.pyplot as plt
import bibtexparser


def is_valid_bibtex(entry):
    try:
        bibtexparser.loads(entry)
        return True
    except:
        return False


def main():
    # Directory containing the results CSV files
    results_dir = "results/"

    # Get a list of all CSV files in the results directory
    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))

    if not csv_files:
        print(f"No CSV files found in directory '{results_dir}'.")
        return

    # Read and append all CSV files into a single DataFrame
    df_list = []
    for file in csv_files:
        df_list.append(pd.read_csv(file))

    df = pd.concat(df_list, ignore_index=True)

    # Check if 'Model' column exists
    if "Model" not in df.columns:
        print(
            "The CSV files must contain a 'Model' column to differentiate between models."
        )
        return

    # Get the list of unique models
    models = df["Model"].unique()
    for model in models:
        print(model)
    print(f"Found models: {', '.join(models)}\n")

    # Initialize dictionaries to store statistics per model
    model_stats = {}
    for model in models:
        model_stats[model] = {
            "total_fields": 0,
            "total_matching_fields": 0,
            "field_accuracy": {},
            "total_bibtex_entries": 0,
            "valid_bibtex_entries": 0,
        }

    # Required fields
    required_fields = {
        "author",
        "title",
        "journal",
        "year",
        "publisher",
        "volume",
        "number",
        "school",
    }

    # Iterate over each row to extract field comparison data
    for index, row in df.iterrows():
        model = row["Model"]
        field_comparisons_json = row.get("FieldComparisons", "{}")
        bibtex_entry = row.get("BibTeX", "")

        try:
            field_comparisons = json.loads(str(field_comparisons_json))
        except json.JSONDecodeError:
            print(f"Error decoding JSON at index {index} for model '{model}'")
            continue

        # Count matching fields for the current model
        for field, comparison in field_comparisons.items():
            if field in required_fields:
                model_stats[model]["total_fields"] += 1
                match = comparison.get("Match", False)
                model_stats[model]["total_matching_fields"] += int(match)

                # Update per-field accuracy stats for the current model
                if field not in model_stats[model]["field_accuracy"]:
                    model_stats[model]["field_accuracy"][field] = {
                        "total": 0,
                        "matches": 0,
                    }
                model_stats[model]["field_accuracy"][field]["total"] += 1
                model_stats[model]["field_accuracy"][field]["matches"] += int(match)

        # Check for valid BibTeX entry
        model_stats[model]["total_bibtex_entries"] += 1
        if is_valid_bibtex(bibtex_entry):
            model_stats[model]["valid_bibtex_entries"] += 1

    # Compute and display overall accuracy per model
    overall_accuracy = {}
    bibtex_accuracy = {}
    for model, stats in model_stats.items():
        total = stats["total_fields"]
        matches = stats["total_matching_fields"]
        accuracy = (matches / total) * 100 if total > 0 else 0
        overall_accuracy[model] = accuracy

        total_bibtex = stats["total_bibtex_entries"]
        valid_bibtex = stats["valid_bibtex_entries"]
        bibtex_acc = (valid_bibtex / total_bibtex) * 100 if total_bibtex > 0 else 0
        bibtex_accuracy[model] = bibtex_acc

        print(f"Model '{model}' - Overall Field Accuracy: {accuracy:.2f}%")
        print(f"Model '{model}' - BibTeX Validity Accuracy: {bibtex_acc:.2f}%")

    print("\n")

    # Compute and display per-field accuracy per model
    per_field_accuracy = {}
    all_fields = set()
    for model, stats in model_stats.items():
        per_field_accuracy[model] = {}
        for field, field_stats in stats["field_accuracy"].items():
            accuracy = (
                (field_stats["matches"] / field_stats["total"]) * 100
                if field_stats["total"] > 0
                else 0
            )
            per_field_accuracy[model][field] = accuracy
            print(f"Model '{model}' - Field '{field}': {accuracy:.2f}% accuracy")
            all_fields.add(field)

    print("\n")

    # Generate Pandoc tables
    print("# Overall Accuracy by Model")
    print("| Model | Field Accuracy (%) | BibTeX Validity (%) |")
    print("|-------|--------------------|---------------------|")
    for model in models:
        print(
            f"| {model} | {overall_accuracy[model]:.2f} | {bibtex_accuracy[model]:.2f} |"
        )

    print("\n# Per-Field Accuracy by Model")
    fields = sorted(list(all_fields))
    header = "| Field | " + " | ".join(models) + " |"
    separator = "|-------" + "|-------" * len(models) + "|"
    print(header)
    print(separator)
    for field in fields:
        row = (
            f"| {field} | "
            + " | ".join(
                f"{per_field_accuracy[model].get(field, 0):.2f}" for model in models
            )
            + " |"
        )
        print(row)

    # Plot overall accuracy comparison
    plt.figure(figsize=(10, 6))
    models = list(overall_accuracy.keys())
    accuracies = [overall_accuracy[model] for model in models]
    bibtex_accuracies = [bibtex_accuracy[model] for model in models]
    bars1 = plt.bar(models, accuracies, color="skyblue", label="Field Accuracy")
    plt.ylabel("Accuracy (%)")
    plt.title("Overall Field Accuracy by Model", pad=20)
    plt.ylim(0, 100)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend()

    # Add accuracy labels on top of each bar
    for bars in [bars1]:
        for bar in bars:
            height = bar.get_height()
            plt.annotate(
                f"{height:.2f}%",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

    plt.tight_layout()
    plt.savefig("overall_accuracy_comparison.png", dpi=300)
    plt.show()

    # Plot per-field accuracy comparison
    fields = sorted(list(all_fields))
    index = range(len(fields))
    bar_width = 0.8 / len(models)  # Adjust bar width based on number of models
    # Generate a list of colors
    colors = plt.cm.get_cmap("tab10", len(models)).colors

    plt.figure(figsize=(14, 8))

    for i, model in enumerate(models):
        accuracies = [per_field_accuracy[model].get(field, 0) for field in fields]
        plt.bar(
            [x + i * bar_width for x in index],
            accuracies,
            bar_width,
            label=model,
            color=colors[i],
        )

    plt.xlabel("Fields")
    plt.ylabel("Accuracy (%)")
    plt.title("Per-Field Accuracy Comparison by Model")
    plt.xticks(
        [x + bar_width * (len(models) - 1) / 2 for x in index], fields, rotation=45
    )
    plt.ylim(0, 100)
    plt.legend(title="Models")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("per_field_accuracy_comparison.png", dpi=300)
    plt.show()

    # Summary statistics for TimeToGeneration column
    if "TimeToGeneration" in df.columns:
        time_to_generation_stats = {
            "mean": df["TimeToGeneration"].mean(),
            "median": df["TimeToGeneration"].median(),
            "std_dev": df["TimeToGeneration"].std(),
        }

        with open("time_to_generation_stats.txt", "w") as f:
            f.write("Summary Statistics for TimeToGeneration:\n")
            f.write(f"Mean: {time_to_generation_stats['mean']:.2f}\n")
            f.write(f"Median: {time_to_generation_stats['median']:.2f}\n")
            f.write(f"Standard Deviation: {time_to_generation_stats['std_dev']:.2f}\n")

        # Create a box and whisker plot for TimeToGeneration for each model
        plt.figure(figsize=(10, 6))
        data = [
            df[df["Model"] == model]["TimeToGeneration"].dropna() for model in models
        ]
        plt.boxplot(data, labels=models)
        plt.title("Box and Whisker Plot for TimeToGeneration by Model")
        plt.ylabel("TimeToGeneration")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("time_to_generation_boxplot.png", dpi=300)
        plt.show()
    else:
        print("The 'TimeToGeneration' column is not present in the CSV files.")


if __name__ == "__main__":
    main()
