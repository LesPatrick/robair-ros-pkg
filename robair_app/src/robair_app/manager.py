import rospy
import uuid

from robair_msgs.msg import Command

from robair_common.utils import get_local_ip_address

from .xmpp.client import ClientXMPP
from .xmpp.rpc import remote
from .player import run_player


class RobotManager(ClientXMPP):
    def __init__(self, node_name):
        rospy.init_node(node_name)
        jid = rospy.get_param('robot_jabber_id')
        password = rospy.get_param('robot_jabber_password')
        super(RobotManager, self).__init__(jid, password)
        self.cmd_publisher = rospy.Publisher('/cmd', Command)
        self.clients = []

    @remote
    def hello(self, key):
        # TODO: use ressource manager website !
        # jid = self.current_rpc_session().client_jid
        # self.clients.append(jid)
        return True
        # url = rospy.get_param('robair_api_url')
        # r = requests.get(url + "check", params={"key": key})
        # authorize = r.json()['valid']
        # if r.json()['valid']:
        #     jid = self.current_rpc_session().client_jid
        #     self.clients[jid] = self.get_proxy(jid)
        #     run_player(self.get_url_streaming(),
        #                self.clients[jid].get_url_streaming())
        # return authorize

    @remote
    def run_video_player(self, remote_url):
        # Improve this with ROS srv...
        local_url = "http://%s:%d" % (get_local_ip_address(), 9090)
        run_player(local_url, remote_url)
        return local_url

    @remote
    def publish_cmd(self, cmd):
        # jid = self.current_rpc_session().client_jid
        # if jid in self.clients:
        self.cmd_publisher.publish(cmd)
        return True


class ClientManager(ClientXMPP):
    def __init__(self, node_name):
        jid = rospy.get_param('tv_jabber_id')
        password = rospy.get_param('tv_jabber_password')
        super(ClientManager, self).__init__(jid, password)
        rospy.init_node(node_name)
        self.robot_jid = rospy.get_param('robot_jabber_id')
        self.proxy_robot = self.get_proxy(self.robot_jid)
        # if not self.proxy_robot.hello(self.make_reservation()):
        #     raise RuntimeError('RobAir permission denied, try later...')
        # subscriber to a remote cmd
        self.run_video_player()
        rospy.Subscriber('/cmd', Command, self.proxy_robot.publish_cmd)

    def make_reservation(self):
        # TODO: use ressource manager website !
        # url = rospy.get_param('robair_api_url')
        # r = requests.get(url + "new", params={"jid": self.jid})
        # data = r.json()
        # if data['error']:
        #     log.info("Error: %s" % data['error_message'])
        # else:
        #     return data['key']
        return uuid.uuid4()

    def run_video_player(self):
        # Improve this with ROS srv...
        local_url = "http://%s:%d" % (get_local_ip_address(), 9090)
        remote_url = self.proxy_robot.run_video_player(local_url)
        run_player(local_url, remote_url)
