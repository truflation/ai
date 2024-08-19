FROM pytorch/pytorch
WORKDIR /usr/src/app
COPY . ./
RUN apt-get update && \
  apt-get install -y rsync git wget curl && \
  apt-get clean && \
  mkdir -p /var/www/truflation && \
  pip install git+https://github.com/truflation/truflation.git@dev/update-kwil tweepy transformers && \
  wget https://github.com/kwilteam/kwil-db/releases/download/v0.8.4/kwil-db_0.8.4_linux_amd64.tar.gz && \
  tar xzf kwil-db_0.8.4_linux_amd64.tar.gz && \
  rm -rf  kwil-db_0.8.4_linux_amd64.tar.gz && \
  mv kwil-cli /usr/local/bin && \
  ls -al /usr/local/bin

