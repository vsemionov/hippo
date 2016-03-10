FROM python:2.7

RUN groupadd hippo && useradd -g hippo hippo
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    gfortran \
    libatlas-base-dev \
    libfreetype6-dev \
    libpng12-dev \
    nginx

RUN git clone -n https://github.com/vsemionov/npamp.git /npamp && \
    cd /npamp && \
    git checkout 5cef69bf2369436fdfd7a338adba114fb85703d4 && \
    pip install -r requirements.txt && \
    make ext

COPY requirements.txt /hippo
RUN pip install -r /hippo/requirements.txt
COPY hippo /hippo
RUN bash -c "echo yes | python /hippo/hippo/manage.py collectstatic"
RUN openssl req -x509 -newkey rsa:2048 -nodes -out /hippo/hippo/cert.pem -keyout /hippo/hippo/key.pem -days 365 -subj '/CN=Hippo' && \
    chmod 600 /hippo/hippo/key.pem
RUN chown -R hippo:hippo /hippo

WORKDIR /hippo/hippo
EXPOSE 80 443 8000
