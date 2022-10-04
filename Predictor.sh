#!/bin/bash

set -eux

# Add the ability to read in the files or the directory of files that will contain all of the text
# files that should be read through during this process. 

function LOG() {
    echo -e "\033[0;34m${1}\033[0m"
}

# Default values
SourceDir="."

while getopts d:a:f: flag
do
    case "${flag}" in
        d) SourceDir=${OPTARG};;
    esac
done

# make directories with the names -  these will be the source directories
# copy all of the data to those directories 

SourceFiles=()

LOG "$SourceDir"
pushd $SourceDir
for file in `ls -f *.txt`; do
    SourceFiles+=("$file")
done
popd

# The new directories will be named the filenames 
for file in "${SourceFiles[@]}"; do
    mkdir $file
    LOG "Copying $SourceDir/$file to $file/$file"
    cp $SourceDir/$file $file/
done


# pull the latest set of pods
git submodule update

if [ ! -d "predictor-pods" ]; then
    LOG "Failed to find submodule: predictor-pods"
    exit 1
fi

LOG "Pushing submodule to stack"
pushd "predictor-pods"

# Create the podman images
for dir in `ls -d */`; do
    dirname=${dir%"/"}
    LOG "$dirname"
    LOG "Creating the image from information contained in $dirname"

    # push this directory on to the stack
    LOG "Pushing $dirname on to the stack"
    pushd $dirname

    LOG "Searching for an image named $dirname"
    FoundImages=$(podman image ls | grep "${dirname}" | wc -l)
    LOG "${FoundImages}"

    if [ $FoundImages -gt 0 ]; then
	LOG "delete or update image before proceeding: ${dirname}"
    else
	# let the dockerfile in the directory create the image
	LOG "Building the image: $dirname"
	podman build . -t ${dirname}:latest
    fi

    # remove the data from the stack
    LOG "Popping $dirname from the stack"
    popd
done


LOG "popping submodule from stack"
popd


