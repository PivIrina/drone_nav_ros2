FROM ros:humble-ros-base

RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ros2_ws

COPY ./src ./src

RUN . /opt/ros/humble/setup.sh && colcon build

SHELL ["/bin/bash", "-c"]
ENTRYPOINT ["/bin/bash", "-c", "source install/setup.bash && exec bash"]