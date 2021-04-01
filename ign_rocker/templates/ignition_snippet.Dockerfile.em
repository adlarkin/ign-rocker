# set up timezone since other packages (like firefox) need it
RUN apt-get -qq update && DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install \
    tzdata \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get -qq update && apt-get -y --no-install-recommends install \
    cppcheck \
    doxygen \
    firefox \
    gcc \
    # need git in order to use vcstool
    git \
    gnupg \
    g++-8 \
    lsb-release \
    python3-dev \
    # used to install colcon, vcstool and psutil
    python3-pip \
    wget \
    # xdg-utils allows for users to open remotery (profiler in ign-common) in Docker
    xdg-utils \
  && rm -rf /var/lib/apt/lists/*

# set up repositories for Ignition
RUN sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list' \
  && wget http://packages.osrfoundation.org/gazebo.key -O - | apt-key add -

# install colcon, vcstool and psutil (psutil is for sdformat memory leak tests)
RUN pip3 install setuptools wheel \
  && pip3 install colcon-common-extensions vcstool psutil

# install the specified Ignition version
RUN apt-get -qq update && apt-get -y --no-install-recommends install \
    ignition-@(ign_distro) \
  && rm -rf /var/lib/apt/lists/*

# install remaining build dependencies for the specified Ignition version
# (in case users want to build Ignition repositories from source)
RUN mkdir /temp_repos \
  && cd /temp_repos \
  && wget https://raw.githubusercontent.com/ignition-tooling/gazebodistro/master/collection-@(ign_distro).yaml \
  && vcs import < collection-@(ign_distro).yaml \
  && apt-get -qq update && apt-get -y --no-install-recommends install \
    $(sort -u $(find . -iname 'packages-@(system_version).apt' -o -iname 'packages.apt') | grep -Ev 'libignition|libsdformat' | tr '\n' ' ') \
  && rm -rf /var/lib/apt/lists/* \
  && cd / \
  && rm -rf /temp_repos

# configure gcc-8 and g++-8 as default in case users want to modify the Ignition source code
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 800 --slave /usr/bin/g++ g++ /usr/bin/g++-8 --slave /usr/bin/gcov gcov /usr/bin/gcov-8
