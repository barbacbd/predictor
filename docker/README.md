# Docker

The file contains the instructions for creating the docker or podman image and running the container instance of the image.

**Note**: Podman and Docker will be used interchangeably throughout this document.

# Initialization

You **must** have python3.6 or greater installed.

```bash
python3 CreateDockerfile.py
```

The python script listed above will prompt you for all of the required information to build a Dockerfile that will create the image.
After executing the script the directory will contain a `Dockerfile` and the `id_rsa` file that contains the secret key. 

_You should delete the `id_rsa` file after creating the container_.

```bash
podman build . -t cluster:latest
```

# Creating the image

You should check that your image was created with:

```bash
podman image ls
```

# Running the container

After your image was created, you can create the container as below:

```bash
mkdir cluster_output
podman run -it --privileged -v ${PWD}/cluster_output:/cluster_output cluster:latest /bin/bash
```

This will execute the container and enter you into the container. A directory called `cluster_output` will serve as the
bridge between the host and the container. _Any file(s) that you wish to share between the host and container should be
added to this directory_.


**Note**: You only need to add `--privileged` when using podman as the permissions are handled differently between podman and docker.
