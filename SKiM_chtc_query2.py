import sys
import pdb
import json
import datetime
import requests
import argparse
import os.path
import time

from requests.auth import HTTPBasicAuth

# some constants for search
URL_BASE = 'http://deepdive2000.chtc.wisc.edu/es/articles_pubmed_march2019/article/_count'
AUTH = HTTPBasicAuth('dduser', 'searchtime')

def make_query_object(target_term, key_phrase, through_year):
    # build the constraint list first
    should_tt = []
    should_kp = []
    must = []

    # are we searching on a target term
    if target_term is not None:
        target_list = target_term[1]
        for target_tok in target_list:
            should_tt.append({
                'match_phrase' : {'title' : target_tok},
                })
            should_tt.append({ 
                'match_phrase' : {'abstract_long_form' : target_tok}
                })
    
    # and key phrase
    if key_phrase is not None:
        kp_list = key_phrase[1]
        for kp_tok in kp_list:
            should_kp.append({
                'match_phrase' : {'title' : kp_tok},
                })
            should_kp.append({
                'match_phrase' : {'abstract_long_form' : kp_tok}
                })  
            
    # always add the year constraint
    must.append({
        'bool': {
            'should': should_tt
        }
    })
    must.append({
        'bool': {
            'should': should_kp
        }
    })
    must.append({'range' : {'publication_date.year' : {'lte' : through_year}}})
    query = {'query': {'bool': {'must': must } } }
    
    return query

def get_count(target_term, key_phrase, through_year):
    key = str((target_term, key_phrase, through_year))
    q = make_query_object(target_term, key_phrase, through_year)
    res = requests.get(URL_BASE, data=json.dumps(q), auth=AUTH,
                        headers={'Content-Type': 'application/json'})
    ret_cnt = res.json()['count']
    return ret_cnt

def build_arg_parser():
    parser = argparse.ArgumentParser(description='Run a KinderMiner search on CHTC')
    parser.add_argument('-s', '--sep', 
                        action='store_true', 
                        help='perform keyphrase match as separate tokens')
    parser.add_argument('-y', '--year', 
                        type=int, 
                        default=datetime.datetime.now().year, 
                        help='limit search to publications through particular year')
    parser.add_argument('term_file', 
                        help='file containing ID and target terms+synonyms, one per line')
    parser.add_argument('keyphrase', 
                        help='file containing ID and keyphrase+synonyms, one per line') 
    return parser

# this is the API version used for the web interface
def run_full_query(all_targets, key_phrase, through_year=None, sep_kp=False):
    # handle through year
    if through_year is None:
        through_year = datetime.datetime.now().year
    # handle separated key phrase
    if sep_kp:
        key_phrase = key_phrase.strip().split()
    # we will return this as a dictionary stored somewhat compactly
    ret = dict()
    # compute the total number of articles in the database
    db_article_cnt = get_count(None, None, through_year, URL_BASE, AUTH)
    ret['db_article_cnt'] = db_article_cnt
    # and the number of times the key phrase shows up
    kp_cnt = get_count(None, key_phrase, through_year, URL_BASE, AUTH)
    ret['kp_cnt'] = kp_cnt
    # now go through each target
    ret['target'] = list()
    ret['targ_cnt'] = list()
    ret['targ_with_kp_cnt'] = list()
    for target in all_targets:
        targ_with_kp_cnt = 0
        # first the individual count
        targ_cnt = get_count(target, None, through_year, URL_BASE, AUTH)
        # only need to query combined if articles exist for both individually
        if targ_cnt > 0 and kp_cnt > 0:
            # now do both key phrase and target
            targ_with_kp_cnt = get_count(target, key_phrase, through_year, URL_BASE, AUTH)
        ret['target'].append(target)
        ret['targ_cnt'].append(targ_cnt)
        ret['targ_with_kp_cnt'].append(targ_with_kp_cnt)
    return ret

