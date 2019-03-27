## An example BIDS App using pybids

This is a fork of the original BIDS Apps example, which was built prior to the existence of [pybids](https://github.com/bids-standard/pybids). At the participant level, the entry point script (run.py) will:

- validates and loads a BIDS dataset using pybids
- finds all of the event.tsv files
- computes the mean of the specified response time column (default='RT')
- saves the run means to derivatives/rt/sub-XX/func/sub-XX_task-XX_runMeanRT.tsv

At the group level, it will load all of the participant run mean files, compute the overall mean for each subject, and save them to derivatives/rt/participants.tsv

For more information about the specification of BIDS Apps see [here](https://docs.google.com/document/d/1E1Wi5ONvOVVnGhj21S1bmJJ4kyHFT7tkxnV3C23sjIE/edit#).


### Usage
This App has the following command line arguments:

		usage: run.py [-h]
		              [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
		              bids_dir output_dir {participant,group}

		Example BIDS App entry point script.

		positional arguments:
		  bids_dir              The directory with the input dataset formatted
		                        according to the BIDS standard.
		  {participant,group}   Level of the analysis that will be performed. Multiple
		                        participant level analyses can be run independently
		                        (in parallel).

		optional arguments:
		  -h, --help            show this help message and exit
		  --output_dir          The directory where the output files should be stored.
		                        If you are running a group level analysis, this folder
		                        should be prepopulated with the results of
		                        the participant level analysis.
		  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
		                        The label(s) of the participant(s) that should be
		                        analyzed. The label corresponds to
		                        sub-<participant_label> from the BIDS spec (so it does
		                        not include "sub-"). If this parameter is not provided
		                        all subjects will be analyzed. Multiple participants
		                        can be specified with a space separated list.
			--rt_var_name VARIABLE_NAME
														name for response time variable in events file
                    				default='RT'

To build the dockerfile (creating an image called "rt"):

	make docker-build

To run it in participant level mode (for all participants):

    docker run -i --rm \
		-v <local path to bids dataset>:/bids_dataset \
		rt /bids_dataset participant

To run the group level:

   	docker run -i --rm \
		-v <local path to bids dataset>:/bids_dataset \
		rt /bids_dataset group

### Example

For a working example, download [ds001715](https://openneuro.org/datasets/ds001715/versions/1.0.0) from OpenNeuro and then use that directory as the local BIDS dataset path.
