import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, PoseStamped
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker
import heapq
import math

class PathNode(Node):
    def __init__(self):
        super().__init__('path_node')
        
        self.declare_parameter('map_min_x', 0.0)
        self.declare_parameter('map_min_y', 0.0)
        self.declare_parameter('map_max_x', 15.0)
        self.declare_parameter('map_max_y', 15.0)
        self.declare_parameter('goal_x', 10.0)
        self.declare_parameter('goal_y', 10.0)
        self.declare_parameter('step', 1.0)
        
        self.map_min = (
            self.get_parameter('map_min_x').value,
            self.get_parameter('map_min_y').value
        )
        self.map_max = (
            self.get_parameter('map_max_x').value,
            self.get_parameter('map_max_y').value
        )
        self.goal = (
            self.get_parameter('goal_x').value,
            self.get_parameter('goal_y').value
        )
        self.step = self.get_parameter('step').value
        
        self.start = (0.0, 0.0)
        self.obstacles = []
        
        self.current_position = [self.start[0], self.start[1]]
        
        self.path_points = []
        
        self.path_pub = self.create_publisher(Path, 'path', 10)
        self.marker_pub = self.create_publisher(Marker, 'drone_marker', 10)
        
        self.obstacle_sub = self.create_subscription(
            PoseStamped, '/obstacles', self.obstacle_callback, 10
        )
        
        self.timer = self.create_timer(0.1, self.update_drone)
        self.generate_new_path()
        
        self.get_logger().info(
            f'PathNode started: map={self.map_min}->{self.map_max}, '
            f'goal={self.goal}, step={self.step}'
        )

    def obstacle_callback(self, msg):
        obstacle = (msg.pose.position.x, msg.pose.position.y)
        if obstacle not in self.obstacles:
            self.obstacles.append(obstacle)
            self.get_logger().info(f'New obstacle at {obstacle}')
            self.generate_new_path()

    def is_inside_map(self, x, y):
        return (self.map_min[0] <= x <= self.map_max[0] and 
                self.map_min[1] <= y <= self.map_max[1])

    def heuristic(self, pos, goal):
        return math.sqrt((pos[0]-goal[0])**2 + (pos[1]-goal[1])**2)

    def generate_new_path(self):
        start = tuple(self.current_position)
        goal = self.goal
        
        open_set = []
        heapq.heappush(open_set, (0 + self.heuristic(start, goal), 0, start, [start]))
        visited = set()
        
        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            
            if current in visited:
                continue
            visited.add(current)
            

            if math.hypot(current[0]-goal[0], current[1]-goal[1]) < self.step:
                self.path_points = path + [goal]
                self.get_logger().info(f'Path found: {len(self.path_points)} points')
                return
            
            for dx, dy in [
                (self.step, 0), (-self.step, 0),
                (0, self.step), (0, -self.step),
                (self.step, self.step), (-self.step, -self.step),
                (self.step, -self.step), (-self.step, self.step)
            ]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if not self.is_inside_map(*neighbor):
                    continue
                
                if any(math.hypot(neighbor[0]-obs[0], neighbor[1]-obs[1]) < self.step 
                       for obs in self.obstacles):
                    continue
                
                if neighbor in visited:
                    continue
                
                g_new = g + math.hypot(dx, dy)
                f_new = g_new + self.heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_new, g_new, neighbor, path + [neighbor]))
        
        self.get_logger().warn('No path found!')

    def update_drone(self):
        if not self.path_points:
            return
        
        target = self.path_points[0]
        dx = target[0] - self.current_position[0]
        dy = target[1] - self.current_position[1]
        distance = math.hypot(dx, dy)
        speed = 0.3  
        
        if distance < speed:
            self.current_position[0] = target[0]
            self.current_position[1] = target[1]
            self.path_points.pop(0)
        else:
            self.current_position[0] += speed * dx / distance
            self.current_position[1] += speed * dy / distance
        
        self.publish_path()
        self.publish_marker()

    def publish_path(self):
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        path_msg.header.stamp = self.get_clock().now().to_msg()

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.pose.position.x = float(self.current_position[0])
        pose.pose.position.y = float(self.current_position[1])
        pose.pose.orientation.w = 1.0
        path_msg.poses.append(pose)

        for x, y in self.path_points:
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.orientation.w = 1.0
            path_msg.poses.append(pose)
        
        self.path_pub.publish(path_msg)

    def publish_marker(self):
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = self.current_position[0]
        marker.pose.position.y = self.current_position[1]
        marker.pose.position.z = 0.5
        marker.scale.x = 0.3
        marker.scale.y = 0.3
        marker.scale.z = 0.3
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 1.0
        self.marker_pub.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = PathNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()