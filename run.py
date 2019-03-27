#!/usr/bin/env python3
"""
example of BIDS app for BIDS compmodels

"""

import argparse
import os
import subprocess
import nibabel
import numpy
from glob import glob
import pandas
import json
from bids import BIDSLayout, BIDSValidator

__version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'version')).read()

def run(command, env={}):
    merged_env = os.environ
    merged_env.update(env)
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True,
                               env=merged_env)
    while True:
        line = process.stdout.readline()
        line = str(line, 'utf-8')[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d"%process.returncode)

# these are standard input arguments for any BIDS-app

parser = argparse.ArgumentParser(description='Example BIDS App entrypoint script.')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                    'Multiple participant level analyses can be run independently '
                    '(in parallel) using the same output_dir.',
                    choices=['participant', 'group'])
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored. If you are running group level analysis '
                    'this folder should be prepopulated with the results of the'
                    'participant level analysis. Defaults to <bids dir>/derivatives/rt',
                    nargs="?")
parser.add_argument('--participant_label', help='The label(s) of the participant(s) that should be analyzed. The label '
                   'corresponds to sub-<participant_label> from the BIDS spec '
                   '(so it does not include "sub-"). If this parameter is not '
                   'provided all subjects should be analyzed. Multiple '
                   'participants can be specified with a space separated list.',
                   nargs="+")
parser.add_argument('--rt_var_name',help='name for response time variable in events file',
                    default='RT',nargs="?")
parser.add_argument('--skip_bids_validator', help='Whether or not to perform BIDS dataset validation',
                   action='store_true')
parser.add_argument('-v', '--version', action='version',
                    version='BIDS-App example version {}'.format(__version__))


args = parser.parse_args()

if not args.skip_bids_validator:
    run('bids-validator %s'%args.bids_dir)

if args.output_dir is not None:
    output_dir = args.output_dir 
else:
    output_dir = os.path.join(args.bids_dir,'derivatives/rt')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# load BIDS layout
layout = BIDSLayout(args.bids_dir)
print(layout)
dataset_description = layout.description
dataset_description['PipelineDescription']={'Name':'Mean RT analysis example'}
with open(os.path.join(output_dir,'dataset_description.json'),'w') as f:
    json.dump(dataset_description,f)


#running participant level
if args.analysis_level == "participant":

    # only for a subset of subjects
    if args.participant_label:
        subcodes = args.participant_label
    # for all subjects
    else:
        # Ask get() to return the ids of subjects that have func files
        subcodes = layout.get(return_type='id', target='subject', suffix='events')

    # compute mean RT for each run/subject
    for s in subcodes:
        subdata = []
        print('processing subject',s)
        func_files = layout.get(suffix='events', subject=s)
        for f in func_files:
            d = pandas.read_csv(f.path,sep='\t')
            try:
                assert args.rt_var_name in d.columns
            except:
                raise Exception('rt_var_name %s is not found in the data file'%args.rt_var_name)
            meanRT = d[args.rt_var_name].mean()
            subdata.append([s,f.entities['run'],meanRT])
        subdata_df = pandas.DataFrame(subdata,columns=['subject','run','runMeanRT']).sort_values(['subject','run'])

        sub_output_dir = os.path.join(output_dir,'sub-%s/func'%s)
        if not os.path.exists(sub_output_dir):
            os.makedirs(sub_output_dir)

        subdata_df.to_csv(os.path.join(sub_output_dir,
            'sub-%s_task-%s_runMeanRT.tsv'%(f.entities['subject'],f.entities['task'])),
            index=False,sep='\t')


# running group level
elif args.analysis_level == "group":
    # load the layout with derivatives
    layout2 = BIDSLayout(args.bids_dir, derivatives=True)
    print(layout2)
    # get all of the meanRT files
    meanRTfiles = layout2.get(suffix='runMeanRT')

    groupdata = []
    for f in meanRTfiles:
        df = pandas.read_csv(f.path,sep='\t')
        groupdata.append([f.entities['subject'],df.runMeanRT.mean()])
    groupdata_df = pandas.DataFrame(groupdata,columns=['subject','meanRT']).sort_values(['subject'])
    groupdata_df.to_csv(os.path.join(output_dir,'participants.tsv'),sep='\t',index=False)
