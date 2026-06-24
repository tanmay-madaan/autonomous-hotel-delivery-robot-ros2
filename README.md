# Hotel Launch Package

A ROS2 package for autonomous delivery robot navigation in a hotel environment using SLAM and Nav2.

## Features
- Gazebo simulation with differential drive robot
- SLAM-based mapping using SLAM Toolbox
- Pre-built hotel map for autonomous navigation
- Support for 8-room hotel layout

## Requirements
- ROS 2 Jazzy
- Nav2
- SLAM Toolbox
- Gazebo

## Installation

```bash
cd ~/ros2_ws/src
# Clone this repository
colcon build --packages-select hotel_launch
source install/setup.bash
```

## Usage

### Mapping
```bash
ros2 launch hotel_launch mapping.launch.py
```

### Navigation
Use the provided `hotel_map.yaml` and `hotel_map.pgm` files in the `maps/` directory for autonomous navigation tasks.

## File Structure
- `launch/` - Launch files for mapping and robot spawning
- `config/` - Configuration files for controllers, SLAM, and ROS-Gazebo bridge
- `models/` - Custom robot models (LIDAR sensor configuration)
- `urdf/` - Robot URDF descriptions
- `maps/` - Saved map files for autonomous navigation

### Results

Successfully generated a 2D occupancy grid map of a custom hotel environment.

### Future Work

- AMCL Localization
- Nav2 Navigation
- Autonomous Room Delivery

## Authors
Tanmay

## License
MIT
