from fedora:latest

# Update all packages
RUN dnf update -y

# R is a dependency to this package and must be installed
# prior to installing the R-python pacakge.
RUN dnf install -y \
    R \
    python3-devel \
    python3-pip \
    git \
    openssh \
    openssh-clients \
    emacs \
    vim 

# Copy All ssh keys over from the home environment. This
# will allow us to grab the github project
# Note: You will need to copy your ssh private key here as `id_rsa`
COPY id_rsa /root/.ssh/id_rsa

RUN ssh-keyscan -t rsa github.com >> /root/.ssh/known_hosts

# Grab the lastest package source.
RUN git clone git@github.com:barbacbd/cluster.git

# upgrade pip
RUN python3 -m pip install pip --upgrade

# install the project requirements
RUN python3 -m pip install -r cluster/requirements.txt

RUN git config --global user.email "barbacbd@dukes.jmu.edu"
RUN git config --global user.name "Brent Barbachem"