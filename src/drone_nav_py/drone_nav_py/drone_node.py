import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
import math

class DroneMarker(Node):
    def __init__(self):
        super().__init__('drone_marker_node')

        self.x = 0.0
        self.y = 0.0
        self.path_points = []
        self.current_index = 0
        self.declare_parameter('speed', 2.0)
        self.speed = self.get_parameter('speed').value
        self.marker_pub = self.create_publisher(Marker, 'drone_marker', 10)
        self.position_pub = self.create_publisher(Point, '/drone_position', 10)
        self.path_sub = self.create_subscription(Path, 'path', self.path_callback, 10)
        self.timer = self.create_timer(0.05, self.move_along_path)

        self.get_logger().info(f'DroneMarker started with speed={self.speed}')

    def path_callback(self, msg):
        self.path_points = [(pose.pose.position.x, pose.pose.position.y) for pose in msg.poses]
        if not self.path_points:
            return
        self.current_index = min(range(len(self.path_points)), key=lambda i: (self.path_points[i][0]-self.x)**2 + (self.path_points[i][1]-self.y)**2)

    def move_along_path(self):
        if not self.path_points or self.current_index >= len(self.path_points):
            self.publish_marker()
            self.publish_position()
            return

        target_x, target_y = self.path_points[self.current_index]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        step_size = self.speed * 0.05

        if dist <= step_size:
            self.x = target_x
            self.y = target_y
            self.current_index += 1
        else:
            self.x += dx / dist * step_size
            self.y += dy / dist * step_size

        self.publish_marker()
        self.publish_position()

    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = self.x
        marker.pose.position.y = self.y
        marker.pose.position.z = 0.5
        marker.scale.x = 0.5
        marker.scale.y = 0.5
        marker.scale.z = 0.5
        marker.color.r = 0.0
        marker.color.g = 0.0
        marker.color.b = 1.0
        marker.color.a = 1.0
        self.marker_pub.publish(marker)

    def publish_position(self):
        msg = Point()
        msg.x = self.x
        msg.y = self.y
        msg.z = 0.0
        self.position_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DroneMarker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
