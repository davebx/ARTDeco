'''
Script for running diff_exp_read_in mode.
'''
from ARTDeco.modules.DESeq2 import reformat_meta,reformat_comparisons,generate_comparisons,load_deseq_dataset,run_deseq,\
    deseq_results

import sys
import os

def main(argv):

    home_dir = argv[0]
    meta_file = argv[1]
    comparisons_file = argv[2]
    overwrite = bool(argv[3] == 'True')

    #Checking prerequisites.
    print('Checking prerequisites...')

    if os.path.isfile(os.path.join(home_dir,'dogs','all_dogs.raw.txt')):
        print('DoG expression file exists...')
    else:
        print('DoG expression file does not exist... Re-run DoG finding step...')
        sys.exit(1)

    #Check input format.
    print('Checking meta file...')

    #Check meta file.
    if os.path.isfile(meta_file):

        meta = open(meta_file).readlines()
        meta_format = True
        groups = []
        i = 0
        while i < len(meta) and meta_format:

            line = meta[i].strip().split('\t')

            #If the length of the split line is different than 2, the meta file isn't properly formatted.
            if len(line) != 2:
                meta_format = False

            #Otherwise, ensure that the first line is the proper format.
            else:
                if i == 0:
                    if line[0] != 'Experiment' or line[1] != 'Group':
                        meta_format = False
                else:
                    if line[1] not in groups:
                        groups.append(line[1])

            i += 1

        if meta_format:
            print('Meta file properly formatted...')
        else:
            print('Meta file not properly formatted... Exiting...')
            sys.exit(1)

    else:
        print('Meta file does not exist... Exiting...')
        sys.exit(1)

    #Reformat meta file.
    print('Checking meta file...')
    if os.path.isfile(os.path.join(home_dir,'preprocess_files','meta.reformatted.txt')) and not overwrite:
        print('Reformatted meta file exists...')
    else:
        print('Reformatting meta file...')
        reformat_meta(meta_file,os.path.join(home_dir,'preprocess_files'))

    #Reformat/generate comparisons file.
    print('Checking/generating comparisons file...')
    if os.path.isfile(comparisons_file):

        print('Comparisons file exists...')

        #Check format.
        comparisons = [line.strip().split('\t') for line in open(comparisons_file).readlines()]
        comparisons_lens = [len(line) for line in comparisons]

        #Check if lines are tab-separated formatted.
        if len(set(comparisons_lens)) == 1 and len(comparisons[0]) == 2:

            membership = [(line[0] in groups and line[1] in groups) for line in comparisons]

            if len(set(membership)) == 1 and membership[0]:
                comparisons_format = True
            else:
                comparisons_format = False
        else:
            comparisons_format = False

        #If the file is properly formatted, reformat it. Otherwise, generate an all-by-all file.
        if comparisons_format:
            print('Comparisons file properly formatted... Reformatting...')
            reformat_comparisons(comparisons_file, os.path.join(home_dir,'preprocess_files'))
        else:
            print('Comparisons file not properly formatted... Generating all-by-all comparisons file...')
            generate_comparisons(os.path.join(home_dir,'preprocess_files','meta.reformatted.txt'),
                                 os.path.join(home_dir,'preprocess_files'))

    else:
        print('Comparison file does not exist or not provided... Generating comparisons file...')
        generate_comparisons(os.path.join(home_dir,'preprocess_files','meta.reformatted.txt'),
                             os.path.join(home_dir,'preprocess_files'))

    #Run DESeq2.
    print('Check for DESeq2 output...')
    all_comparisons = True
    for condition1, condition2 in comparisons:
        if not os.path.isfile(os.path.join(home_dir,'diff_exp_dogs',f'{condition1}-{condition2}-results.txt')):
            all_comparisons = False

    if all_comparisons and not overwrite:
        print('DESeq2 results exist...')
    else:
        print('Running DESeq2')
        dds = load_deseq_dataset(os.path.join(home_dir,'dogs','all_dogs.raw.txt'),
                                 os.path.join(home_dir,'preprocess_files','meta.reformatted.txt'))
        dds_results = run_deseq(dds)

        #Create differential expression directory.
        if os.path.isdir(os.path.join(home_dir,'diff_exp_dogs')):
            print('Differential expression directory exists...')
        else:
            print('Creating differential expression directory...')
            os.mkdir(os.path.join(home_dir, 'diff_exp_dogs'))

        #Output results.
        print('Output DESeq2 results...')
        for condition1, condition2 in comparisons:
            deseq_results(dds_results,condition1,condition2,os.path.join(home_dir,'diff_exp_dogs'))


if __name__ == '__main__':
    main(sys.argv[1:])