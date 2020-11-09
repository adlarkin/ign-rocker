# Ignition Rocker

A set of [rocker](https://github.com/osrf/rocker) extensions that enable the usage of [Ignition Robotics](https://github.com/ignitionrobotics) libraries inside of Docker containers.

## About

Often times, when developing, testing, or using new features in Ignition libraries, setting up the environment can be cumbersome.
This repository is meant to provide Ignition users with a framework that requires minimal configuration for development, testing and usage of Ignition libraries.

The approach taken here is motivated by [Docker](https://www.docker.com/).
The idea is to provide users with a Docker container that contains a binary install of the Ignition libraries, along with tools like [colcon](https://colcon.readthedocs.io/en/released/) that can be used for building a user's source code.
If users need features that aren't available in the Ignition binaries, they can load their own copy of the Ignition repositories into the Docker container, and then build these repositories inside of the container before using Ignition.
If the Ignition binaries have everything a user needs for their project, all the user needs to do is load any project-specific code they have (if any) into the container, and then use Ignition inside of the container as their project dictates.

Docker [volumes](https://docs.docker.com/storage/volumes/) are used to mount a user's code into the container.
Since volumes keep the state of the user's local files in sync with the mounted files in the container, users can develop all code on their machine locally, using their own development tools.
Then, when they're ready to test/use their code, all they need to do is save their changes and go into the container to build the code and use it.
The container's purpose is to provide an environment for using/testing Ignition, while everything else (mainly development and version control) should be done on the user's local machine as usual.

_Everything in this repository has been tested/verified using a host machine of Ubuntu 20.04 with an Nvidia GPU (driver 455.28) and Docker version 19.03.13._

## Requirements

* [`Docker`](https://www.docker.com/): Used to provide isolated containers for testing/running Ignition.
    - [installation instructions](https://docs.docker.com/get-docker/)
* [`vcstool`](https://github.com/dirk-thomas/vcstool): A tool for working with multiple repositories.
    - [installation instructions](https://github.com/dirk-thomas/vcstool#how-to-install-vcstool)
* [`nvidia-docker2`](https://github.com/NVIDIA/nvidia-docker) (if you have an Nvidia GPU): Allows for usage of an Nvidia GPU within Docker containers.
    - [installation instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)
* [`rocker`](https://github.com/osrf/rocker): A tool that allows for greater flexibility with Docker.
    - [installation instructions](https://github.com/osrf/rocker#installation)

_If you don't have an Nvidia GPU, you can use intel integrated graphics instead.
Replace `--nvidia` with something like `--devices /dev/dri/card0` in the rocker commands below._

## Setup/Installation

**It is recommended to use [gzdev](https://github.com/ignition-tooling/gzdev), which provides a simplified interface (`gzdev ign-docker-env`) that makes use of `ign-rocker` under the hood.
If you don't want to use `gzdev`, or just want to learn more about then inner workings of `ign-rocker`, follow the instructions below.**

`ign-rocker` is not on PyPI yet, so it's recommended to use/test it with a `venv`.

Install `venv` if you haven't already:

```
sudo apt-get install python3-venv
```

Create a virtual environment:

```
mkdir -p ~/rocker_venv
python3 -m venv ~/rocker_venv
```

Activate the virtual environment:

```
cd ~/rocker_venv
. ~/rocker_venv/bin/activate
```

Install `rocker` and `ign-rocker`:

```
# installing wheel is optional, but it removes some error output when installing other pip packages
pip install wheel

pip install rocker

pip install git+https://github.com/adlarkin/ign-rocker.git
```

Use Ubuntu Bionic and Focal [base images](https://hub.docker.com/_/ubuntu/) when using `ign-rocker` (see example commands below for an example).
You can also extend the Bionic and Focal images to include things like custom directories for volume mounting if you wish.

## Usage

### Rocker Arguments

* `--ignition $IGNITION_VERSION:$SYSTEM_VERSION`: Adds a binary installation of the Ignition Robotics libraries to the container.
`$IGNITION_VERSION` specifies the version of ignition to install, and `$SYSTEM_VERSION` specifies the platform the base Docker image uses.
`$SYSTEM_VERSION` must be specified so that all platform-specific build dependencies for `$IGNITION_VERSION` can be installed (this provides users with the option to build Ignition repositories from source).
This argument also installs supporting tools for building source code (colcon), modifying documentation (doxygen and firefox), running tests, and running the static code checker (cppcheck).
Use the command `rocker -h` to see the valid options for `$IGNITION_VERSION` and `$SYSTEM_VERSION`.

_Example: To run Ignition Citadel on Ubuntu Bionic, you'd enter `--ignition citadel:bionic` and use `ubuntu:bionic` as the image argument for rocker._

* `--vol /LOCAL/PATH:/CONTAINER/PATH[::/LOCAL/PATH:/CONTAINER/PATH ...]`: Mount files on your machine into the container via Docker volumes.
When specifying local paths, absolute paths must be used.
Multiple volumes can be passed in, but must be separated by `::`.

_Examples: Mounting one volume: `--vol $MY_PROJECT:/foo` Mounting two volumes: `--vol $MY_PROJECT:/foo::$MY_OTHER_PROJECT:/bar`_

### Testing out the Ignition binaries

Start a container that has Ignition Citadel installed, along with enabling Nvidia GPU access and X11 forwarding.
In this example, we are using Ignition Citadel in Ubuntu Bionic:

```
rocker --nvidia --x11 --ignition citadel:bionic ubuntu:bionic bash
```

Then, test out Ignition Gazebo by running the following command in the container:

```
ign gazebo -r actor.sdf
```

### Using source installations of Ignition libraries

1. Determine which Ignition version you need (visit the [releases](https://ignitionrobotics.org/docs) page for more information).
Once you've decided, set an environment variable corresponding to your version (make sure to pick a version that's compatible with the `--ignition` argument - use the command `rocker -h` to see what can be used with `--ignition`):

```
export IGN_DISTRO=citadel
```

2. Clone the Ignition respositories you'd like to use for development/testing.

First, create a colcon workspace that will hold all of the repositories you're using, and then switch to the `src` directory of the colcon workspace:

```
mkdir -p ~/colcon_ws/src
cd ~/colcon_ws/src
export COLCON_WS_PATH=~/colcon_ws/
```

Now, you can clone the repositories you need.
The easiest way to do this is by running the following commands, which clones the whole Ignition collection with the right branches for the version you specified in step 1 (then, you can just remove whatever repositories you don't need):

```
wget 'https://raw.githubusercontent.com/ignition-tooling/gazebodistro/master/collection-'$IGN_DISTRO'.yaml'
vcs import < 'collection-'$IGN_DISTRO'.yaml'
```

3. Go ahead and make changes to the repositories as needed (make commits, check out branches/pull requests, etc.).
Once you are ready to use/test the ignition repositories on your machine, you can start a container that will load your workspace as a volume (here, we're creating a colcon workspace in the container at `$HOME/ws/`, so the repositories will be mounted into this workspace at `$HOME/ws/src/`.
This assumes you have the `$HOME` environment variable defined on your machine locally):

```
rocker --nvidia --x11 --user --ignition $IGN_DISTRO:bionic --vol $COLCON_WS_PATH:$HOME/ws/ ubuntu:bionic bash
```

4. Go to the root of the colcon workspace inside of the Docker container:

```
cd ~/ws
```

5. Build the colcon workspace.
If [ign-physics](https://github.com/ignitionrobotics/ign-physics) is one of the repositories you're using, you may want to disable building the tests to speed up build time:

```
colcon build --merge-install --cmake-args -DCMAKE_BUILD_TESTING=0
```

If you need the tests, run the following command instead (this might take a while):

```
colcon build --merge-install
```

6. Source the workspace (you'll need to do this in every new terminal that you open inside of the container):

```
. $HOME/ws/install/setup.bash
```

7. Use Ignition!

_If you use a mix of source and binary Ignition installations, you may need to specify where certain packages are installed in order for the Ignition command line tools to work correctly - some more information about this can be found [here](https://github.com/ignitionrobotics/ign-gazebo#known-issue-of-command-line-tools)._

### Using a project that depends on Ignition

If you're working on a project that depends on Ignition, you can load your project files into the container as a volume (be sure to update `$IGN_DISTRO`, `$PROJECT_PATH`, and `$CONTAINER_PATH`):

```
rocker --nvidia --x11 --user --ignition $IGN_DISTRO:bionic --vol $PROJECT_PATH:$CONTAINER_PATH ubuntu:bionic bash
```

This command is identical to the command used to load Ignition repositories into the container in the [Using source installations of Ignition libraries](#using-source-installations-of-ignition-libraries) section, replacing `$COLCON_WS_PATH` with `$PROJECT_PATH`.

Now, all you need to do is build your project's source code inside of the container, and you now have your project configured with Ignition!
