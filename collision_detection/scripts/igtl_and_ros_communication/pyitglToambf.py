# import pyigtl
# client = pyigtl.OpenIGTLinkClient(host="169.254.184.175", port=18944)
# message = client.wait_for_message("NeedleToTracker", timeout=3)
# print(message)

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import pyigtl
import numpy as np


class PosePublisher(Node):
    def __init__(self):
        super().__init__('pose_publisher')
        self.publisher = self.create_publisher(PoseStamped, 'pose_topic', 10)
        self.timer = self.create_timer(0.1, self.publish_pose)
        self.client = pyigtl.OpenIGTLinkClient(host="169.254.184.175", port=18944)

    def publish_pose(self):
        try:
            message = self.client.wait_for_message("NeedleToTracker", timeout=3)
            if message:
                pose_stamped = PoseStamped()
                pose_stamped.header.stamp = self.get_clock().now().to_msg()
                pose_stamped.header.frame_id = "world"

                # Extract translation from the matrix and cast to float
                pose_stamped.pose.position.x = float(message.matrix[0, 3])
                pose_stamped.pose.position.y = float(message.matrix[1, 3])
                pose_stamped.pose.position.z = float(message.matrix[2, 3])

                # Convert the rotation matrix to a quaternion and ensure it's float
                q = self.matrix_to_quaternion(message.matrix[0:3, 0:3])
                pose_stamped.pose.orientation.x = float(q[0])
                pose_stamped.pose.orientation.y = float(q[1])
                pose_stamped.pose.orientation.z = float(q[2])
                pose_stamped.pose.orientation.w = float(q[3])

                self.publisher.publish(pose_stamped)
                self.get_logger().info('Publishing: "%s"' % pose_stamped)
        except Exception as e:
            self.get_logger().info('Failed to get pose: %s' % str(e))

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


def main(args=None):
    rclpy.init(args=args)
    pose_publisher = PosePublisher()
    rclpy.spin(pose_publisher)

    pose_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
