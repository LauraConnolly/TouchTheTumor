#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
from ambf_client import Client
import time
import tf.transformations
import pyigtl
from scipy.spatial.transform import Rotation as R
import numpy as np
import vtk

 # This script is used to recieve the pivot calibrations (CauteryTipToCautery and NeedleTipToNeedle) from SlicerROS2 and to
 # automate the transfer of data from pyigtl to AMBF
class launch_pyigtl_control_loop():

    def __init__(self):
        # Initialize some of the data
        self.needleTipToneedle = None
        self.cauteryTipToCautery = None
        self.openigtlinkclient = None
        self.drill_handle = None
        self.tumor_handle = None

    def needleTipCallback(self, msg):
        self.needleTipToneedle = msg
        print("Needle Tip To Needle Transform: {}".format(msg))

    def cauteryTipCallback(self, msg):
        self.cauteryTipToCautery = msg
        print("Cautery Tip To Cautery Transform: {}".format(msg))

    def initializeOpenIGTLinkConnections(self, client_name):
        self.openigtlinkclient = pyigtl.OpenIGTLinkClient(host="169.254.184.175", port=18944)

    def initializeAMBFConnections(self, slicer_obj_name, tumor_obj_name):
        client_name = None
        self.client = Client(client_name) if client_name else Client()
        self.client.connect()

        self.drill_handle = self.client.get_obj_handle(slicer_obj_name)
        self.tumor_handle = self.client.get_obj_handle(tumor_obj_name)

        if self.drill_handle.object_type != 'RIGID_BODY' or self.tumor_handle.object_type != 'RIGID_BODY':
            raise ValueError("Both objects must be of type RIGID_BODY")

    def recieveIGTLAndPublishToROS(self):
        CauteryToReference = self.openigtlinkclient.wait_for_message("CauteryToReference", timeout=3)
        CauteryToReferenceMatrix = self.matrix_to_pose(CauteryToReference.matrix, "Cautery")
        CauteryToReferenceNumpy = self.pose_to_numpy_matrix(CauteryToReferenceMatrix.pose)
        CauteryTipToCauteryNumpy = self.pose_to_numpy_matrix(self.cauteryTipToCautery.pose)
        CauteryTipToReferenceMatrix = tf.transformations.concatenate_matrices(CauteryToReferenceNumpy, CauteryTipToCauteryNumpy)
        CauteryTipToReference = self.matrix_to_pose(CauteryTipToReferenceMatrix, "CauteryTip")
        self.publish_to_ambf(self.drill_handle, CauteryTipToReference, "cautery")

        # Needle tip to needle shouldn't be applied to the tumor
        NeedleToReference = self.openigtlinkclient.wait_for_message("NeedleToReference", timeout=3)
        NeedleToReferenceMatrix = self.matrix_to_pose(NeedleToReference.matrix, "Needle")
        self.publish_to_ambf(self.tumor_handle, NeedleToReferenceMatrix, "needle")


    def pose_to_numpy_matrix(self, pose):

        px, py, pz = pose.position.x, pose.position.y, pose.position.z
        ox, oy, oz, ow = pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w

        # Convert quaternion to rotation matrix
        rotation_matrix = tf.transformations.quaternion_matrix([ox, oy, oz, ow])

        transform_matrix = rotation_matrix
        transform_matrix[0:3, 3] = [px, py, pz]

        return transform_matrix

    def matrix_to_quaternion_xyz(self, matrix):

        rotation_matrix = matrix[:3, :3]
        rotation = R.from_matrix(rotation_matrix)
        quaternion = rotation.as_quat()  # Returns [x, y, z, w] for SciPy
        translation = matrix[:3, 3]

        return quaternion, translation

    def matrix_to_pose(self, matrix, name):
        pose = PoseStamped()
        pose.header.stamp = rospy.Time.now()
        pose.header.frame_id = name # You should set the correct reference frame ID

        quaternion, translation = self.matrix_to_quaternion_xyz(matrix)
        pose.pose.orientation.x = quaternion[0]
        pose.pose.orientation.y = quaternion[1]
        pose.pose.orientation.z = quaternion[2]
        pose.pose.orientation.w = quaternion[3]

        pose.pose.position.x = translation[0] * 0.001
        pose.pose.position.y = translation[1] * 0.001
        pose.pose.position.z = translation[2] * 0.001
        if name == "CauteryTip":
            print("Pose from OpenIGTLink: {}".format(matrix))
        return pose

    def publish_to_ambf(self, handle, msg, controllee):

        px, py, pz = msg.pose.position.x * 10000, msg.pose.position.y * 10000, msg.pose.position.z * 10000
        # if it's needle to refernece - multiple by 10 to scale to the simulation coordinates - without it, convert units and then simulation
        if controllee == "needle":
            px, py, pz = msg.pose.position.x*10, msg.pose.position.y*10, msg.pose.position.z*10

        orientation = msg.pose.orientation
        quaternion = (orientation.x, orientation.y, orientation.z,orientation.w)
        if controllee == "cautery":
            print("Publishing from OpenIGTLink to AMBF {}: pose {}, rpy {}".format(controllee, (px, py, pz), (quaternion)))

        handle.set_pos(px, py, pz)
        handle.set_rot(quaternion)
        print("Publishing to AMBF")

    def timer_callback(self, event):
        self.recieveIGTLAndPublishToROS()

    def run(self):
        rospy.spin()

def main():

    # Node that controls the cautery
    drill_obj_name = "drill_reference"
    # Node that controls the tumor
    tumor_obj_name = "volume_reference"

    # Capture data from Slicer
    rospy.init_node('ambf_client', anonymous=True)

    control_loop = launch_pyigtl_control_loop()

    # Get the pivot calibration results for the needle and cautery (published from SlicerROS2)
    # Script waits for 5 seconds for these to be published
    print("Publish pivot calibrations from Slicer.")
    rospy.Subscriber('/NeedleTipToNeedle', PoseStamped, control_loop.needleTipCallback)
    rospy.Subscriber('/CauteryTipToCautery', PoseStamped, control_loop.cauteryTipCallback)
    time.sleep(5)

    # Activate OpenIGTLink connections
    print(" Now activate OpenIGTLink connections")
    control_loop.initializeOpenIGTLinkConnections(None) # None is the arguement called client_name
    control_loop.initializeAMBFConnections(drill_obj_name, tumor_obj_name)

    # Run the control loop
    timer = rospy.Timer(rospy.Duration(0.001), control_loop.timer_callback)
    control_loop.run()


if __name__ == '__main__':
    main()