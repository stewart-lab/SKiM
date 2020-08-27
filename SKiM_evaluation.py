from __future__ import print_function
import sys
import os
import os.path
import argparse
import datetime
import time
import multiprocessing
from multiprocessing import Pool
import pdb
import re
import scipy.stats as stats
import glob
import math

CUI_SPLITTER = ('   ', '\t')


class KinderMinerCount(object):
    def __init__(self,
                    target,
                    target_and_keyphrase_count,
                    target_count,
                    keyphrase_count,
                    db_article_count):
        self.target = target
        self.target_and_keyphrase_count = target_and_keyphrase_count
        self.target_count = target_count
        self.keyphrase_count = keyphrase_count
        self.db_article_count = db_article_count
        self.notarget_count = db_article_count - target_count
        self.nokeyphrase_count = db_article_count - keyphrase_count
        self.target_and_nokeyphrase_count = \
                            target_count - target_and_keyphrase_count
        self.notarget_and_keyphrase_count = \
                            keyphrase_count - target_and_keyphrase_count
        self.notarget_and_nokeyphrase_count = \
            self.nokeyphrase_count - self.target_and_nokeyphrase_count


class KinderMinerResult(object):
    def __init__(self, 
                 target, 
                 p_value, 
                 target_and_keyphrase_ratio,
                 fet_p_value_and_ratio):
        self.target = target
        self.p_value = p_value
        self.target_and_keyphrase_ratio = target_and_keyphrase_ratio
        self.fet_p_value_and_ratio = fet_p_value_and_ratio

def evaluate_pvalue_and_sort(results, p_val_cutoff=1e-5):
    """Evaluate KinderMiner results from Level 1 and Level 2"""
    counts_list = []
    counts_dict = {}
    lines = iter(results)
    line = lines.__next__()
    (targ_name_ind,
            targ_withkp_ind,
            targ_count_ind,
            kp_count_ind,
            total_count_ind) = line.strip().split('\t')
    for line in  lines:
        (name, targ_and_kp, targ_tot, kp_tot, db_tot) = \
                                            line.strip().split('\t')
        (targ_tot, kp_tot, db_tot, targ_and_kp) = (
                                            int(targ_tot),
                                            int(kp_tot),
                                            int(db_tot),
                                            int(targ_and_kp))
        km_count = KinderMinerCount(name,
                                    targ_and_kp,
                                    targ_tot,
                                    kp_tot,
                                    db_tot)
        counts_dict[name] = km_count
        counts_list.append(km_count)

    # now compute the FET and ratios
    km_results, km_results_all = \
                compute_kinderminer_results(counts_list, p_val_cutoff)

    # now sort by prediction score (FET p-value and ratio)
    km_results = sorted(km_results,
                        key=lambda x: float(x.fet_p_value_and_ratio),
                        reverse=True)

    # various outputs
    output, output_all, return_array = output_for_files(km_results,
                                                        km_results_all,
                                                        counts_dict)
    return output, output_all, return_array

def output_for_files(km_results, km_results_all, counts_dict):
    # return output
    return_array = []
    output = []
    output.append('target\ttarg_and_kp\ttarg_tot\tkp_tot\tdb_tot\t'
                            'fet_p_value\ttarg_and_kp_ratio\tprediction_score')
    for kmr in km_results:
        targ = kmr.target
        targ_and_kp = counts_dict[targ].target_and_keyphrase_count
        targ_tot = counts_dict[targ].target_count
        kp_tot = counts_dict[targ].keyphrase_count
        db_tot = counts_dict[targ].db_article_count
        p_value = kmr.p_value
        tkp_ratio = kmr.target_and_keyphrase_ratio
        fet_p_value_and_ratio = kmr.fet_p_value_and_ratio
        output.append('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format(
                                                        targ,
                                                        targ_and_kp,
                                                        targ_tot,
                                                        kp_tot,
                                                        db_tot,
                                                        p_value,
                                                        tkp_ratio,
                                                        fet_p_value_and_ratio))
        return_array.append(targ)

    output_all = []
    output_all.append('target\ttarg_and_kp\ttarg_tot\tkp_tot\tdb_tot\t'
                            'fet_p_value\ttarg_and_kp_ratio\tprediction_score')
    for kmr_all in km_results_all:
        targ_all = kmr_all.target
        targ_and_kp_all = \
                        counts_dict[targ_all].target_and_keyphrase_count
        targ_tot_all = counts_dict[targ_all].target_count
        kp_tot_all = counts_dict[targ_all].keyphrase_count
        db_tot_all = counts_dict[targ_all].db_article_count
        p_value_all = kmr_all.p_value
        tkp_ratio_all = kmr_all.target_and_keyphrase_ratio
        fet_p_value_and_ratio_all = kmr_all.fet_p_value_and_ratio
        output_all.append(
                '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format(
                                                    targ_all,
                                                    targ_and_kp_all,
                                                    targ_tot_all,
                                                    kp_tot_all,
                                                    db_tot_all,
                                                    p_value_all,
                                                    tkp_ratio_all,
                                                    fet_p_value_and_ratio_all))
    return output, output_all, return_array

def compute_kinderminer_results(km_counts, p_cutoff=float('1e-5')):
    """Filter KinderMiner results meeting cut-off"""
    ret_all = list()
    ret = list()
    for kmc in km_counts:
        targ_and_kp = kmc.target_and_keyphrase_count
        notarg_and_kp = kmc.notarget_and_keyphrase_count
        targ_and_nokp = kmc.target_and_nokeyphrase_count
        notarg_and_nokp = kmc.notarget_and_nokeyphrase_count
        # compute FET p
        odds_ratio,p_value = \
                stats.fisher_exact([[targ_and_kp,notarg_and_kp],
                                    [targ_and_nokp,notarg_and_nokp]],
                                    alternative='greater')
        # compute ratio
        ratio_denom = targ_and_kp + targ_and_nokp
        if p_value < p_cutoff and ratio_denom > 0:
            # compute ratio
            targ_and_kp_ratio = float(targ_and_kp) / float(ratio_denom)
            # computer FET p + ratio
            if p_value == 0.0:
                log_fet_p_value = -math.log10(float(1.0e-323))
            else:
                log_fet_p_value = -math.log10(float(p_value))
            log_ratio = math.log10(float(targ_and_kp_ratio))
            fet_p_value_and_ratio = log_fet_p_value + log_ratio
            ret.append(KinderMinerResult(kmc.target,
                                            p_value,
                                            targ_and_kp_ratio,
                                            fet_p_value_and_ratio))
            ret_all.append(KinderMinerResult(kmc.target,
                                            p_value,
                                            targ_and_kp_ratio,
                                            fet_p_value_and_ratio))
        elif p_value >= p_cutoff and ratio_denom > 0:
            if targ_and_kp > 0:
                targ_and_kp_ratio = float(targ_and_kp) / float(ratio_denom)
                log_fet_p_value = -math.log10(float(p_value))
                log_ratio = math.log10(float(targ_and_kp_ratio))
                fet_p_value_and_ratio = log_fet_p_value + log_ratio
                ret_all.append(KinderMinerResult(kmc.target,
                                                p_value,
                                                targ_and_kp_ratio,
                                                fet_p_value_and_ratio))
    return ret, ret_all


if __name__ == '__main__':
    main()

