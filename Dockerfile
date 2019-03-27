FROM ubuntu

# Install python and nibabel
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    # pip3 install setuptools -U && \
    # apt-get install  -y libblas-dev liblapack-dev libatlas-base-dev gfortran  && \
    apt-get install -y nodejs npm && \
    npm install bids-validator && \
    pip3 install scipy && \
    pip3 install nibabel && \
    pip3 install pybids && \
    # apt-get remove -y python3-pip && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PYTHONPATH=""
ENV PATH /node_modules/bids-validator/bin:$PATH

COPY run.py /run.py

COPY version /version

ENTRYPOINT ["/run.py"]
