# SKiM
Serial KinderMiner (or simply SKiM) is general literature-based discovery system for querying all ~30 million PubMed abstracts. 

This repository provides the python script for SKiM, a general literature based discovery system for uncovering unknown public knowledge from all ~30 million PubMed articles. This project is done by Stewart Computational Biology Group (https://morgridge.org/research/regenerative-biology/bioinformatics/) within Thomson Lab (https://morgridge.org/research/regenerative-biology/thomson-lab/) at Morgridge Institute for Research, Madison, WI, USA.

A local PubMed database version is required for executing SKiM. 

We applied SKiM for repurposing drugs for four diseases from Swanson's work, Raynaud's disease, migraine, Alzheimer's disease and schizophrenia. We compiled three lexicons from various resources for the study. The diseases lexicon was compiled from UMLS Metathesaurus and SNOMED CT. The drugs lexicon was compiled from UMLS Metathesaurus, DrugBank and PharmGKB. The phenotypes and synonyms lexicon was compiled from Human Phenotypes Ontology (HPO), Phenome Wide Association Studies (PheWAS), and Online Mendelian Inheritance in Man (OMIM). Resources such as UMLS Metathesaurus requires licence. Instead of sharing the lexicons, we share the scripts for compiling the lexicons. 

We compiled a list of disease-drug associations from Comparative Toxicogenomics Database (CTD), National Drug File - Reference Terminology (NDF-RT), DrugBank and ClinicalKey. We used our diseases and drugs lexicon to identify the duplicates across the resources. Instead of sharing the associations, we share the scripts for generating disease-drug associations from various resources.

Basic syntax for executing SKiM:
$ python production_SKiM.py keyphrase level_1_file level_2_file output_dir num_level2_queries

Display help:
$ python production_SKiM.py -h
usage: production_SKiM.py [-h] [--outfile OUTFILE] [-o] [-k] [-s] [-t] [-a]
                          [-db DB_VERSION] [-kf] [-d DELIMITER] [-v] [-p]
                          [-y YEAR] [-ti] [-ab]
                          keyphrase level1_file level2_file output_dir
                          num_level2_queries

Run Serial KinderMiner (SKiM)

positional arguments:
    keyphrase             Keyphrase for Level 1 (A term)
    level1_file           Target terms for Level 1 (B terms)
    level2_file           Target terms for Level 2 (C terms)
    output_dir            directory with output files
    num_level2_queries    number of B terms for Level 2 execution

optional arguments:
-h, --help                                  show this help message and exit
--outfile OUTFILE                           Ranked C term outfile
-o, --overwrite_chtc_query_results          overwrite existing result files
-k, --do_NOT_overwrite_getFET_results       keep existing CHTC result files.
-s, --sep                                   perform keyphrase match as separate tokens
-t, --targ_sep                              perform target term match as separate tokens
-a, --alias                                 perform alias matching for target terms and
                                            keyphrase(aliases for both use a specified delimiter
                                            [default:pipeline])
-db DB_VERSION, --db_version DB_VERSION     PubMed Database version
-kf, --keyphrasefile
-d DELIMITER, --delimiter DELIMITER         defines the delimiter to be used for alias
                                            separationwhen that option is used [default: pipeline]
-v, --verbose                               -v flag for verbose output
-p , --FET_pvalue                           FET cutoff. default:1e-5
-y YEAR, --year YEAR                        limit search to publication year
-ti, --title_excluded                       exclude title; query only in abstract
-ab, --abstract_wo_abbr_expansion           points to original PubMed database, with the
                                            abbrevation expansions turned off.
