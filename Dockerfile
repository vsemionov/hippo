FROM python:2.7
COPY . /hippo
WORKDIR /hippo
RUN pip install -r requirements.txt
