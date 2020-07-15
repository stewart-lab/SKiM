# SKiM
Serial KinderMiner (or simply SKiM) is general literature-based discovery system for querying all ~30 million PubMed abstracts. 

This repository provides the python script for SKiM, a general literature based discovery system for uncovering unknown public knowledge from all ~30 million PubMed articles. This project is done by Stewart Computational Biology Group (https://morgridge.org/research/regenerative-biology/bioinformatics/) within Thomson Lab (https://morgridge.org/research/regenerative-biology/thomson-lab/) at Morgridge Institute for Research, Madison, WI, USA.

A local PubMed database version is required for executing SKiM. 

We applied SKiM for repurposing drugs for four diseases from Swanson's work, Raynaud's disease, migraine, Alzheimer's disease and schizophrenia. We compiled three lexicons from various resources for the study. The diseases lexicon was compiled from UMLS Metathesaurus and SNOMED CT. The drugs lexicon was compiled from UMLS Metathesaurus, DrugBank and PharmGKB. The phenotypes and synonyms lexicon was compiled from Human Phenotypes Ontology (HPO), Phenome Wide Association Studies (PheWAS), and Online Mendelian Inheritance in Man (OMIM). Resources such as UMLS Metathesaurus requires licence. Instead of sharing the lexicons, we share the scripts for compiling the lexicons. 

We compiled a list of disease-drug associations from Comparative Toxicogenomics Database (CTD), National Drug File - Reference Terminology (NDF-RT), DrugBank and ClinicalKey. We used our diseases and drugs lexicon to identify the duplicates across the resources. Instead of sharing the associations, we share the scripts for generating disease-drug associations from various resources.

Basic syntax for executing SKiM:
$ python production_SKiM.py A_TERM_FILE B_TERMS_FILE C_TERMS_FILE OUTPUT_FOLDER NUMBER_OF_B_TERMS_FOR_B2C_EXECUTION
