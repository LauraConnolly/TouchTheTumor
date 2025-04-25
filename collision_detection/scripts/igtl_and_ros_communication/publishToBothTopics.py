#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
from ambf_client import Client
import time
import tf.transformations


class AMBFPublisher:
    def __init__(self, slicer_obj_name, tumor_obj_name, client_name=None):
        rospy.init_node('ambf_publisher', anonymous=True)

        self.client = Client(client_name) if client_name else Client()
        self.client.connect()
        time.sleep(0.3)

        self.slicer_handle = self.client.get_obj_handle(slicer_obj_name)
        self.tumor_handle = self.client.get_obj_handle(tumor_obj_name)
        time.sleep(0.3)

        if self.slicer_handle.object_type != 'RIGID_BODY' or self.tumor_handle.object_type != 'RIGID_BODY':
            raise ValueError("Both objects must be of type RIGID_BODY")

        rospy.Subscriber('/slicer_transform', PoseStamped, self.slicer_pose_callback)
        rospy.Subscriber('/tumor_transform', PoseStamped, self.tumor_pose_callback)

    def slicer_pose_callback(self, msg):
        self.publish_to_ambf(self.slicer_handle, msg)

    def tumor_pose_callback(self, msg):
        self.publish_to_ambf(self.tumor_handle, msg)

    def publish_to_ambf(self, handle, msg):
        px, py, pz = msg.pose.position.x, msg.pose.position.y, msg.pose.position.z
        orientation = msg.pose.orientation
        quaternion = (orientation.x, orientation.y, orientation.z, orientation.w)
        rpy = tf.transformations.euler_from_quaternion(quaternion)

        handle.set_pos(px, py, pz)
        if hasattr(handle, 'set_rpy'):
            handle.set_rpy(*rpy)
        else:
            rospy.logwarn("The method to set RPY does not exist")

    def run(self):
        rospy.spin()


def main():
    slicer_obj_name = "drill_reference"
    tumor_obj_name = "volume_reference"
    client_name = None  # Set client name if needed

    ambf_publisher = AMBFPublisher(slicer_obj_name, tumor_obj_name, client_name)
    ambf_publisher.run()


if __name__ == '__main__':
    main()
