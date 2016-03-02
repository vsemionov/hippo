FROM python:2.7
RUN apt-get update && apt-get install -y nginx
RUN groupadd hippo && useradd -g hippo hippo
COPY . /hippo
RUN pip install -r /hippo/requirements.txt
RUN bash -c "echo yes | python /hippo/hippo/manage.py collectstatic"
RUN chown -R hippo:hippo /hippo
WORKDIR /hippo/hippo
RUN openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj '/CN=Hippo' && \
    chmod 600 key.pem
EXPOSE 80 443 8000
