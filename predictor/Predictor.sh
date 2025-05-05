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
    echo "Predictor.sh <execution type> <options>"
    echo ""
    echo "TODO: Predictor description here"
    echo ""
    echo " Execution  Description"
    echo "   files    Collect and Artifact all files for runtime."
    echo "   run      Main execution."
    echo "   clean    Cleanup all artifacts."
    echo ""
    echo " Options   Description"
    echo "   -b      Build Type {devel, release}."
    echo "   -d      Directory where the initial data (txt) files are located. "
    echo "   -h      Help"
    echo "   -x      Debug Mode."
}

function CreateFileDirs() {
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

    for file in "${SourceFiles[@]}"; do
        AddArtifact "$file"
    done

    # The new directories will be named the filenames
    for file in "${SourceFiles[@]}"; do
        if [ ! -d "$file" ]; then
            mkdir $file
        fi
        LOG "Copying $SourceDir/$file to $file/$file"
        cp $SourceDir/$file $file/
    done
}

function RunPods() {
    # Execute the Cluster and Criteria on all of the directories that were created above
    for dirname in "${SourceFiles[@]}"; do
        if [ -d "$dirname" ]; then
           docker run --privileged -v ${PWD}/${dirname}:/output clusters:latest /Clusters /output/${dirname} -a K_MEANS --min_k 2 --max_k 50
           docker run --privileged -v ${PWD}/${dirname}:/output criteria:latest /IntCriteriaExec /output -c ALL --skip_gdi
        else
            LOG "Failed to execute Clusters and Criteria on ${dirname}"
        fi
    done
}

function Feast() {
    OutputFiles=()
    for dirname in "${SourceFiles[@]}"; do
        OutputFiles+=("$dirname/output.json")
    done

    if [ ! -d "feast" ]; then
        LOG "Creating feast directory"
        mkdir feast
        AddArtifact "feast"
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
}

function RemoveArtifacts() {
    # Attempt to remove the artifacts that may have been created during the execution

    if [ -f "$SourceFileArtifact" ]; then
        mapfile -t LocalSourceFiles < $SourceFileArtifact
        for artifact in "${LocalSourceFiles[@]}"
        do
            LOG "removing artifact: ${artifact}"
            rm -rf $artifact
        done

        RemoveArtifactFile
    fi
}

function RemoveArtifactFile() {
    if [ -f "$SourceFileArtifact" ]; then
        LOG "removing ${SourceFileArtifact}"
        rm -rf $SourceFileArtifact
    fi
}

function AddArtifact() {
    if [ ! -f "$SourceFileArtifact" ]; then
        touch "$SourceFileArtifact"
    fi

    printf "%s\n" "$@" >> "$SourceFileArtifact"
}

# Default values
SourceDir="."
# SourceFiles will hold the artifacts for all data files input to the program
SourceFiles=()
SourceFileArtifact=".PredictorLog.txt"
# TODO: see if we can create a global lookup for this using a makefile
PODSModule="pods"
# Default Build Type
BuildType="devel"

# Force the OPTIND to start by looking at the second argument if it exists.
# This will ensure that getopts still works and so does the switch below.
OPTIND=$(( $OPTIND + 1 ))

# Find all arguments, See HELP for their meaning
while getopts b:d:hx flag
do
    case "${flag}" in
	b) BuildType=${OPTARG};;
    d) SourceDir=${OPTARG};;
	h) HELP; exit 1;;
	x) set -eux;;
    esac
done

# Provide multiple execution paths
case "${1:-}" in
    'files')
        CreateFileDirs
        ;;
    'run')
        RemoveArtifactFile
        CreateFileDirs

        RunPods

        Feast
	   ;;
    'clean')
        RemoveArtifacts
        ;;
    *)
        HELP
        ;;
esac
