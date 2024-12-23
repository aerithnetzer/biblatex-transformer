import pandas as pd
import os
import subprocess
import requests as req
import json

# This file loads random data from the crossref works API and saves metadata as a json file

# Load random data from the crossref works API

base_url = 'https://api.crossref.org/works?sample=1000'

def sample_crossref_dois(base_url = "https://api.crossref.org/works?sample=1", sample_size = 1):
    """
    This function retrieves a random sample of DOIs from the crossref works API

    Parameters:
        url (str): The url of the crossref works API
        sample_size (int): The number of DOIs to retrieve

    Returns:
        sampled_dois (list): A list of DOIs
    """

    # Initialize an empty list to store the sampled DOIs
    sampled_dois = []
    # Retrieve DOIs from the crossref works API until the sample size is reached

    while int(len(sampled_dois)) < sample_size:
        response = req.get("https://api.crossref.org/works?sample=1&mailto=aerith.netzer@northwestern.edu").json()
        for i in response['message']['items']:
            doi = i['DOI']
            sampled_dois.append(doi)

    return sampled_dois

def get_crossref_metadata(doi):
    """
    This function retrieves metadata for a given DOI from the crossref works API

    Parameters:
        doi (str): A DOI

    Returns:
        metadata (dict): Metadata for the given DOI
    """

    # Construct the URL for the crossref works API
    url = f"https://api.crossref.org/works/{doi}"

    # Retrieve metadata for the given DOI
    response = req.get(url).json()

    # Extract the metadata from the response
    metadata = response['message']

    return metadata

def save_relevant_metadata(metadata):
    """
    This function saves relevant metadata to a json file

    Parameters:
        metadata (dict): Metadata for a given DOI

    Returns:
        None
    """

    # Extract relevant metadata fields
    relevant_metadata = {}


    try:
        if 'DOI' in metadata:
            relevant_metadata['DOI'] = metadata['DOI']
    except KeyError as e:
        print(f"KeyError: DOI not found in metadata - {e}")

    try:
        if 'title' in metadata and len(metadata['title']) > 0:
            relevant_metadata['title'] = metadata['title'][0]
    except KeyError as e:
        print(f"KeyError: Title not found in metadata - {e}")

    try:
        if 'page' in metadata:
            relevant_metadata['pages'] = metadata['page']
    except KeyError as e:
        print(f"KeyError: Page not found in metadata - {e}")

    try:
        if 'author' in metadata:
            relevant_metadata['author'] = metadata['author']
    except KeyError as e:
        print(f"KeyError: Author not found in metadata - {e}")

    try:
        if 'published' in metadata and 'date-parts' in metadata['published']:
            relevant_metadata['published'] = metadata['published']['date-parts'][0]
    except KeyError as e:
        print(f"KeyError: Published date not found in metadata - {e}")

    try:
        if 'publisher' in metadata:
            relevant_metadata['publisher'] = metadata['publisher']
    except KeyError as e:
        print(f"KeyError: Publisher not found in metadata - {e}")

    try:
        if 'short-container-title' in metadata and len(metadata['short-container-title']) > 0:
            relevant_metadata['journal_title'] = metadata['short-container-title'][0]
    except KeyError as e:
        print(f"KeyError: Journal title not found in metadata - {e}")

    # Convert to JSON
    relevant_metadata_json = json.dumps(relevant_metadata)
    print(relevant_metadata_json)

def get_pandoc_citeproc(relevant_metadata):
    """
    This function converts relevant metadata to pandoc-citeproc format

    Parameters:
        relevant_metadata (dict): Relevant metadata for a given DOI

    Returns:
        pandoc_citeproc (dict): Metadata in pandoc-citeproc format
    """

    # Convert relevant metadata to pandoc-citeproc format
    if relevant_metadata is None:
        return {}

    pandoc_citeproc = {
        'type': 'article',
        'doi': relevant_metadata['DOI'],
        'title': relevant_metadata['title'],
        'page': relevant_metadata['pages'],
        'author': relevant_metadata['author'],
        'issued': relevant_metadata['published']['date-parts'][0],
    }

    return pandoc_citeproc

def create_plaintext_citation(pandoc_citeproc, csl):
    """
    This function converts pandoc-citeproc metadata to a plaintext citation

    Parameters:
        pandoc_citeproc (dict): Metadata in pandoc-citeproc format
        csl (str): The citation style language (CSL) to use

    Returns:
        plaintext_citation (str): A plaintext citation
    """

    # Convert pandoc-citeproc metadata to a plaintext citation
    try:
        # Construct the Pandoc command
        command = [
            "pandoc",
            "--citeproc",
            str(pandoc_citeproc),
            "--pdf-engine=xelatex",  # You can specify the PDF engine (e.g., xelatex, lualatex, etc.)
            "--csl=apa-6th-edition.csl"
        ]

        # Run the Pandoc command
        subprocess.run(command, check=True)
        print(f"Converted successfully.")
    finally:
        print("Conversion failed.")

def main():
    sampled_dois = sample_crossref_dois()

    for i in sampled_dois:
        metadata = get_crossref_metadata(i)
        relevant_metadata = save_relevant_metadata(metadata)
        pandoc_citeproc = get_pandoc_citeproc(relevant_metadata)
        create_plaintext_citation(pandoc_citeproc, "apa-6th-edition.csl")
main()
