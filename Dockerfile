FROM python:2.7
RUN groupadd hippo && useradd -g hippo hippo
COPY . /hippo
WORKDIR /hippo/hippo
RUN pip install -r ../requirements.txt
