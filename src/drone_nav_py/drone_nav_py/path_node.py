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

        # Настройки карты
        self.map_min = (0.0, 0.0)
        self.map_max = (15.0, 15.0)
        self.step = 1.0
        self.start = (0.0, 0.0)
        self.goal = (10.0, 10.0)
        self.obstacles = []

        # Текущая позиция дрона
        self.current_position = [self.start[0], self.start[1]]

        # Полный путь, рассчитанный A*
        self.path_points = []

        # Публикаторы
        self.path_pub = self.create_publisher(Path, 'path', 10)
        self.marker_pub = self.create_publisher(Marker, 'drone_marker', 10)

        # Подписка на препятствия
        self.obstacle_sub = self.create_subscription(Point,'/obstacles', self.obstacle_callback, 10)

        # Таймер обновления движения
        self.timer = self.create_timer(0.1, self.update_drone)

        # Расчёт начального пути
        self.generate_new_path()
        self.get_logger().info('PathNode with smooth A* started')

    def obstacle_callback(self, msg):
        obstacle = (msg.x, msg.y)
        if obstacle not in self.obstacles:
            self.obstacles.append(obstacle)
            self.generate_new_path()

    def is_inside_map(self, x, y):
        return self.map_min[0] <= x <= self.map_max[0] and self.map_min[1] <= y <= self.map_max[1]

    def heuristic(self, pos, goal):
        return abs(pos[0]-goal[0]) + abs(pos[1]-goal[1])

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
            if current == goal:
                self.path_points = path
                return
            # Рассматриваем соседние клетки
            for dx, dy in [(self.step,0),(0,self.step),(self.step,self.step),(-self.step,0),(0,-self.step),(-self.step,-self.step)]:
                neighbor = (current[0]+dx, current[1]+dy)
                if not self.is_inside_map(*neighbor) or neighbor in self.obstacles or neighbor in visited:
                    continue
                g_new = g + self.step
                f_new = g_new + self.heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_new, g_new, neighbor, path + [neighbor]))
        self.get_logger().warning("No path found!")
        self.path_points = []

    def update_drone(self):
        if not self.path_points:
            return

        target = self.path_points[0]
        dx = target[0] - self.current_position[0]
        dy = target[1] - self.current_position[1]
        distance = math.hypot(dx, dy)
        speed = 0.1  # скорость перемещения за таймер

        if distance < speed:
            # дошли до точки
            self.current_position[0] = target[0]
            self.current_position[1] = target[1]
            self.path_points.pop(0)
        else:
            # движение к точке
            self.current_position[0] += speed * dx / distance
            self.current_position[1] += speed * dy / distance

        self.publish_path()
        self.publish_marker()

    def publish_path(self):
        path_msg = Path()
        path_msg.header.frame_id = 'map'
        path_msg.header.stamp = self.get_clock().now().to_msg()
        path_msg.poses = []
        for x, y in [tuple(self.current_position)] + self.path_points:
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.position.z = 0.5
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
        marker.scale.x = 0.5
        marker.scale.y = 0.5
        marker.scale.z = 0.5
        marker.color.r = 0.0
        marker.color.g = 0.0
        marker.color.b = 1.0
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
