import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker
from std_msgs.msg import ColorRGBA
import random

class ObstaclePublisher(Node):
    def __init__(self):
        super().__init__('obstacle_node')

        self.point_pub = self.create_publisher(Point, '/obstacles', 10)
        self.marker_pub = self.create_publisher(Marker, '/obstacles_marker', 10)

        self.obstacles = []
        self.map_min_x = 0.0
        self.map_max_x = 15.0
        self.map_min_y = 0.0
        self.map_max_y = 15.0


        self.create_timer(0.5, self.publish_all_obstacles)
        self.create_timer(5.0, self.add_random_obstacle)
        self.get_logger().info('ObstaclePublisher started')


        self.add_obstacle(2.0, 2.0)
        self.add_obstacle(3.0, 1.0)
        self.add_obstacle(5.0, 4.0)
        self.add_obstacle(6.0, 6.0)


    def add_obstacle(self, x, y, z=0.0):
        obstacle = (float(x), float(y), float(z))
        if obstacle not in self.obstacles:
            self.obstacles.append(obstacle)
            self.get_logger().info(f'Obstacle added at {obstacle}')


    def add_random_obstacle(self):
        x = random.uniform(self.map_min_x + 1.0, self.map_max_x - 1.0)
        y = random.uniform(self.map_min_y + 1.0, self.map_max_y - 1.0)
        self.add_obstacle(x, y)


    def publish_all_obstacles(self):
        for idx, obstacle in enumerate(self.obstacles):
            x, y, z = obstacle
            point_msg = Point()
            point_msg.x = x
            point_msg.y = y
            point_msg.z = z
            self.point_pub.publish(point_msg)

            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "obstacles"
            marker.id = idx
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = z + 0.5
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.5
            marker.scale.y = 0.5
            marker.scale.z = 1.0
            marker.color = ColorRGBA(r=1.0, g=0.0, b=0.0, a=1.0)
            self.marker_pub.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = ObstaclePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
