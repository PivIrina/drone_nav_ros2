import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
import math

class PathNode(Node):
    def __init__(self):
        super().__init__('path_node')

        self.map_min = (0.0, 0.0)
        self.map_max = (15.0, 15.0)
        self.step = 1.0  
        self.goal = (10.0, 10.0)
        self.obstacles = []
        self.path_points = []

        self.current_position = self.start

        self.path_pub = self.create_publisher(Path, 'path', 10)

        self.obstacle_sub = self.create_subscription(Point,'/obstacles', self.obstacle_callback, 10)

        self.drone_sub = self.create_subscription(Point, '/drone_position', self.drone_position_callback, 10)

        self.timer = self.create_timer(0.1, self.publish_path)
        self.generate_new_path()
        self.get_logger().info('Path Node started')

    def drone_position_callback(self, msg):
        self.current_position = (msg.x, msg.y)

    def obstacle_callback(self, msg):
        obstacle = (msg.x, msg.y)
        if obstacle not in self.obstacles:
            self.obstacles.append(obstacle)
        self.generate_new_path()


    def is_inside_map(self, x, y):
        return self.map_min[0] <= x <= self.map_max[0] and self.map_min[1] <= y <= self.map_max[1]
    def generate_new_path(self):
        start = self.current_position
        goal = self.goal
        path = [start]
        x, y = start
        gx, gy = goal

        max_iterations = 500
        i = 0

        while (x, y) != (gx, gy) and i < max_iterations:
            i += 1
            candidates = [
                (x + self.step, y),
                (x, y + self.step),
                (x + self.step, y + self.step)
            ]
            candidates.sort(key=lambda p: abs(p[0]-gx) + abs(p[1]-gy))

            moved = False
            for nx, ny in candidates:
                if not self.is_inside_map(nx, ny):
                    continue
                if (nx, ny) in self.obstacles:
                    continue
                x, y = nx, ny
                path.append((x, y))
                moved = True
                break
            if not moved:
                self.get_logger().warning('Path blocked by obstacles!')
                break

        self.path_points = path

    def publish_path(self):
        if not self.path_points:
            return
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        path_msg.header.stamp = self.get_clock().now().to_msg()
        for x, y in self.path_points:
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.position.z = 0.0
            pose.pose.orientation.w = 1.0
            path_msg.poses.append(pose)
        self.path_pub.publish(path_msg)


def main(args=None):
    rclpy.init(args=args)
    node = PathNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
