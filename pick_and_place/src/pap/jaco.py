from robot import Robot
import rospy
import kinova_msgs.msg
from kinova_msgs.srv import HomeArm
import actionlib
from geometry_msgs.msg import Point, Quaternion, Pose, PoseStamped
from std_msgs.msg import Header, Int64, Bool
import numpy as np

class JacoGripper(object):
    def __init__(self, robot_type='j2n6a300'):
        self.tol = 1.0
        self.robot_type = robot_type
        self.finger_maxDist = 18.9/2/1000  # max distance for one finger
        self.finger_maxTurn = 7400  # max thread rotation for one finger
        self.currentFingerPercent = [0.0, 0.0, 0.0]
        self.finger_pos_sub = rospy.Subscriber('/{}_driver/out/finger_position'.format(robot_type),
                                                kinova_msgs.msg.FingerPosition,
                                                self.setCurrentFingerPercent)
    def set_position(self, position):
        """Accept position from 0 (open) to 100 (closed)."""
        action_address = ('/{}_driver/fingers_action/'
                          'finger_positions'.format(self.robot_type))
        client = actionlib.SimpleActionClient(
            action_address,
            kinova_msgs.msg.SetFingersPositionAction)
        client.wait_for_server()
        position_turns = np.clip(position, 0, 100) / 100 * self.finger_maxTurn
        goal = kinova_msgs.msg.SetFingersPositionGoal()
        goal.fingers.finger1 = float(position_turns[0])
        goal.fingers.finger2 = float(position_turns[1])
        if len(position) < 3:
            goal.fingers.finger3 = 0.0
        else:
            goal.fingers.finger3 = float(position_turns[2])
        client.send_goal(goal)
        if client.wait_for_result(rospy.Duration(5.0)):
            return client.get_result()
        else:
            client.cancel_all_goals()
            rospy.logwarn('        the gripper action timed-out')

    def open(self):
        self.set_position([0, 0, 0])

    def close(self):
        self.set_position([100, 100, 100])

    def close_with_feedback(self, fingers):
        return 0

    def setCurrentFingerPercent(self,msg):
        finger_value = [0.0, 0.0, 0.0]
        finger_value[0] = msg.finger1
        finger_value[1] = msg.finger2
        finger_value[2] = msg.finger3
        #finger_turn = [x / 100.0 * self.finger_maxTurn for x in finger_value]
        finger_percent = [x / self.finger_maxTurn * 100.0 for x in finger_value]
        self.currentFingerPercent = finger_percent

class Jaco(Robot):
    def __init__(self, robot_type='j2n6a300', *args, **kwargs):
        super(Jaco, self).__init__(base='root')
        self.robot_type = robot_type
        # self.home()
        self.gripper = JacoGripper()

        self.velocity_pub = rospy.Publisher(
            '/{}_driver/in/cartesian_velocity'.format(self.robot_type),
            kinova_msgs.msg.PoseVelocity,
            queue_size=1)


    def home(self):
        addr = '/{}_driver/in/home_arm'.format(self.robot_type)
        rospy.wait_for_service(addr)
        try:
            serv = rospy.ServiceProxy(addr, HomeArm)
            rep = serv()
            rospy.loginfo(rep)
        except rospy.ServiceException as e:
            rospy.loginfo("Service error {}".format(e))

    def move_ik(self, stamped_pose):
        """Take a PoseStamped and move the arm there.

        """
        action_address = ('/' + self.robot_type + '_driver/pose_action/tool_pose')
        self.client = actionlib.SimpleActionClient(
                    action_address,
                    kinova_msgs.msg.ArmPoseAction)

        if not isinstance(stamped_pose, PoseStamped):
            raise TypeError("No duck typing here? :(")
        pose = stamped_pose.pose
        position, orientation = pose.position, pose.orientation
        # Send a cartesian goal to the action server. Adapted from kinova_demo
        rospy.loginfo("Waiting for SimpleAction server")
        self.client.wait_for_server()

        goal = kinova_msgs.msg.ArmPoseGoal()
        goal.pose.header = Header(frame_id=(self.robot_type + '_link_base'))
        goal.pose.pose.position = position
        goal.pose.pose.orientation = orientation

        rospy.loginfo("Sending goal")
        print goal
        self.client.send_goal(goal)

        # rospy.loginfo("Waiting for up to {} s for result".format(t))
        if self.client.wait_for_result(rospy.Duration(100)):
            rospy.loginfo("Action succeeded")
            print self.client.get_result()
            return self.client.get_result()
        else:
            self.client.cancel_all_goals()
            rospy.loginfo('        the cartesian action timed-out')
            return None

    def move_joints(self,jointangles):
        """Take a joint angles and move the arm.

        """
        action_address_joints = ('/' + self.robot_type +
                          '_driver/joints_action/joint_angles')
        self.client_joints = actionlib.SimpleActionClient(
            action_address_joints,
            kinova_msgs.msg.ArmJointAnglesAction)

        self.client_joints.wait_for_server()

        goal = kinova_msgs.msg.ArmJointAnglesGoal()

        goal.angles.joint1 = jointangles[0]
        goal.angles.joint2 = jointangles[1]
        goal.angles.joint3 = jointangles[2]
        goal.angles.joint4 = jointangles[3]
        goal.angles.joint5 = jointangles[4]
        goal.angles.joint6 = jointangles[5]

        self.client_joints.send_goal(goal)
        if self.client_joints.wait_for_result(rospy.Duration(100.0)):
            return self.client_joints.get_result()
        else:
            print('        the joint angle action timed-out')
            self.client_joints.cancel_all_goals()
            return None


    def kinematic_control(self,msg):
        self.velocity_pub.publish(msg)
            # r.sleep()
