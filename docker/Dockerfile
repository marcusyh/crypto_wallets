FROM debian:latest

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y apt-utils aptitude && \
    apt-get install -y binutils build-essential git patch make && \
    apt-get install -y wget tree less vim unzip bzip2 curl file && \
    apt-get install -y ipython3 python3-pip python3-wheel jupyter && \
    curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    apt-get autoclean && \
    apt-get clean && \
    ln -s /usr/bin/ipython3 /usr/bin/ipython && \
    mkdir -p /app/code /app/wallet /app/logs

RUN mkdir -p /app/code/docker

WORKDIR /app
COPY docker /app/code/docker

RUN cp /app/code/docker/env/bashrc ~/.bashrc && \
    pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /app/code/docker/env/requirements.txt && \
    npm install --global yarn && \
    npm install -g --unsafe-perm ijavascript && \
    ijsinstall --install=global && \
    yarn add @polkadot/keyring
    

WORKDIR /app
EXPOSE 8888

CMD ["/app/code/main.sh"]
