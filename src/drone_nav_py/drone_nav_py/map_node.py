import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid

class MapNode(Node):
    def __init__(self):
        super().__init__('map_node')
        self.publisher_ = self.create_publisher(OccupancyGrid, 'map', 10)
        self.timer = self.create_timer(1.0, self.publish_map)

    def publish_map(self):
        msg = OccupancyGrid()
        msg.info.width = 10
        msg.info.height = 10
        msg.info.resolution = 1.0
        msg.data = [0]*100 
        self.publisher_.publish(msg)
        self.get_logger().info('Map published')

def main(args=None):
    rclpy.init(args=args)
    node = MapNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
