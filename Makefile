docker-build:
	docker build -t rt .

run:
	docker run -i --rm -v /Users/poldrack/data_unsynced/ds001715-download:/bids_dataset rt /bids_dataset 


shell:
	docker run -v /Users/poldrack/data_unsynced/ds001715-download:/bids_dataset:ro -it --entrypoint=bash rt
