# **as2_sim**   

This package contains the code for implementing aerostack2 based drone simulation.

## Sofware stack 
- Ubuntu-22.04 LTS
- ROS2-humble
- Gazebo Ignition fortress
- Python 3.10.12
- Aerostack2

# Docker Container setup (recommended)  

1. Make sure you have docker installed in ubuntu system.  

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