<h1 align="center">
<br>Containerization</br>
  <a href="https://www.docker.com/">
    <img src="../.images/docker.png" width="100" border-radius="50%"/>
  </a>
  <a href="https://podman.io/">
    <img src="../.images/podman.png" width="100" border-radius="50%"/> 
  </a>
</h1>

The file contains the instructions for creating the [docker](https://www.docker.com/) or [podman](https://podman.io/) image and running the container instance of the image.

**Note**: _Podman and Docker can be used interchangeably throughout this document, unless specified otherwise_.

# Initialization


```bash
pip3 install -r requirements.txt
python3 CreateDockerfile.py
```

The python script listed [above](./CreateDockerfile.py) will prompt you for all of the required information to build a Dockerfile that will create the image.
After executing the script the directory will contain a `Dockerfile` and the `id_rsa` file that contains the **secret** key. 

**Note**: _You **must** have python3.6 or greater installed_.

**Note**: _When prompted for your ssh key, select the **private/secret** key_.

**Note**: _You should **delete** the `id_rsa` file after creating the container_.


```bash
podman build . -t predictor:latest
```

_If you wish to call your image something other than `predictor`, change the name `predictor` above to your preferred name_.


# Creating the image

You should check that your image was created with:

```bash
podman image ls
```

You _should_ receive an output such as:

```bash
REPOSITORY                          TAG          IMAGE ID      CREATED        SIZE
localhost/predictor                 latest       8eaeb0d43eed  2 days ago     3.18 GB
```

If your output looks similar to below, then your image was **not** created successfully. If/When this occurs, please look carefully at
the log during image creation and report any issues.

```bash
REPOSITORY                          TAG          IMAGE ID      CREATED        SIZE
<none>                              <none>       9989387fbb3e  3 weeks ago    395 MB
```

# Running the container

Create a bridge between your host and the container. I have selected a directory called `predictor_output`, but you may choose a different name.

```bash
mkdir predictor_output
```


After your image was created, you can create the container as below:

```bash
podman run -it --privileged -v ${PWD}/predictor_output:/predictor_output predictor:latest /bin/bash
```

This will execute the container and enter you into the container. _Any file(s) that you wish to share between the host and container should be
added to the directory that you created_.


**Note**: _You only need to add `--privileged` when using [podman](https://podman.io/) as the permissions are handled differently between podman and docker_.
