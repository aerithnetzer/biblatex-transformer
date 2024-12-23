import requests
import time
import pandas as pd
import json
import bibtexparser
import re  # Import re module for regex operations
import csv
import signal
import time


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise (TimeoutException)


signal.signal(signal.SIGALRM, timeout_handler)


def generate_text_with_ollama(model_name, prompt):
    url = 'http://localhost:11434/api/generate'
    payload = {
        "model": model_name,
        "prompt": prompt,
        "temperature": 0,  # Make output more deterministic
        # Stop generation at double newlines (if supported by Ollama)
        "stop": ["\n\n"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers,
                             data=json.dumps(payload), stream=True)

    # Handle streaming response
    generated_text = ''
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if data.get('done', False):
                break
            else:
                generated_text += data.get('response', '')

    return generated_text.strip()


def create_prompt(plain_text_citation):
    prompt = f"""
You are a professional citation parser.

Given the following plain text citation:

{plain_text_citation}

Please convert this citation into a structured BibTeX entry. Include all relevant fields such as author, title, journal, volume, pages, year, etc.

Output only the BibTeX entry, and nothing else. Do not include any explanations, preambles, or additional text.
    """
    return prompt.strip()


def extract_bibtex(text):
    start = text.find('@')
    if start == -1:
        return text.strip()  # No BibTeX entry found
    brace_level = 0
    in_braces = False
    for idx, char in enumerate(text[start:], start=start):
        if char == '{':
            brace_level += 1
            in_braces = True
        elif char == '}':
            brace_level -= 1
        if brace_level == 0 and in_braces:
            # We've found the closing brace of the BibTeX entry
            end = idx + 1
            return text[start:end].strip()
    # If we reach here, braces were unbalanced
    return text[start:].strip()  # Return from '@' to the end


def compare_bibtex_entries(bibtex1, bibtex2):
    # Parse the BibTeX strings into dictionaries
    try:
        parser1 = bibtexparser.loads(bibtex1)
        parser2 = bibtexparser.loads(bibtex2)
    except Exception as e:
        print(f"Error parsing BibTeX: {e}")
        return {}

    entries1 = parser1.entries
    entries2 = parser2.entries

    if len(entries1) != len(entries2):
        print("Number of entries does not match.")
        return {}

    comparisons = []

    for entry1, entry2 in zip(entries1, entries2):
        # Exclude the 'ID' (cite key) from comparison
        ignore_fields = ['ID']
        fields1 = {k.lower(): v.strip()
                   for k, v in entry1.items() if k not in ignore_fields}
        fields2 = {k.lower(): v.strip()
                   for k, v in entry2.items() if k not in ignore_fields}

        all_fields = set(fields1.keys()).union(set(fields2.keys()))
        field_comparisons = {}
        for field in all_fields:
            value1 = fields1.get(field, '')
            value2 = fields2.get(field, '')
            match = value1.lower() == value2.lower()  # Case-insensitive comparison
            field_comparisons[field] = {
                'GeneratedValue': value2,
                'ActualValue': value1,
                'Match': match
            }
        comparisons.append(field_comparisons)

    return comparisons


def main():
    # CSV file path
    csv_file = 'output.csv'  # Update this path to your CSV file
    df = pd.read_csv(csv_file)

    # List of models to test (ensure these models are installed in Ollama)
    models = ['llama2:7b', 'llama3:8b', 'tinyllama', 'mistral', 'codegemma:2b',
              'codegemma:7b', 'starcoder2:3b']  # Replace with your installed model names

    results = []

    for model in models:
        print(f"Testing model: {model}")
        model_results = []
        for index, row in df.iterrows():
            plain_text_citation = row['Plain Text Citation']
            actual_bibtex = row['BibTeX Citation']
            prompt = create_prompt(plain_text_citation)

            try:
                signal.alarm(90)

                start_generation_time = time.time()
                generated_bibtex = generate_text_with_ollama(model, prompt)
                end_generation_time = time.time()
                print(f"Generated BibTeX: {generated_bibtex}")
                generated_bibtex = extract_bibtex(generated_bibtex)

                # Remove newlines from generated and actual BibTeX
                generated_bibtex_single_line = generated_bibtex.replace(
                    '\n', ' ').replace('\r', '')
                actual_bibtex_single_line = actual_bibtex.replace(
                    '\n', ' ').replace('\r', '')

                # Compare the BibTeX entries field by field
                field_comparisons = compare_bibtex_entries(
                    actual_bibtex, generated_bibtex)
                if field_comparisons:
                    field_comparison = field_comparisons[0]
                    total_fields = len(field_comparison)
                    matching_fields = sum(
                        1 for v in field_comparison.values() if v['Match'])
                    percentage_match = (
                        matching_fields / total_fields) * 100 if total_fields > 0 else 0
                    # Prepare a summary of non-matching fields
                    non_matching_fields = [
                        f for f, v in field_comparison.items() if not v['Match']]
                    # Optionally, store detailed field comparisons as JSON string
                    field_comparison_json = json.dumps(field_comparison)
                else:
                    # Handle empty comparisons
                    total_fields = 0
                    matching_fields = 0
                    percentage_match = 0
                    non_matching_fields = []
                    field_comparison_json = ''

                model_results.append({
                    'Model': model,
                    'Index': index,
                    'PlainTextCitation': plain_text_citation,
                    'GeneratedBibTeX': generated_bibtex_single_line,
                    'TimeToGeneration': end_generation_time - start_generation_time,
                    'ActualBibTeX': actual_bibtex_single_line,
                    'TotalFields': total_fields,
                    'MatchingFields': matching_fields,
                    'PercentageMatch': percentage_match,
                    'NonMatchingFields': ', '.join(non_matching_fields),
                    'FieldComparisons': field_comparison_json  # Optional detailed comparisons
                })

                result_text = f"{
                    matching_fields}/{total_fields} fields matched ({percentage_match:.1f}%)"
                print(f"Processed citation {index} with model {
                      model}: {result_text}")

            except Exception as e:
                print(f"Error processing citation index {
                      index} with model {model}: {e}")
                model_results.append({
                    'Model': model,
                    'Index': "null",
                    'PlainTextCitation': "null",
                    'GeneratedBibTeX': 'null',
                    'ActualBibTeX': 'null',
                    'TotalFields': 0,
                    'MatchingFields': 0,
                    'PercentageMatch': 0,
                    'NonMatchingFields': 'null',
                    'FieldComparisons': 'null',
                    'Error': str(e)
                })

            # Collect results
            results.extend(model_results)

        # Convert the results to a DataFrame for analysis
            results_df = pd.DataFrame(results)
# Save results to CSV
            results_df.to_csv(f'results/{model}_comparison_results.csv',
                              index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar='"')
            print(f"Results saved to results/{model}_comparison_results.csv")


if __name__ == '__main__':
    main()
