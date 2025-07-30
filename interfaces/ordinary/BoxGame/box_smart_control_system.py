from collections import deque
import numpy as np
import time

class SmartControlSystem:
    """智能双模式控制系统
    
    实现摇杆模式和触控板模式的自动切换控制：
    - 摇杆模式：轻微滑动时，基于COP位移方向的相对控制
    - 触控板模式：明显滑动时，基于COP位移的相对控制
    
    🔄 坐标系统说明：
    - 传感器坐标系：64x64网格，(0,0)在左上角，X向右，Y向下
    - 游戏坐标系：与传感器坐标系相同，箱子在传感器网格中移动
    - 角度定义：0°=右，90°=下，180°=左，270°=上（传感器坐标系）
    - 方向映射：手指向右下滑动 → 箱子向右下移动
    """
    
    def __init__(self):
        # 🎮 控制模式
        self.JOYSTICK_MODE = "joystick"
        self.TOUCHPAD_MODE = "touchpad"
        self.IDLE_MODE = "idle"
        self.current_mode = self.IDLE_MODE
        
        # 📏 COP距离分段阈值
        self.joystick_threshold = 0.05    # 摇杆模式阈值（轻微滑动）
        self.touchpad_threshold = 10    # 触控板模式阈值（明显滑动）
        
        # ⚙️ 摇杆模式参数
        self.joystick_sensitivity = 2.0  # 摇杆灵敏度
        self.joystick_max_speed = 8.0    # 最大移动速度
        self.joystick_smoothing = 0.8    # 运动平滑系数
        
        # 🖱️ 触控板模式参数
        self.touchpad_sensitivity = 1.2  # 触控板灵敏度
        self.touchpad_damping = 0.3      # 阻尼系数
        self.touchpad_max_range = 20.0   # 最大移动范围
        
        # 📊 状态跟踪
        self.last_velocity = np.array([0.0, 0.0])
        self.accumulated_displacement = np.array([0.0, 0.0])
        self.mode_switch_time = 0.0
        self.mode_history = deque(maxlen=5)
        
        # 🎯 控制中心位置（传感器中央）
        self.control_center = np.array([32.0, 32.0])
        
        print("🎮 智能双模式控制系统初始化完成")
        print(f"📏 COP距离阈值: 摇杆={self.joystick_threshold}, 触控板={self.touchpad_threshold}")
    
    def detect_cop_distance_mode(self, current_cop, initial_cop):
        """基于COP距离检测控制模式"""
        if current_cop is None or initial_cop is None:
            return self.IDLE_MODE, 0.0
        
        # 计算COP位移距离
        dx = current_cop[0] - initial_cop[0]
        dy = current_cop[1] - initial_cop[1]
        distance = np.sqrt(dx*dx + dy*dy)
        
        # 基于距离分段判断（使用小量epsilon处理浮点数精度）
        epsilon = 1e-10
        if distance < self.joystick_threshold - epsilon:
            return self.IDLE_MODE, distance
        elif distance < self.touchpad_threshold - epsilon:
            return self.JOYSTICK_MODE, distance
        else:
            return self.TOUCHPAD_MODE, distance
    
    def update_control_mode(self, is_contact, current_cop, initial_cop):
        """更新控制模式 - 基于COP距离自动切换"""
        old_mode = self.current_mode
        
        if not is_contact:
            self.current_mode = self.IDLE_MODE
        else:
            # 🎮 双模式：基于COP距离分段判断
            detected_mode, distance = self.detect_cop_distance_mode(current_cop, initial_cop)
            self.current_mode = detected_mode
        
        # 记录模式切换
        if old_mode != self.current_mode:
            self.mode_switch_time = time.time()
            self.mode_history.append((self.current_mode, time.time()))
            
            # 计算当前距离用于调试
            if current_cop is not None and initial_cop is not None:
                dx = current_cop[0] - initial_cop[0]
                dy = current_cop[1] - initial_cop[1]
                distance = np.sqrt(dx*dx + dy*dy)
            else:
                distance = 0.0
            
            print(f"🔄 控制模式切换: {old_mode} → {self.current_mode}")
            print(f"   接触: {is_contact}, 距离: {distance:.3f}")
            print(f"   阈值: 摇杆={self.joystick_threshold}, 触控板={self.touchpad_threshold}")
            
            # 模式切换时重置状态
            if self.current_mode == self.TOUCHPAD_MODE:
                self.accumulated_displacement = np.array([0.0, 0.0])
            elif self.current_mode == self.JOYSTICK_MODE:
                self.last_velocity = np.array([0.0, 0.0])
    
    def calculate_joystick_control(self, current_cop, initial_cop, box_position):
        """摇杆模式控制计算 - 基于COP位移方向"""
        if current_cop is None or initial_cop is None:
            return box_position
        
        # 🎯 计算COP位移方向
        cop_displacement = np.array([
            current_cop[0] - initial_cop[0],  # X方向位移
            current_cop[1] - initial_cop[1]   # Y方向位移
        ])
        
        # 计算位移距离和方向
        displacement_magnitude = np.linalg.norm(cop_displacement)
        if displacement_magnitude < 1e-6:  # 避免除零
            self.last_velocity *= 0.9
            return box_position + self.last_velocity
        
        # 归一化方向向量
        direction = cop_displacement / displacement_magnitude
        
        # 🚀 基于距离计算速度（在摇杆阈值范围内）
        # 将距离映射到速度：joystick_threshold -> 0, touchpad_threshold -> max_speed
        distance_ratio = (displacement_magnitude - self.joystick_threshold) / (self.touchpad_threshold - self.joystick_threshold)
        distance_ratio = np.clip(distance_ratio, 0.0, 1.0)
        
        # 非线性速度响应
        speed_factor = distance_ratio ** 0.7
        target_speed = speed_factor * self.joystick_max_speed * self.joystick_sensitivity
        
        # 🎮 计算目标速度向量
        target_velocity = direction * target_speed
        
        # 🌊 平滑处理
        self.last_velocity = (self.joystick_smoothing * self.last_velocity + 
                             (1 - self.joystick_smoothing) * target_velocity)
        
        # 📍 计算新位置
        new_position = box_position + self.last_velocity
        
        return new_position
    
    def calculate_touchpad_control(self, current_cop, initial_cop, box_position):
        """触控板模式控制计算 - 相对控制"""
        if current_cop is None or initial_cop is None:
            return box_position
        
        # 🖱️ 计算COP位移 - 传感器坐标系
        # 传感器坐标系：(0,0)在左上角，X向右，Y向下
        cop_displacement = np.array([
            current_cop[0] - initial_cop[0],  # X方向位移（右为正）
            current_cop[1] - initial_cop[1]   # Y方向位移（下为正）
        ])
        
        # 🎯 限制位移范围
        displacement_magnitude = np.linalg.norm(cop_displacement)
        if displacement_magnitude > self.touchpad_max_range:
            cop_displacement = cop_displacement * (self.touchpad_max_range / displacement_magnitude)
        
        # 🖱️ 应用触控板灵敏度和阻尼
        scaled_displacement = cop_displacement * self.touchpad_sensitivity
        self.accumulated_displacement = (self.accumulated_displacement * self.touchpad_damping + 
                                       scaled_displacement * (1 - self.touchpad_damping))
        
        # 📍 计算目标位置 - 相对控制：基于当前箱子位置 + 手指滑动方向
        # 手指向右滑动 → 箱子向右移动
        # 手指向下滑动 → 箱子向下移动
        target_position = box_position + self.accumulated_displacement
        
        return target_position
    
    def calculate_target_position(self, is_contact, current_cop, initial_cop, 
                                box_position, box_original_position):
        """统一的目标位置计算接口"""
        
        # 🔄 更新控制模式
        self.update_control_mode(is_contact, current_cop, initial_cop)
        
        if self.current_mode == self.JOYSTICK_MODE:
            # 🎮 摇杆模式：基于COP位移方向的相对控制
            target_position = self.calculate_joystick_control(
                current_cop, initial_cop, box_position
            )
        elif self.current_mode == self.TOUCHPAD_MODE:
            # 🖱️ 触控板模式：基于COP位移的相对控制
            target_position = self.calculate_touchpad_control(
                current_cop, initial_cop, box_position
            )
        else:
            # 🛑 空闲模式：返回原始位置
            target_position = box_position.copy()
            self.last_velocity *= 0.95  # 逐渐停止
            self.accumulated_displacement *= 0.95  # 逐渐复位
        
        return target_position
    
    def get_control_info(self):
        """获取控制系统状态信息"""
        return {
            'mode': self.current_mode,
            'system_mode': 'dual_mode',  # 固定为双模式
            'velocity': self.last_velocity.copy(),
            'displacement': self.accumulated_displacement.copy(),
            'mode_switch_time': self.mode_switch_time,
            'joystick_sensitivity': self.joystick_sensitivity,
            'touchpad_sensitivity': self.touchpad_sensitivity,
            'joystick_threshold': self.joystick_threshold,
            'touchpad_threshold': self.touchpad_threshold
        }
    
    def update_parameters(self, params):
        """更新控制参数"""
        self.joystick_sensitivity = params.get('joystick_sensitivity', self.joystick_sensitivity)
        self.joystick_max_speed = params.get('joystick_max_speed', self.joystick_max_speed)
        self.joystick_smoothing = params.get('joystick_smoothing', self.joystick_smoothing)
        self.joystick_threshold = params.get('joystick_threshold', self.joystick_threshold)
        self.touchpad_threshold = params.get('touchpad_threshold', self.touchpad_threshold)
        
        self.touchpad_sensitivity = params.get('touchpad_sensitivity', self.touchpad_sensitivity)
        self.touchpad_damping = params.get('touchpad_damping', self.touchpad_damping)
        self.touchpad_max_range = params.get('touchpad_max_range', self.touchpad_max_range)
        
        print(f"🎮 控制系统参数已更新")
    
    def reset(self):
        """重置控制系统"""
        self.current_mode = self.IDLE_MODE
        self.last_velocity = np.array([0.0, 0.0])
        self.accumulated_displacement = np.array([0.0, 0.0])
        self.mode_history.clear()
        print("🔄 控制系统已重置")
    
    def reset_on_contact_end(self):
        """接触结束时重置累积位移"""
        self.accumulated_displacement = np.array([0.0, 0.0])
        print("🔄 接触结束，累积位移已重置")