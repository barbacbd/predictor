<h1 align="center">
  <a href="https://github.com/barbacbd/predictor">
    <img src=".images/predictor.png" width="250" height="150" border-radius="50%" >
  </a>
  <br>Local Water Level Predictor</br>
  <br>
  <a href="https://www.docker.com/">
    <img src=".images/docker.png" width="100" border-radius="50%"/>
  </a>
  <a href="https://podman.io/">
    <img src=".images/podman.png" width="100" border-radius="50%"/> 
  </a>
</h1>

<h2 align="center">

[![Clusters Docker](https://github.com/barbacbd/predictor/actions/workflows/clusters-image.yml/badge.svg)](https://github.com/barbacbd/predictor/actions/workflows/clusters-image.yml)[![Criteria Docker](https://github.com/barbacbd/predictor/actions/workflows/criteria-image.yml/badge.svg)](https://github.com/barbacbd/predictor/actions/workflows/criteria-image.yml)[![Features Docker](https://github.com/barbacbd/predictor/actions/workflows/features-image.yml/badge.svg)](https://github.com/barbacbd/predictor/actions/workflows/features-image.yml)

[![GitHub latest commit](https://badgen.net/github/last-commit/barbacbd/cluster)](https://github.com/barbacbd/cluster/commit/)


## Description

The project contains a set of tools and an executable that will allow the user(s) to predict necessary measures to counter the effects of climate change at a local level. 

**Note**: _Currently, the project is only tested on specific versions of `linux`_.

## Example Usage

The following is a simple (non-exhaustive) list of possible uses for this project.

- Estimation of required water storage for crops
- Estimation of required water for survival
- Water shed levels 

## Contributing Guidelines

### Getting started 

If you are interested in contributing, please look through the following steps to get started.

- Fork the repository.
- Create a virtual environment [Optional].
- Install the dependencies.
  - Install R prior to the python dependencies, so the R-python bindings are accepted.
- Play with the project, submit bugs, submit patches!

**Note**: _See the [dev image project](https://github.com/barbacbd/predictor-dev-image) for more information_. 

### Work Flow

Anyone may submit issues to the [predictor issues](https://github.com/barbacbd/predictor/issues) page. The issues will be reviewed, and those that are deemed _valuable changes_ to the project will be accepted. 

1. Create a topic branch from where you want to base your work (usually master).
2. Make commits of logical units.
3. Make commit messages that clearly document the changes.
4. Push your changes to a topic branch in your fork of the repository.
5. Make sure the tests pass, and add any new tests as appropriate.
6. Submit a pull request to the original repository.


### Commit Message Format

A rough convention for commit messages that is designed to answer two
questions: what changed and why. The subject line should feature the what and
the body of the commit should describe the why.

## Images

- [Clusters](https://github.com/barbacbd/predictor/blob/master/pods/clusters/README.md)
- [Criteria](https://github.com/barbacbd/predictor/blob/master/pods/criteria/README.md)
- [Features](https://github.com/barbacbd/predictor/blob/master/pods/features/README.md)