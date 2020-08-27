import sys
import json
import datetime
import requests
import argparse
import os
import os.path
import time
import math
import SKiM_sorter

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

def get_targets_uniquelist(OUTPUT_DIR, sub_dir, filename):
    results = list()
    targets_uniquelist = list()
    INPUT_FILE = os.path.join(OUTPUT_DIR, sub_dir, filename)
    with open(INPUT_FILE, 'r') as infile:
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
            phenotypes = line_list[8]

            if fet_p_value == "0.0":
                log_fet_p_value = -math.log10(float(1.0e-323))
            else:
                log_fet_p_value = -math.log10(float(fet_p_value)) 
            log_ratio = math.log10(float(targ_and_kp_ratio))
            fet_p_value_and_ratio = log_fet_p_value + log_ratio

            results.append(KinderMinerResult(target,
                                                target_and_keyphrase_count,
                                                target_count,
                                                keyphrase_count,
                                                db_article_count,
                                                fet_p_value,
                                                targ_and_kp_ratio,
                                                fet_p_value_and_ratio,
                                                phenotypes))

            if target not in targets_uniquelist:
                targets_uniquelist.append(target)

    return results, targets_uniquelist         

def get_grouped_results(results, targets_uniquelist):
    output_1 = list()
    output_2 = list()
    temp = list()

    for each_target in targets_uniquelist:
        for each_result in results:
            if each_result.target == each_target:
                output_1.append(KinderMinerResult(each_result.target,
                                        each_result.target_and_keyphrase_count,
                                        each_result.target_count,
                                        each_result.keyphrase_count,
                                        each_result.db_article_count,
                                        each_result.fet_p_value,
                                        each_result.targ_and_kp_ratio,
                                        each_result.fet_p_value_and_ratio,
                                        each_result.phenotypes))
                temp.append(KinderMinerResult(each_result.target,
                                        each_result.target_and_keyphrase_count,
                                        each_result.target_count,
                                        each_result.keyphrase_count,
                                        each_result.db_article_count,
                                        each_result.fet_p_value,
                                        each_result.targ_and_kp_ratio,
                                        each_result.fet_p_value_and_ratio, 
                                        each_result.phenotypes))                
        all_p_value, all_ratio, all_sum, all_phen = group_values(temp)
        output_2.append(KinderMinerResult(temp[0].target,
                                        temp[0].target_and_keyphrase_count,
                                        temp[0].target_count,
                                        temp[0].keyphrase_count,
                                        temp[0].db_article_count,
                                        all_p_value,
                                        all_ratio,
                                        all_sum,
                                        all_phen))
        temp.clear()

    return output_1, output_2

def group_values(temp):
    all_p_value = ''
    all_ratio = ''
    all_sum = ''
    all_phen = ''
    for each_temp in temp:
        # grouping fet p-value
        if all_p_value == '':
            all_p_value = str(each_temp.fet_p_value)
        else:
            all_p_value = all_p_value + '|' + str(each_temp.fet_p_value)
        
        # grouping ratio
        if all_ratio == '':
            all_ratio = str(each_temp.targ_and_kp_ratio)
        else:
            all_ratio = all_ratio + '|' + str(each_temp.targ_and_kp_ratio)

        # grouping sum
        if all_sum == '':
            all_sum = str(each_temp.fet_p_value_and_ratio)
        else:
            all_sum = all_sum + '|' + str(each_temp.fet_p_value_and_ratio)

        # grouping phenotypes
        if all_phen == '':
            all_phen = str(each_temp.phenotypes)
        else:
            all_phen = all_phen + '|' + str(each_temp.phenotypes)

    return all_p_value, all_ratio, all_sum, all_phen