def get_terms_asTokens(FILE_NAME):
    terms_asTokens = {}
    with open(FILE_NAME, 'r') as infile:
        for line in infile:
            tmp = line.strip().split('\t')
            if len(tmp) == 1:
                tmp = line.strip().split('   ')
            assert len(tmp)==2, "we expect just id and |-separated string here"
            var = tmp[1].strip().split('|')
            tokens = []
            for el in var:
                t = el.split(' ')
                if len(t) == 0:
                    tokens = [el for el in range(t)]
                else:
                    tokens.extend(t)
            unique_tokens_only = list(set(i.lower() for i in tokens))
            terms_synonyms[tmp[0]] =  unique_tokens_only
    return terms_asTokens

def get_terms_synonyms(FILE_NAME):
    terms_synonyms = {}
    if os.path.isfile(FILE_NAME):
        with open(FILE_NAME, 'r') as infile:
            for line in infile:
                tmp = line.strip().split('\t')
                if len(tmp) == 1:
                    tmp = line.strip().split('   ')
                assert len(tmp)==2, "we expect just id and |-separated string here"
                terms_synonyms[tmp[0]] = tmp[1].strip().split('|')
    else:
        (id, term) = FILE_NAME.strip().split(':')
        terms_synonyms[id] = term.strip().split('|')
    return terms_synonyms

def get_output_filename(CUI_key, kp_synonym_list):
    cuikey = CUI_key.split('_')[0]
    syn = kp_synonym_list[0].replace(' ', '_')
    output_file = cuikey + '_' + syn
    return output_file

def get_synonyms_for_selected_bs(level2_results, level2_dictionary):
    selected_bs_synonyms = {}
    for result in level2_results:
        b_id_term = result.split(':')
        b_synonyms = level2_dictionary.get(b_id_term[0])
        selected_bs_synonyms[b_id_term[0]] = b_synonyms
    return selected_bs_synonyms

def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    # command line args
    TARGET_TERM_FILE = args.term_file
    KEY_PHRASE_FILE_NAME = args.keyphrase
    THROUGH_YEAR = args.year
    SEPARATE_KP = args.sep

    # read keyphrases from file
    if SEPARATE_KP:
        assert False, "have to deal with filename"
        key_phrases_asTokens = get_terms_asTokens(KEY_PHRASE_FILE_NAME)
     
    
    results = perform_all_chtc_queries(
            KEY_PHRASE_FILE_NAME,
            TARGET_TERM_FILE,
            THROUGH_YEAR,
            SEPARATE_KP)

def perform_all_chtc_queries(
        KEY_PHRASE_FILE_NAME, TARGET_TERM_FILE, THROUGH_YEAR, SEPARATE_KP):

    key_phrases = get_terms_synonyms(KEY_PHRASE_FILE_NAME)    

    # read the all the target terms to query
    target_terms = get_terms_synonyms(TARGET_TERM_FILE)
        
    # compute the total number of articles in the database
    db_article_cnt = get_count(None, None, THROUGH_YEAR)

    # and the number of times the key phrase shows up
    return_array = []
    id_synonyms = {}
    for key_phrase in key_phrases.items():
        kp_cnt = get_count(None, key_phrase, THROUGH_YEAR)

        return_array.append('target\ttarget_with_keyphrase_count\t' +
                'target_count\tkeyphrase_count\tdb_article_count')
        for target in target_terms.items():
            targ_with_kp_cnt = 0
            
            # if key_phrase and target_term are same, skip execution
            if key_phrase == target:
                continue             

            # first the individual count
            targ_cnt = get_count(target, None, THROUGH_YEAR) 
        
            # only need to query if articles exist for both individually
            if targ_cnt > 0 and kp_cnt > 0:
                # now do both key phrase and target
                targ_with_kp_cnt = get_count(target, key_phrase, THROUGH_YEAR)

            key = target[0]
            value = target[1]
            id_synonyms[key] = value
            outstr = '{0}\t{1}\t{2}\t{3}\t{4}'.format(key+':'+value[0], +
                                                        targ_with_kp_cnt, +
                                                        targ_cnt, + 
                                                        kp_cnt, +
                                                        db_article_cnt)
            # print (outstr)
            return_array.append(outstr)
        return return_array, id_synonyms


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()

    #print(end - start)
