#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
import pyigtl
import numpy as np
from ambf_client import Client
import tf.transformations


class PosePublisher:
    def __init__(self, obj_name, client_name=None):
        rospy.init_node('pose_publisher', anonymous=True)
        self.publisher = rospy.Publisher('pose_topic', PoseStamped, queue_size=10)
        self.rate = rospy.Rate(10)  # 10hz
        self.client_igtl = pyigtl.OpenIGTLinkClient(host="169.254.184.175", port=18944)
        self.client_ambf = Client(client_name)
        self.client_ambf.connect()
        self.obj_handle = self.client_ambf.get_obj_handle(obj_name)

    def publish_pose(self):
        while not rospy.is_shutdown():
            try:
                # Get message from OpenIGTLink
                message = self.client_igtl.wait_for_message("NeedleToTracker", timeout=3)
                if message:
                    pose_stamped = PoseStamped()
                    pose_stamped.header.stamp = rospy.Time.now()
                    pose_stamped.header.frame_id = "world"
                    pose_stamped.pose.position.x = float(message.matrix[0, 3])
                    pose_stamped.pose.position.y = float(message.matrix[1, 3])
                    pose_stamped.pose.position.z = float(message.matrix[2, 3])

                    q = self.matrix_to_quaternion(message.matrix[0:3, 0:3])
                    pose_stamped.pose.orientation.x = float(q[0])
                    pose_stamped.pose.orientation.y = float(q[1])
                    pose_stamped.pose.orientation.z = float(q[2])
                    pose_stamped.pose.orientation.w = float(q[3])

                    # Publish to ROS
                    self.publisher.publish(pose_stamped)

                    # Set AMBF position
                    self.obj_handle.set_pos(pose_stamped.pose.position.x,
                                            pose_stamped.pose.position.y,
                                            pose_stamped.pose.position.z)

                    # Convert quaternion to RPY and set AMBF orientation
                    rpy = tf.transformations.euler_from_quaternion(q)
                    if hasattr(self.obj_handle, 'set_rpy'):
                        self.obj_handle.set_rpy(*rpy)

                    rospy.loginfo('Publishing: "%s"' % pose_stamped)
            except Exception as e:
                rospy.loginfo('Failed to get pose: %s' % str(e))
            self.rate.sleep()

    def matrix_to_quaternion(self, R):
        """Convert a rotation matrix to a quaternion."""
        q = np.empty((4,), dtype=np.float32)
        tr = np.trace(R)
        if tr > 0:
            S = np.sqrt(tr + 1.0) * 2
            q[3] = 0.25 * S
            q[0] = (R[2, 1] - R[1, 2]) / S
            q[1] = (R[0, 2] - R[2, 0]) / S
            q[2] = (R[1, 0] - R[0, 1]) / S
        else:
            if (R[0, 0] > R[1, 1]) and (R[0, 0] > R[2, 2]):
                S = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
                q[3] = (R[2, 1] - R[1, 2]) / S
                q[0] = 0.25 * S
                q[1] = (R[0, 1] + R[1, 0]) / S
                q[2] = (R[0, 2] + R[2, 0]) / S
            elif R[1, 1] > R[2, 2]:
                S = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
                q[3] = (R[0, 2] - R[2, 0]) / S
                q[0] = (R[0, 1] + R[1, 0]) / S
                q[1] = 0.25 * S
                q[2] = (R[1, 2] + R[2, 1]) / S
            else:
                S = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
                q[3] = (R[1, 0] - R[0, 1]) / S
                q[0] = (R[0, 2] + R[2, 0]) / S
                q[1] = (R[1, 2] + R[2, 1]) / S
                q[2] = 0.25 * S
        return q

def main():
    obj_name = "drill_reference"  # Change this to your object's name
    pose_publisher = PosePublisher(obj_name)
    pose_publisher.publish_pose()


if __name__ == '__main__':
    main()
