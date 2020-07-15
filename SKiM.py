from chtc_query import MatchText

import os
import os.path

def read_input_file(FILE_NAME,
                    SEP_KP, 
                    STEM_KP, 
                    ALIAS, 
                    TITLE, 
                    DELIM,
                    ABSTRACT_IS_LONGFORM):
    # read files
    with open(FILE_NAME) as infile:
        file_list = [MatchText(k, SEP_KP, STEM_KP, ALIAS, TITLE, DELIM,
                        ABSTRACT_IS_LONGFORM) for k in infile]
    return file_list

def write_to_file(output,
                  OUTPUT_DIR,
                  sub_dir,
                  output_file):
    # write the output to file
    outfile_path_name = os.path.join(OUTPUT_DIR, 
                                     sub_dir,
                                     output_file)
    with open(outfile_path_name, 'w') as out_fh:
        for outstr in output:
            out_fh.write(outstr + '\n')
