import sys
import json
import datetime
import requests
import argparse
import os.path
import time
import math

class KinderMinerResult(object):
    def __init__(self, target, target_and_keyphrase_count,
                    target_count, keyphrase_count, db_article_count,
                    fet_p_value, targ_and_kp_ratio, 
                    fet_p_value_and_ratio, phenotypes):
        self.target = target
        self.target_and_keyphrase_count = target_and_keyphrase_count
        self.target_count = target_count
        self.keyphrase_count = keyphrase_count
        self.db_article_count = db_article_count
        self.fet_p_value = fet_p_value
        self.targ_and_kp_ratio = targ_and_kp_ratio
        self.fet_p_value_and_ratio = fet_p_value_and_ratio
        self.phenotypes = phenotypes

def get_results(OUTPUT_DIR, sub_dir):
    results = list()
    results_all = list()
    dir_path = os.path.join(OUTPUT_DIR, sub_dir)
    for root, dir, files in os.walk(dir_path):
        for filename in files:
            print(filename)
            phenotype = get_phenotype(filename)
            if filename.endswith("_all.txt"):
                RESULT_FILE = os.path.join(dir_path, filename)
                results_all = read_result_file(RESULT_FILE, 
                                                results_all, phenotype)
            else:
                RESULT_FILE = os.path.join(dir_path, filename)
                results = read_result_file(RESULT_FILE, results, phenotype)
    return results, results_all

def get_phenotype(filename):
    if filename.endswith("_all.txt"):
        phenotype = filename[26:-8]
    else:
        phenotype = filename[26:-4]
    return phenotype    

def read_result_file(RESULT_FILE, result, phenotype):
    with open(RESULT_FILE, 'r') as infile:
        for line in infile:
            if line.startswith('target\t'):
                continue
            line_list = line.strip().split('\t')
            target = line_list[0]
            target_and_keyphrase_count = line_list[1]
            target_count = line_list[2]
            keyphrase_count = line_list[3]
            db_article_count = line_list[4]
            fet_p_value = line_list[5]
            targ_and_kp_ratio = line_list[6]
            fet_p_value_and_ratio = line_list[7]
            phenotypes = phenotype

            if fet_p_value == "0.0":
                log_fet_p_value = -math.log10(float(1.0e-323))
            else:
                log_fet_p_value = -math.log10(float(fet_p_value)) 
            log_ratio = math.log10(float(targ_and_kp_ratio))
            fet_p_value_and_ratio = log_fet_p_value + log_ratio

            result.append(KinderMinerResult(target,
                                                target_and_keyphrase_count,
                                                target_count,
                                                keyphrase_count,
                                                db_article_count,
                                                fet_p_value,
                                                targ_and_kp_ratio,
                                                fet_p_value_and_ratio,
                                                phenotypes))

    return result

def main():
    OUTPUT_DIR = sys.argv[1]
    RESULT_DIR = sys.argv[2]
    sub_dir = "L2_output/with_ratios/"     
   
    # read b-c output files
    results, results_all = get_results(OUTPUT_DIR, sub_dir)

    # sort on FET p-value and ratio
    results_sorted = sorted(results,
                            key=lambda x: float(x.fet_p_value_and_ratio),
                            reverse=True)
    results_sorted_all = sorted(results_all,
                            key=lambda x: float(x.fet_p_value_and_ratio),
                            reverse=True)
    
    # write to file
    write_to_file(RESULT_DIR,
                    results_sorted, 
                    filename="bc_output_sorted_on_prediction_score.txt")
    write_to_file(RESULT_DIR,
                    results_sorted_all,
                    filename="all_bc_output_sorted_on_prediction_score.txt")

def write_to_file(RESULT_DIR, bc_results, filename):
    OUTPUT_FILE = os.path.join(RESULT_DIR,
                                    filename) 
    with open(OUTPUT_FILE, 'w') as outfile:
        outfile.write('target\ttarget_with_keyphrase_count\t' +
                'target_count\tkeyphrase_count\tdb_article_count\t' +
                'fet_p_value\ttarget_and_keyphrase_ratio\t' +
                'fet_p_value_and_ratio\tphenotypes')
        outfile.write('\n')
        for res in bc_results:
            target = res.target
            targ_and_kp = res.target_and_keyphrase_count
            targ_tot = res.target_count
            kp_tot = res.keyphrase_count
            db_tot = res.db_article_count
            p_value = res.fet_p_value
            tkp_ratio = res.targ_and_kp_ratio
            p_value_ratio = res.fet_p_value_and_ratio
            phen = res.phenotypes
            outfile.write(
                    '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}'.format(target,
                                                                targ_and_kp,
                                                                targ_tot,
                                                                kp_tot,
                                                                db_tot,
                                                                p_value,
                                                                tkp_ratio,
                                                                p_value_ratio,
                                                                phen))
            outfile.write('\n')


if __name__ == '__main__':
    main()
