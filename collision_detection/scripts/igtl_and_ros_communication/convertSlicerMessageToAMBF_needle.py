
from ambf_client import Client
import time
import rospy
from geometry_msgs.msg import PoseStamped
from argparse import ArgumentParser
import tf.transformations


class ObjectControl:
    def __init__(self, obj_name, client_name):
        if client_name:
            self.client = Client(client_name)
        else:
            self.client = Client()
        self.client.connect()
        time.sleep(0.3)
        self.obj_handle = self.client.get_obj_handle(obj_name)
        time.sleep(0.3)

        if self.obj_handle.object_type == 'RIGID_BODY':
            self._pose_supported = True
        else:
            self._pose_supported = False

    def pose_callback(self, msg):
        if self._pose_supported:
            # Extract position
            px, py, pz = msg.pose.position.x, msg.pose.position.y, msg.pose.position.z

            # Extract orientation quaternion
            orientation = msg.pose.orientation
            quaternion = (orientation.x, orientation.y, orientation.z, orientation.w)

            # Convert quaternion to RPY
            rpy = tf.transformations.euler_from_quaternion(quaternion)

            # Set position and orientation
            self.obj_handle.set_pos(px, py, pz)
            if hasattr(self.obj_handle, 'set_rpy'):
                self.obj_handle.set_rpy(*rpy)  # Assuming there is a method to set RPY
            else:
                print("The method to set RPY does not exist")

    def run(self):
        if not rospy.core.is_initialized():
            rospy.init_node('ambf_object_controller1', anonymous=True)
        rospy.Subscriber('/tumor_transform', PoseStamped, self.pose_callback)
        rospy.spin()


def main():
    parser = ArgumentParser()
    parser.add_argument('-o', action='store', dest='obj_name', help='Specify AMBF Obj Name')
    parser.add_argument('-a', action='store', dest='client_name', help='Client Name', default=None)

    parsed_args = parser.parse_args()
    print('Specified Arguments:', parsed_args)

    oc = ObjectControl(parsed_args.obj_name, parsed_args.client_name)
    oc.run()


if __name__ == '__main__':
    main()
