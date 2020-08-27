import os
import os.path

def write_to_file(output,
                  OUTPUT_DIR,
                  sub_dir,
                  output_file):
    # check whether the sub directories exist within the output directory
    outfile_path_name = os.path.join(OUTPUT_DIR, 
                                     sub_dir)
    isdir = os.path.isdir(outfile_path_name)
    
    # create the sub directories if absent
    if isdir == False:
        try:
            os.makedirs(outfile_path_name)
        except OSError:
            print ("Creation of the output directory %s failed" % outfile_path_name)

    # write the output to file
    outfile = os.path.join(outfile_path_name,
                              output_file)
    with open(outfile, 'w') as out_fh:
        for outstr in output:
            out_fh.write(outstr + '\n')
