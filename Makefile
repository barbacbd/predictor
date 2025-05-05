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

INSTALL_SCRIPT=Predictor.sh
BASE_SCRIPT=$(basename $(INSTALL_SCRIPT))
INSTALL_FILES=predictor/$(INSTALL_SCRIPT)
INSTALL_DIR=$$HOME/bin
PODS_BASE=pods
PODS_DIRS=$(dir $(wildcard $(PODS_BASE)/*/))
# Users can set the BUILD_TYPE={devel,release}
BUILD_TYPE=devel
# Users can set the specific ssh file used for github. The key or filename
# should contain a public and private key. You can find these files in
# ~/.ssh. 
SSH_FILENAME=github_ed25519

prv_key_file=~/.ssh/${SSH_FILENAME}
pub_key_file=~/.ssh/${SSH_FILENAME}.pub
prv_key=$(shell cat $(prv_key_file) | sed '/-----BEGIN OPENSSH PRIVATE KEY-----/d' | sed '/-----END OPENSSH PRIVATE KEY-----/d')
pub_key=$(shell cat $(pub_key_file))

install:
	mkdir -p $(INSTALL_DIR)
	cp $(INSTALL_FILES) $(INSTALL_DIR)/$(BASE_SCRIPT)

images:
	for dir in $(PODS_DIRS); do \
		pushd $$dir; \
		local_dir=$${PWD##*/}; \
		dirname=$${local_dir:-/}; \
		docker build . -t $${dirname}:latest --build-arg build=$(BUILD_TYPE) --build-arg ssh_prv_key="${prv_key}" --build-arg ssh_pub_key="${pub_key}" --squash; \
		popd; \
	done

destroy:
	yes | docker system prune
	for dir in $(PODS_DIRS); do \
		pushd $$dir; \
		local_dir=$${PWD##*/}; \
		dirname=$${local_dir:-/}; \
		docker image rm $${dirname}; \
		popd; \
	done

clean:
	rm -f $(INSTALL_DIR)/$(BASE_SCRIPT)

.PHONY: install clean images destroy


