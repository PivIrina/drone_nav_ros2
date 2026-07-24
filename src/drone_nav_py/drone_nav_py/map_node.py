import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid

class MapNode(Node):
    def __init__(self):
        super().__init__('map_node')
        
        self.declare_parameter('map_min_x', 0.0)
        self.declare_parameter('map_min_y', 0.0)
        self.declare_parameter('map_max_x', 15.0)
        self.declare_parameter('map_max_y', 15.0)
        
        self.map_min_x = self.get_parameter('map_min_x').value
        self.map_min_y = self.get_parameter('map_min_y').value
        self.map_max_x = self.get_parameter('map_max_x').value
        self.map_max_y = self.get_parameter('map_max_y').value
        
        self.width = int(self.map_max_x - self.map_min_x)
        self.height = int(self.map_max_y - self.map_min_y)
        
        self.publisher_ = self.create_publisher(OccupancyGrid, 'map', 10)
        self.timer = self.create_timer(1.0, self.publish_map)

    def publish_map(self):
        msg = OccupancyGrid()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.info.width = self.width
        msg.info.height = self.height
        msg.info.resolution = 1.0
        msg.info.origin.position.x = float(self.map_min_x)
        msg.info.origin.position.y = float(self.map_min_y)
        msg.info.origin.orientation.w = 1.0
        msg.data = [0] * (self.width * self.height)
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MapNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()