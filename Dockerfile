FROM python:2.7
COPY . /hippo
WORKDIR /hippo
RUN pip install -r requirements.txt
RUN groupadd hippo && useradd -g hippo hippo
USER hippo
