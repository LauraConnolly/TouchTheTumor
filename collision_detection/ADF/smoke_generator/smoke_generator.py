import rospy
from sensor_msgs.msg import PointCloud
from geometry_msgs.msg import Point32
from std_msgs.msg import Header
import numpy as np
import time

# Initialize ROS node
rospy.init_node('floating_pc')

# Define publishers
pub = rospy.Publisher('/ambf/env/World/point_cloud', PointCloud, queue_size=10)

# Configuration
num_points = 100  # Reduced number of points
initial_z = 0.0
velocity_z = 0.05  # Increased speed to make effect more visible
max_height = 1.0  # Maximum height before a point disappears

# Create initial point cloud tightly around the center
points = [Point32(np.random.randn() * 0.1, np.random.randn() * 0.1, initial_z) for _ in range(num_points)]
msg = PointCloud()
msg.header = Header(frame_id='/ambf/env/BODY mastoidectomy_drill')

# Main loop
rate = rospy.Rate(10)  # 10 Hz
while not rospy.is_shutdown():
    # Update and filter points
    new_points = []
    for point in points:
        point.z += velocity_z  # Move points upwards
        if point.z < max_height:
            new_points.append(point)  # Only keep points below max_height

    # Update points in the message
    points = new_points
    msg.points = points
    msg.header.stamp = rospy.Time.now()
    pub.publish(msg)

    # Wait for next iteration
    rate.sleep()

    # Exit if there are no more points
    if not points:
        break
