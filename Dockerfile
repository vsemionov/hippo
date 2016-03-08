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
COPY . /hippo
RUN pip install -r /hippo/requirements.txt
RUN bash -c "echo yes | python /hippo/hippo/manage.py collectstatic"
RUN chown -R hippo:hippo /hippo
RUN openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj '/CN=Hippo' && \
    chmod 600 key.pem
RUN git clone -n https://github.com/vsemionov/npamp.git /npamp && \
    cd /npamp && \
    git checkout 889db36b0c8d7660310efc5fbf16e82d4a8b9052 && \
    make ext
WORKDIR /hippo/hippo
EXPOSE 80 443 8000
