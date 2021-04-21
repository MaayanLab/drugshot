# DrugShot

PubMed contains millions of publications that co-mention terms that describe drugs with other biomedical terms such as genes or diseases. DrugShot is a web-based server application that enables users to enter any biomedical search term into a simple input form to receive ranked lists of drugs and small molecules based on their relevance to the search term. To produce ranked lists of drugs, DrugShot cross-references returned PubMed IDs with DrugRIF, a curated resource of drug-PMID associations, to produce an associated compound list where each compound is ranked according to total co-mentions with the search term from shared PubMed IDs. Additionally, lists of compounds predicted to be associated with the search terms are generated based on co-occurrence in the literature and co-expression from L1000 drug-induced gene expression profiles. Through its search functionality and abstraction of drug lists from different sources, DrugShot can facilitate hypothesis generation by suggesting small molecule sets related to any biomedical term of interest. 

Currently the development version of the service is hosted at:
https://maayanlab.cloud/drugshot


## Contact
Ma'ayan Laboratory, Computational Systems Biology<br>
Department of Pharmacological Sciences<br>
Icahn School of Medicine at Mount Sinai<br>
New York, NY 10029<br>
