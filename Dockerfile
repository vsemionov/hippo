FROM python:2.7
RUN apt-get update && apt-get install -y nginx
RUN groupadd hippo && useradd -g hippo hippo
COPY . /hippo
RUN pip install -r /hippo/requirements.txt
RUN bash -c "echo yes | python /hippo/hippo/manage.py collectstatic"
RUN chown -R hippo:hippo /hippo
WORKDIR /hippo/hippo
EXPOSE 80 8000
