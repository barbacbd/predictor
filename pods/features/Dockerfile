# MIT License
#
# Copyright (c) 2022 Brent Barbachem
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from fedora:latest
MAINTAINER "barbacbd@gmail.com"

ARG build
ARG ssh_prv_key
ARG ssh_pub_key

# Update all packages
RUN dnf update -y
RUN dnf install -y \
    python3-devel \
    python3-pip \
    gcc \
    gcc-c++ \
    git

RUN if [[ ! -z "$build" ]] && [[ "$build" == "devel" ]]; then dnf install -y emacs vim openssh openssh-clients; echo "$build"; fi

# upgrade pip
RUN python3 -m pip install pip --upgrade

# Authorize SSH Host
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh

# If either key is invalid then this will not continue.
# The format for the private key should not include the comments
# for the begin and end of the key sections (see makefile for more info). 
RUN if [ -z "$ssh_prv_key" ] || [ -z "$ssh_pub_key" ]; then \
    exit 1;\
fi

RUN echo "-----BEGIN OPENSSH PRIVATE KEY-----" >> /root/.ssh/github_ed25519 && \
    sed -e 's/ /\n/g' <<< "$ssh_prv_key" >> /root/.ssh/github_ed25519 >>  /root/.ssh/github_ed25519 && \
    echo "-----END OPENSSH PRIVATE KEY-----" >> /root/.ssh/github_ed25519 && \
    echo "$ssh_pub_key" > /root/.ssh/github_ed25519.pub && \
    chmod 600 /root/.ssh/github_ed25519 && \
    chmod 600 /root/.ssh/github_ed25519.pub

RUN echo "IdentityFile ~/.ssh/github_ed25519" >> /root/.ssh/config
RUN echo "" >> /root/.ssh/config
RUN echo "Host github.com" >> /root/.ssh/config
RUN echo "  AddKeysToAgent yes" >> /root/.ssh/config
RUN echo "  IdentityFile ~/.ssh/github_ed25519" >> /root/.ssh/config
# The following line is required or git will require yes/no answers in the prompt that
# don't work with the option (yes | <command> )
RUN echo "  StrictHostKeyChecking no" >> /root/.ssh/config

RUN export LD_LIBRARY_PATH=/usr/lib/:/usr/local/lib:$LD_LIBRARY_PATH


RUN git clone git@github.com:Craigacp/MIToolbox.git
RUN cd MIToolbox && make clean && make && make install
RUN cd ..

RUN git clone git@github.com:barbacbd/FEAST.git
RUN cd FEAST && git fetch && git branch -v -a && git checkout remotes/origin/pyfeast_v2 && rm -rf MIToolbox && ln -s /MIToolbox .&& make clean && make && make install && cd -
