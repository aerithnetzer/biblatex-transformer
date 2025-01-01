## Background and Motivation

University-owned journal-publishing operations operate under far tighter
economic constraints --- direct and opportunity --- and therefore must
solve the same problems of corporate academic publishers with a fraction
of the resources available. One of these problems is reference metadata,
i.e. machine-actionable references that are then used to count citations
of articles. The act of capturing, counting, and using citations
accurately allows for funding agencies, universities, and publishers to
make data-driven decisions for funding allocation, allows for reviewers
to validate the research of a manuscript, and allows for faster
literature review. Here, we evaluate the use of local large language
models to curate the metadata with minimal human intervention.

### An Example

The workflow for our university --- a small, elite university in the
Mid-west United States --- consists of receiving manuscripts from
authors in a Microsoft Word file format. We then use pandoc
[@PandocIndex] to transform this Word document to a markdown file
format, from which we can build PDF and Web versions from a single
source. But due to author unwillingness to use plaintext markup formats
such as LaTeX or Markdown, we must recreate the bibliography.
Previously, this mean looking up each source, adding them to a
Zotero[@ZoteroYourPersonal] library, and then exporting the biblatex
file for use as metadata in the web version of the article. This would
allow for services such as Google Scholar and Web of Science to scrape
the metadata and count citations for the cited articles. This allows for
researchers conducting literature reviews to find articles easier and
faster, and allows for easier cross-checking for dubious claims. The
present system, can automate this labor-intensive machine-actionable
metadata creation process. With the advent of Large Language Models
(LLMs), we can create systems to parse out the plaintext citations in an
article, pass it to a Large Language Model, and output a
machine-actionable metadata citation entry.

### Limitations and Concerns

Along with the rapid growth in users of Large-Language models, so have
concerns over the ecological sustainability of LLM
technology.[@dingSustainableLLMServing2024]
[@chienReducingCarbonImpact2023] Most of these concerns, however, can be
alleviated with the use of \"small\" models such as those provided by
Ollama. Further, there are concerns about the validity of Large-Language
models, especially concerning their propensity to hallucinate. However,
in combination with validity checkers such as bibtexparser and human
review, we are confident enough in this system to be used in production
of our journals.

## Methodology

::: center
   Col1   Col2   Col2    Col3
  ------ ------ ------- ------
    1      6     87837   787
    2      7      78     5415
    3     545     778    7507
    4     545    18744   7560
    5      88     788    6344
:::

### Data Collection

This is my data collection section.

### Analysis

## Results

### Discussion

## Bibliography {#bibliography .unnumbered}
