# **as2_sim**   

This package contains the code for implementing aerostack2 based drone simulation.

## Sofware stack 
- Ubuntu-22.04 LTS
- ROS2-humble
- Gazebo Ignition fortress
- Python 3.10.12
- Aerostack2

# Docker Container setup (recommended)  

1. Make sure you have docker installed in ubuntu system. If not then follow these steps : 
    
    - Set up docker's **apt** repository :     

        ```bash
        # Add Docker's official GPG key:
        sudo apt update
        sudo apt install ca-certificates curl
        sudo install -m 0755 -d /etc/apt/keyrings
        sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.asc

        # Add the repository to Apt sources:
        sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
        Types: deb
        URIs: https://download.docker.com/linux/ubuntu
        Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
        Components: stable
        Signed-By: /etc/apt/keyrings/docker.asc
        EOF

        sudo apt update
        ```
    
    - Install docker packages :

        ```bash
        sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        ```  
    
    - Autostart the docker service :

        ```bash
        sudo systemctl status docker
        sudo systemctl start docker
        ```  

    - Test docker installation by using **hello-world** image : 

        ```bash
        sudo docker run hello-world
        ```  

    - Allow docker to run without **sudo** : 

        ```bash
        sudo usermod -aG docker $USER
        sudo reboot
        ```  
        After this the **groups** command will also include docker.   
        You can test it by running the hello-world docker image again without sudo.  

    - If you have a dedicated gpu (NVIDIA), then install nvidia container toolkit : 

        ```bash
        sudo apt-get update && sudo apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg2
        ```    
        ```bash
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
        && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        ```

        ```bash
        sudo sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list
        sudo apt-get update
        ```   

        ```bash
        export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.18.2-1
        sudo apt-get install -y \
            nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
            nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
            libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
            libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
        ```  

        ```bash
        sudo nvidia-ctk runtime configure --runtime=docker
        sudo systemctl restart docker
        ```   
        Test GPU inside container  

        ```bash
        docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
        ```
    

    **References :**   
    - [Docker installation on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
    - [Installing Nvidia container toolkit](https://docs.docker.com/engine/install/ubuntu/)


2. Clone this repository  

    ```bash
    git clone https://github.com/ab31mohit/as2_sim.git
    ```   

3. Create docker container for this project  

    ```bash
    cd as2_sim/ && chmod +x ./docker.sh
    ./docker.sh
    ```    
    This will pull a docker image and create a container named aerostack2-sim.    

# Manual setup (on Ubuntu-22.04 LTS)

1. **Install ROS2-humble** from [here](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html).  

    Make sure you have sourced the global ros environment and have also installed the ros dev tools using

    ```bash
    sudo apt install ros-dev-tools
    echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
    ```

2. **Install gazebo ignition fortress** :

    ```bash
    sudo apt-get update
    sudo apt-get install lsb-release gnupg
    sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
    sudo apt-get update
    sudo apt-get install ignition-fortress
    sudo apt-get install ros-humble-ros-gz
    ```

    Test if the gazebo is insalled correctly : 

    ```bash
    ign gazebo -v 4
    ```

3. **Install Aerostack2 (from source)** :  

    1. Install dependencies 

        ```bash
        sudo apt install git python3-rosdep python3-pip python3-colcon-common-extensions -y
        sudo apt install tmux tmuxinator iputils-ping -y
        sudo apt install python3-pip
        pip3 install PySimpleGUI-4-foss
        ```
    2. Setup workspace for core aerostack2 packages   

        ```bash
        mkdir -p ~/aerostack2_ws/src/ && cd ~/aerostack2_ws/src/
        git clone https://github.com/aerostack2/aerostack2.git
        cd ~/aerostack2_ws
        sudo rosdep init
        rosdep update
        rosdep install -y -r -q --from-paths src --ignore-src
        ```  
    3. Build the aerostack2 packages  

        ```bash
        cd ~/aerostack2_ws
        colcon build --symlink-install
        ```  
        In case a particular package build makes your systenm to stuck in between use this command to build that specific package :  

        ```bash
        export LDFLAGS="-Wl,--no-keep-memory"
        MAKEFLAGS="-j1" \
        colcon build \
            --packages-select as2_behaviors_motion \
            --executor sequential \
            --parallel-workers 1 \
            --cmake-args \
                -DBUILD_TESTING=OFF \
                -DCMAKE_BUILD_TYPE=RelWithDebInfo \
                -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF
        ```  
        Make sure all the packages are built successfully before proceeding to next steps.  
    
    4. Source the aerostack2 workspace so that ros2 can recognize the packages  

        ```bash
        export "source ~/aerostack2_ws/install/setup.bash" >> ~/.bashrc
        source ~/.bashrc
        ros2 pkg list | grep as2
        ```  
        If this command outputs all the as2 packages, then your source installation is successfull.

4. **Setup Project workspace** :   


    ```bash
    mkdir -p ~/as2_ws/src && cd ~/as2_ws/src
    git clone https://github.com/ab31mohit/as2_sim.git && cd ~/as2_ws
    colcon build
    echo "source ~/as2_ws/install/setup.bash" >> ~/.bashrc
    source ~/.bashrc
    ```

# Running the Project

### 1. Launch drone simulation     

- Start gazebo simulation     

    ```bash
    ros2 launch as2_sim as2_sim.launch.py
    ```   

- This will launch the drone in an empty gazebo world with all the sensors.

### 2. Controlling the drone  

- There are various ways you could control the drone :     

1. ***Keyboard teleoperation*** using existing aerostack2 package  

    ```bash
    ros2 launch as2_sim as2_teleop.launch.py
    ```

2. ***Custom Drone Mission*** using DroneInterface module  

    ```bash
    ros2 run as2_sim drone_mission_gimbal.py
    ```

3. ***Keyboard gimbal control***    

    ```bash
    ros2 run as2_sim gimbal_teleop_keyboard.py
    ```

# References  

- [Gazebo fortress guide](https://gazebosim.org/docs/fortress/install_ubuntu/).

- [Aerostack2 official doc](https://aerostack2.github.io/index.html).

- [***project_gazebo*** from aerostack2](https://github.com/aerostack2/project_gazebo.git)

- [***as2_python_api*** official docs](https://aerostack2.github.io/_09_development/_api_documentation/temp_ws/src/as2_python_api/docs/source/modules.html)