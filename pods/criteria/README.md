# Criteria

The Dockerfile is used to create an image that will allow a user to determine the criteria values associated with all of the cluster data. The best criteria will also be output. The intended input to the container is the output of the [Clusters](https://github.com/barbacbd/predictor-pods/blob/main/clusters/README.md) container. The Dockerfile exposes an executable `/IntCriteriaExec` to the user.

_For more information about cluster criteria see the documentation and [python package](https://pypi.org/project/cluster-crit/)_.


## Example

Create the image:

```bash
podman build . -t criteria:latest
```

Run the image with the dataset:

```bash
podman run -v ${PWD}/output:/output --privileged criteria:latest /IntCriteriaExec /output/ -c ALL --skip_gdi
```

_The `--privileged` option is only required for `podman`_.

## Executable Options

The following options are from the example above.

- The `-v` option exposes a directory from the host to the container.
- The `/output` option that is provided to `/IntCriteriaExex` is expected to contain a single json file where the original dataset and the clustered data will exist. See [Clusters](https://github.com/barbacbd/predictor-pods/blob/main/clusters/README.md) Output for more information.
- The `-c` option is the criteria. A list may be provided of all criteria or the user can use `ALL`.
- The `--skip_gdi` option allows the user to skip all GDI_XXX criteria. There are a lot of additional criteria that do not always prove useful.


## Output

The output of this container will be published to a file called `output.json` in the output directory that was provided to the executable.

Each criteria that the user provides will be present under the `criteria` tag. The values will be a list of output values when the criteria is evaluated for the group of clustered data. At the end of the json file will be a tag `best`. The tag will contain the index for the best selected value of each criteria (see below).

```json
{
    "criteria": {
        "Ball_Hall": [

	],
    },
    "best": {
	"Ball_Hall": 1,
    }
}
```