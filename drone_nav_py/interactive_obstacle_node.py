import rclpy
from rclpy.node import Node
from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from visualization_msgs.msg import InteractiveMarker, InteractiveMarkerControl, Marker
from geometry_msgs.msg import Point

class InteractiveObstacle(Node):
    def __init__(self):
        super().__init__('interactive_obstacle_node')

        self.obstacle_pub = self.create_publisher(Point, '/obstacles', 10)
        self.server = InteractiveMarkerServer(self, 'obstacle_marker')
        self.counter = 0
        self.get_logger().info("InteractiveObstacle node started")
        self.create_marker(2.0, 2.0)
        self.create_marker(3.0, 1.0)

    def create_marker(self, x, y):
        marker = InteractiveMarker()
        marker.header.frame_id = "map"
        marker.name = f"obstacle_{self.counter}"
        marker.description = f"Obstacle {self.counter}"
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = 0.5

        cube_marker = Marker()
        cube_marker.type = Marker.CUBE
        cube_marker.scale.x = 1.0
        cube_marker.scale.y = 1.0
        cube_marker.scale.z = 1.0
        cube_marker.color.r = 1.0
        cube_marker.color.g = 0.0
        cube_marker.color.b = 0.0
        cube_marker.color.a = 1.0

        control = InteractiveMarkerControl()
        control.always_visible = True
        control.markers.append(cube_marker)
        marker.controls.append(control)

        move_control = InteractiveMarkerControl()
        move_control.name = "move_xy"
        move_control.interaction_mode = InteractiveMarkerControl.MOVE_PLANE
        marker.controls.append(move_control)

        self.server.insert(marker)  
        self.server.setCallback(marker.name, self.marker_feedback)

        self.server.applyChanges()
        self.counter += 1
       
    def marker_feedback(self, feedback):
        point = Point()
        point.x = feedback.pose.position.x
        point.y = feedback.pose.position.y
        point.z = feedback.pose.position.z
        self.obstacle_pub.publish(point)
        self.get_logger().info(f"published obstacle at ({point.x:.2f}, {point.y:.2f}, {point.z:.2f})")


def main(args=None):
    rclpy.init(args=args)
    node = InteractiveObstacle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()