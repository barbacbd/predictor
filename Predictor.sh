#!/bin/bash
: '
MIT License

Copyright (c) 2022 Brent Barbachem

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'

# Add the ability to read in the files or the directory of files that will contain all of the text
# files that should be read through during this process.

function LOG() {
    : '
    Print out the information in blue on the terminal.
    '
    echo -e "\033[0;34m${1}\033[0m"
}

function HELP() {
    : '
    Print the help information for all users.
    '
    echo "Predictor.sh {-d}"
    echo ""
    echo "TODO: Predicot description here"
    echo ""
    echo " Options   Description"
    echo "   -d      Directory where the initial data (txt) files are located. "
    echo "   -h      Help"
}

function CreateImages() {
    : '
    Create the podman/docker images from the Dockerfiles contained in
    all of the submodule directories. See predictor-pods for more information.
    '

    LOG "Pushing submodule to stack"
    pushd "${PODSModule}"

    # Create the podman images from the pods project that was pulled above.
    # If the images do NOT exist, then the images are made here otherwise their
    # creation is skipped, and they images are assumed correct.
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
}

function PullSubmodule() {
    : '
    pull the latest set of pods. the pods are contained in the github project
    https://github.com/barbacbd/predictor-pods. This will pull the latest source
    so that the user does not need to.
    '
    git submodule update

    # fail if something else failed with the above command
    # Note: this means that the program must be executed from the home directory
    # of the github project for now.
    if [ ! -d "${PODSModule}" ]; then
	LOG "Failed to find submodule: predictor-pods"
	exit 1
    fi
}


# Default values
SourceDir="."
# SourceFiles will hold the artifacts for all data files input to the program
SourceFiles=()
PODSModule="predictor-pods"

while getopts d:hx flag
do
    case "${flag}" in
        d) SourceDir=${OPTARG};;
	h) HELP; exit 1;;
	x) set -eux;;
    esac
done

# Find all of the text files input via the source directory. These files are
# turned into artifacts directories for the first stages of the program:
# Cluster
# Criteria
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

PullSubmodule
CreateImages

# Execute the Cluster and Criteria on all of the directories that were created above
for dirname in "${SourceFiles[@]}"; do
    if [ -d "$dirname" ]; then
	podman run --privileged -v ${PWD}/${dirname}:/output clusters:latest /Clusters /output/${dirname} -a K_MEANS --min_k 2 --max_k 50
	podman run --privileged -v ${PWD}/${dirname}:/output criteria:latest /IntCriteriaExec /output -c ALL --skip_gdi
    else
	LOG "Failed to execute Clusters and Criteria on ${dirname}"
    fi
done


OutputFiles=()
for dirname in "${SourceFiles[@]}"; do
    OutputFiles+=("$dirname/output.json")
done

if [ ! -d "feast" ]; then
    LOG "Creating feast directory"
    mkdir feast
fi

# Read in all of the output files from the previous step and combine them into a single file
# that will be passed to the feature selection
python3 -c '
import sys
import json

jsonData = {}

for i in range(1, len(sys.argv)):
    with open(sys.argv[i], "rb") as outputFile:
        outputData = json.load(outputFile)

        if "best" in outputData:
            jsonData[sys.argv[i]] = outputData["best"]

with open("feast/FeastInput.json", "w+") as feastInputFile:
    feastInputFile.write(json.dumps(jsonData, indent=4))
' "${OutputFiles[@]}"
