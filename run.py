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

parser = argparse.ArgumentParser(description='Example BIDS App entrypoint script.')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('--skip_bids_validator', help='Whether or not to perform BIDS dataset validation',
                   action='store_true')
parser.add_argument('-v', '--version', action='version',
                    version='BIDS-App example version {}'.format(__version__))


args = parser.parse_args()

if not args.skip_bids_validator:
    run('bids-validator %s'%args.bids_dir)


layout = BIDSLayout(args.bids_dir)

print(layout)

# Ask get() to return the ids of subjects that have func files
subcodes = layout.get(return_type='id', target='subject', suffix='events')


# compute mean RT for each run/subject
subdata = []

for s in subcodes:
    print('processing subject',s)
    func_files = layout.get(suffix='events', subject=s)
    for f in func_files:
        meanRT = pandas.read_csv(os.path.join(f.dirname,f.filename),sep='\t').query('isMissedTrial == 0').RT.mean()
        subdata.append([s,f.entities['run'],meanRT])

# create a data frame and save to derivatives
subdata_df = pandas.DataFrame(subdata,columns=['subject','run','meanRT']).sort_values(['subject','run'])

deriv_path = os.path.join(args.bids_dir,'derivatives/rt')
if not os.path.exists(deriv_path):
    os.makedirs(deriv_path)

subdata_df.to_csv(os.path.join(deriv_path,'mean_rt.tsv'),sep='\t',index=False)