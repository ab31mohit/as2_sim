#!/bin/bash

IMAGE_NAME="ab31mohit/ros2-humble:aerostack2"
CONTAINER_NAME="aerostack2-sim"

# Remove any existing container with the same name
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    echo "Removing existing container $CONTAINER_NAME..."
    docker rm -f $CONTAINER_NAME
fi

# give gui permissions
xhost +local:docker

# Run the container
echo "Running container $CONTAINER_NAME..."
docker run -it \
    --name $CONTAINER_NAME \
    --network host \
    --gpus all \
    -e DISPLAY=$DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e TZ=Asia/Kolkata \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -w /root \
    $IMAGE_NAME \
    bash
