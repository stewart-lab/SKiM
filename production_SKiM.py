import os
import re
import pdb
import datetime
import time
import unittest
import argparse
import SKiM_output
import SKiM_chtc_query2
import SKiM_evaluation
import SKiM_sorter
import SKiM_output_grouper

def build_arg_parser():
    parser = argparse.ArgumentParser(
                        description='Run Serial KinderMiner (SKiM)')
    parser.add_argument('keyphrase', 
                        help='Keyphrase for Level 1 (A term)')
    parser.add_argument('level1_file', 
                        help='Target terms for Level 1 (B terms)')
    parser.add_argument('level2_file', 
                        help='Target terms for Level 2 (C terms)')
    parser.add_argument('output_dir',
                        help='directory with output files')
    parser.add_argument('--outfile', 
                        help='Ranked C term outfile', 
                        default='Ranked_C_terms_SKiM_output.txt')
    parser.add_argument('num_level2_queries', 
                        help='number of B terms for Level 2 execution')
    parser.add_argument('-o', 
                        '--overwrite_chtc_query_results', 
                        action='store_true', 
                        help='overwrite existing result files')
    parser.add_argument('-k', 
                        '--do_NOT_overwrite_getFET_results', 
                        action='store_true', 
                        help='keep existing CHTC result files.')
    parser.add_argument('-s', '--sep',
                        action='store_true',
                        help='perform keyphrase match as separate tokens')
    parser.add_argument('-t', '--targ_sep', action='store_true',
                        help='perform target term match as separate tokens')
    parser.add_argument('-a', '--alias', action='store_true',
            help='perform alias matching for target terms and keyphrase' +
            '(aliases for both use a specified delimiter [default:pipeline])')
    parser.add_argument('-db', '--db_version', type=str,
            default=str(datetime.datetime.now().strftime("%B").lower()) + \
                    str(datetime.datetime.now().year),
            help='PubMed Database version')
    parser.add_argument('-kf', '--keyphrasefile', action='store_true')
    parser.add_argument('-d', '--delimiter', default='|',
            help='defines the delimiter to be used for alias separation' +
            'when that option is used [default: pipeline]')
    parser.add_argument('-v', '--verbose', 
                        action='store_true', 
                        help='-v flag for verbose output')
    parser.add_argument('-p', '--FET_pvalue', 
                        help='FET cutoff. default:1e-5', 
                        metavar='', 
                        default='1e-5')
    parser.add_argument('-y', '--year',
                        type=int,
                        default=datetime.datetime.now().year,
                        help='limit search to publication year')
    parser.add_argument('-ti', '--title_excluded', action='store_true',
            help='exclude title; query only in abstract')
    parser.add_argument('-ab', '--abstract_wo_abbr_expansion',
            action='store_true',
            help='points to original PubMed database, with the abbrevation' +
            ' expansions turned off.' )
    return parser

def main():    
    results = []
    parser = build_arg_parser()
    args = parser.parse_args()     

    KEY_PHRASE_FILE_NAME = args.keyphrase
    TARGET_TERM_FILE1 = args.level1_file
    TARGET_TERM_FILE2 = args.level2_file
    OUTPUT_DIR = args.output_dir
    OUTFILE = args.outfile
    NUM_LEVEL2 = args.num_level2_queries
    THROUGH_YEAR = args.year
    SEPARATE_KP = args.sep

    # chtc query - Level 1
    ab_results, b_dictionary = \
        SKiM_chtc_query2.perform_all_chtc_queries(KEY_PHRASE_FILE_NAME, 
                                                  TARGET_TERM_FILE1,
                                                  THROUGH_YEAR, 
                                                  SEPARATE_KP)
    SKiM_output.write_to_file(ab_results, 
                       OUTPUT_DIR,
                       sub_dir = "L1_output/queries/", 
                       output_file = "ab_chtc_query_results.txt")
    
    # evaluate - Level 1    
    ab_output, ab_output_all, ab_bterms = \
        SKiM_evaluation.evaluate_pvalue_and_sort(ab_results)
    SKiM_output.write_to_file(ab_output, 
                       OUTPUT_DIR,
                       sub_dir = "L1_output/with_ratios/", 
                       output_file = "ab_output_metpvaluecutoff.txt")
    SKiM_output.write_to_file(ab_output_all,
                       OUTPUT_DIR,
                       sub_dir = "L1_output/with_ratios/",
                       output_file = "ab_output_all.txt")
    
    # get synonyms for b terms
    b_synonyms = \
        SKiM_chtc_query2.get_synonyms_for_selected_bs(ab_bterms, 
                                                      b_dictionary)
    
    # Level 2    
    count = 0
    for ab_i_bterms in ab_bterms:
        # chtc query
        bc_results, c_dictionary = \
            SKiM_chtc_query2.perform_all_chtc_queries(ab_i_bterms, 
                                                      TARGET_TERM_FILE2,
                                                      THROUGH_YEAR, 
                                                      SEPARATE_KP)
        bterm = ab_i_bterms.split(":")[1]
        bterm = bterm.replace(' ','_' )
        SKiM_output.write_to_file(bc_results,
                           OUTPUT_DIR,
                           sub_dir = "L2_output/queries/",
                           output_file = "bc_chtc_query_results_" + \
                                            bterm + ".txt")
        
        # evaluate
        bc_output, bc_output_all, bc_cterms = \
            SKiM_evaluation.evaluate_pvalue_and_sort(bc_results) 
            
        SKiM_output.write_to_file(bc_output, 
                           OUTPUT_DIR,
                           sub_dir = "L2_output/with_ratios/",  
                           output_file = "bc_output_metpvaluecutoff_" \
                                            + bterm + ".txt")
        SKiM_output.write_to_file(bc_output_all,
                           OUTPUT_DIR,
                           sub_dir = "L2_output/with_ratios/",
                           output_file = "bc_output_metpvaluecutoff_" \
                                            + bterm + "_all.txt") 
        
        # break at selected number of b terms
        count = count + 1
        if count >= int(NUM_LEVEL2):
            break    

    # final output - C terms are ranked on prediction score
    c_output, c_output_all = SKiM_sorter.get_results(
                                            OUTPUT_DIR, 
                                            sub_dir = "L2_output/with_ratios/") 
    c_output_sorted, c_output_all_sorted = SKiM_sorter.sort_output(c_output, 
                                                                c_output_all)
    sub_dir = "L2_output/all_bc_output/"
    SKiM_sorter.write_to_file(OUTPUT_DIR,
                    sub_dir,
                    c_output_sorted,
                    filename = "bc_output_sorted_on_prediction_score.txt")
    SKiM_sorter.write_to_file(OUTPUT_DIR,
                    sub_dir,
                    c_output_all_sorted,
                    filename = "all_bc_output_sorted_on_prediction_score.txt")
    
    # final output - C terms are ranked and grouped
    results, uniquetargets = \
                    SKiM_output_grouper.get_targets_uniquelist(OUTPUT_DIR,
                        sub_dir = "L2_output/all_bc_output/",
                        filename = "bc_output_sorted_on_prediction_score.txt")
    output_1, output_2 = SKiM_output_grouper.get_grouped_results(
                                                            c_output_sorted, 
                                                            uniquetargets)
    sub_dir = "SKiM_output/"
    SKiM_sorter.write_to_file(OUTPUT_DIR,
                    sub_dir,
                    output_1,
                    filename = "bc_output_1.txt")
    SKiM_sorter.write_to_file(OUTPUT_DIR,
                    sub_dir,
                    output_2,
                    filename = "bc_output_2.txt")

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()

    print(end - start)
