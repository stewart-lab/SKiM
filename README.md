# SKiM
Serial KinderMiner (SKiM) is general literature-based discovery system for querying all ~30 million PubMed abstracts. 

This repository provides the python script for SKiM, a general literature-based discovery system for uncovering unknown public knowledge from all ~30 million PubMed articles. This project is by the Stewart Computational Biology Group (https://morgridge.org/research/regenerative-biology/bioinformatics/) at the Morgridge Institute for Research, Madison, WI, USA.

A backend PubMed text index is required for executing SKiM. The code for building the backend PubMed text index is available at https://github.com/iross/km_indexer.

We applied SKiM for repurposing drugs for four diseases from Swanson's work, Raynaud's disease, migraine, Alzheimer's disease and schizophrenia. We compiled three lexicons from various resources for the study. The diseases lexicon was compiled from UMLS Metathesaurus and SNOMED CT (https://github.com/stewart-lab/Diseases_lexicon). The drugs lexicon was compiled from UMLS Metathesaurus, DrugBank and PharmGKB (https://github.com/CutaneousBioinf/LiteratureMiningTool/tree/master/DrugDict). For drug repurposing, we used a subset of drugs from the drugs lexicon (https://github.com/stewart-lab/Drugs_subset_for_drugs_repurposing_application). The phenotypes and synonyms lexicon was compiled from Human Phenotypes Ontology (HPO), Phenome Wide Association Studies (PheWAS), and Online Mendelian Inheritance in Man (OMIM) (https://github.com/stewart-lab/Phenotypes_and_symptoms_lexicon). Resources such as UMLS Metathesaurus requires license. Instead of sharing the lexicons, we share the scripts for compiling the lexicons. 

We compiled a list of disease-drug associations from Comparative Toxicogenomics Database (CTD), National Drug File - Reference Terminology (NDF-RT), DrugBank and ClinicalKey. We used our diseases and drugs lexicon to identify the duplicates across the resources. Instead of sharing the associations, we share the scripts for generating disease-drug associations from various resources.

Display help:   
$ python production_SKiM.py -h  

Basic syntax for executing SKiM:   
$ python production_SKiM.py keyphrase level_1_file level_2_file output_dir num_level2_queries  

Example command using the sample A, B and C term files within 'data' folder:
$ python production_SKiM.py data/A_term_file.txt data/B_terms_file.txt data/C_terms_file.txt sample_output/ 4
  
Output is saved within 'sample_output' folder. This folder contains L1_output, L2_output, and SKiM_output folders. The output from level 1 execution (A to Bs) are saved in L1_output folder. The output from level 2 execution (top n Bs to Cs, where n is number) are saved in L2_output folder. The final output is saved in SKiM_output. L1_output includes 'queries' folder to save various counts between A and every B, and 'with_ratios' folder to save significantly associated Bs with A. L2_output includes three folders: 'queries' folder to save various counts between every B from top n Bs and Cs, 'with_ratios' folder to save significantly associated Cs with every B, and 'all_bc_output' folder to save all B to C associations and significant Bs to Cs associations. L1_output, L2_output, and SKiM_output folders and their sub folders are created automatically during runtime. Please see sample_output folder for details.   

SKiM was developed with Python 3.7.2.   
   
Author: Kalpana Raja and John Steill  
   
Affiliation: Morgridge Institute for Research, Madison, WI, USA.   
