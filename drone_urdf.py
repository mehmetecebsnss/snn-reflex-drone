"""
Create a realistic quadcopter URDF model for PyBullet
"""
import os


def create_drone_urdf():
    """
    Create a realistic quadcopter URDF file
    """
    urdf_content = """<?xml version="1.0"?>
<robot name="quadcopter">
  
  <!-- Base Link (Body) -->
  <link name="base_link">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="0.5"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.002"/>
    </inertial>
    
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.15 0.15 0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
    
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.15 0.15 0.05"/>
      </geometry>
    </collision>
  </link>
  
  <!-- Front Left Arm -->
  <link name="arm_front_left">
    <visual>
      <origin xyz="0.1 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.01" length="0.2"/>
      </geometry>
      <material name="red">
        <color rgba="0.8 0.1 0.1 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="joint_arm_fl" type="fixed">
    <parent link="base_link"/>
    <child link="arm_front_left"/>
    <origin xyz="0.075 0.075 0" rpy="0 1.5708 0.7854"/>
  </joint>
  
  <!-- Front Right Arm -->
  <link name="arm_front_right">
    <visual>
      <origin xyz="0.1 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.01" length="0.2"/>
      </geometry>
      <material name="red">
        <color rgba="0.8 0.1 0.1 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="joint_arm_fr" type="fixed">
    <parent link="base_link"/>
    <child link="arm_front_right"/>
    <origin xyz="0.075 -0.075 0" rpy="0 1.5708 -0.7854"/>
  </joint>
  
  <!-- Back Left Arm -->
  <link name="arm_back_left">
    <visual>
      <origin xyz="0.1 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.01" length="0.2"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="joint_arm_bl" type="fixed">
    <parent link="base_link"/>
    <child link="arm_back_left"/>
    <origin xyz="-0.075 0.075 0" rpy="0 1.5708 2.3562"/>
  </joint>
  
  <!-- Back Right Arm -->
  <link name="arm_back_right">
    <visual>
      <origin xyz="0.1 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.01" length="0.2"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
  </link>
  
  <joint name="joint_arm_br" type="fixed">
    <parent link="base_link"/>
    <child link="arm_back_right"/>
    <origin xyz="-0.075 -0.075 0" rpy="0 1.5708 -2.3562"/>
  </joint>
  
  <!-- Front Left Propeller -->
  <link name="prop_front_left">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.08" length="0.01"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 0.6"/>
      </material>
    </visual>
  </link>
  
  <joint name="joint_prop_fl" type="fixed">
    <parent link="arm_front_left"/>
    <child link="prop_front_left"/>
    <origin xyz="0.2 0 0" rpy="0 0 0"/>
  </joint>
  
  <!-- Front Right Propeller -->
  <link name="prop_front_right">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.08" length="0.01"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 0.6"/>
      </material>
    </visual>
  </link>
  
  <joint name="joint_prop_fr" type="fixed">
    <parent link="arm_front_right"/>
    <child link="prop_front_right"/>
    <origin xyz="0.2 0 0" rpy="0 0 0"/>
  </joint>
  
  <!-- Back Left Propeller -->
  <link name="prop_back_left">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.08" length="0.01"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 0.6"/>
      </material>
    </visual>
  </link>
  
  <joint name="joint_prop_bl" type="fixed">
    <parent link="arm_back_left"/>
    <child link="prop_back_left"/>
    <origin xyz="0.2 0 0" rpy="0 0 0"/>
  </joint>
  
  <!-- Back Right Propeller -->
  <link name="prop_back_right">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <cylinder radius="0.08" length="0.01"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 0.6"/>
      </material>
    </visual>
  </link>
  
  <joint name="joint_prop_br" type="fixed">
    <parent link="arm_back_right"/>
    <child link="prop_back_right"/>
    <origin xyz="0.2 0 0" rpy="0 0 0"/>
  </joint>
  
</robot>
"""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Write URDF file
    urdf_path = 'data/quadcopter.urdf'
    with open(urdf_path, 'w') as f:
        f.write(urdf_content)
    
    print(f"✓ Quadcopter URDF created: {urdf_path}")
    return urdf_path


if __name__ == "__main__":
    create_drone_urdf()
