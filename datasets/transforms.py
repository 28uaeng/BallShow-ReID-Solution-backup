"""
自定义数据增强变换
针对篮球场景的遮挡、运动模糊等特殊增强
"""
import random
import numpy as np
import torch
from PIL import Image


class RandomOcclusion:
    """
    随机遮挡增强
    模拟篮球比赛中的包夹、遮挡场景
    """
    def __init__(self, probability=0.2, scale=(0.02, 0.15), ratio=(0.3, 3.0)):
        """
        Args:
            probability: 应用遮挡的概率
            scale: 遮挡区域占图像面积的比例范围 (最小，最大)
            ratio: 遮挡区域的宽高比范围
        """
        self.probability = probability
        self.scale = scale
        self.ratio = ratio
    
    def __call__(self, img):
        if random.random() < self.probability:
            return img
        
        # 转换为 numpy 数组
        if isinstance(img, torch.Tensor):
            img_np = img.numpy()
            img_np = np.transpose(img_np, (1, 2, 0))
        else:
            img_np = np.array(img)
        
        h, w = img_np.shape[:2]
        img_area = h * w
        
        # 随机生成遮挡区域
        target_area = random.uniform(*self.scale) * img_area
        aspect_ratio = random.uniform(*self.ratio)
        
        occlusion_h = int(round(np.sqrt(target_area * aspect_ratio)))
        occlusion_w = int(round(np.sqrt(target_area / aspect_ratio)))
        
        # 确保遮挡区域在图像范围内
        occlusion_h = min(occlusion_h, h)
        occlusion_w = min(occlusion_w, w)
        
        # 随机位置
        top = random.randint(0, h - occlusion_h)
        left = random.randint(0, w - occlusion_w)
        
        # 创建遮挡（使用随机颜色或灰色）
        if random.random() < 0.5:
            # 随机颜色
            color = [random.randint(0, 255) for _ in range(3)]
        else:
            # 灰色（模拟阴影遮挡）
            gray = random.randint(50, 150)
            color = [gray, gray, gray]
        
        img_np[top:top + occlusion_h, left:left + occlusion_w] = color
        
        # 转回 PIL Image 或 Tensor
        if isinstance(img, torch.Tensor):
            img_np = np.transpose(img_np, (2, 0, 1))
            return torch.from_numpy(img_np)
        else:
            return Image.fromarray(img_np)


class RandomMotionBlur:
    """
    随机运动模糊增强
    模拟篮球运动员快速移动时的模糊效果
    """
    def __init__(self, probability=0.2, kernel_size=(5, 15), angle=(0, 360)):
        """
        Args:
            probability: 应用模糊的概率
            kernel_size: 模糊核大小范围
            angle: 模糊方向角度范围
        """
        self.probability = probability
        self.kernel_size_range = kernel_size
        self.angle_range = angle
    
    def __call__(self, img):
        if random.random() < self.probability:
            return img
        
        import cv2
        
        # 转换为 numpy 数组
        if isinstance(img, torch.Tensor):
            img_np = img.numpy()
            img_np = np.transpose(img_np, (1, 2, 0))
        else:
            img_np = np.array(img)
        
        # 随机参数
        kernel_size = random.randint(*self.kernel_size_range)
        angle = random.uniform(*self.angle_range)
        
        # 创建运动模糊核
        kernel = self._create_motion_kernel(kernel_size, angle)
        
        # 应用卷积
        img_blur = cv2.filter2D(img_np, -1, kernel)
        
        # 转回
        if isinstance(img, torch.Tensor):
            img_blur = np.transpose(img_blur, (2, 0, 1))
            return torch.from_numpy(img_blur)
        else:
            return Image.fromarray(img_blur)
    
    def _create_motion_kernel(self, size, angle):
        """创建运动模糊核"""
        import cv2
        
        ax = np.cos(np.deg2rad(angle - 90)) * (size // 2)
        ay = np.sin(np.deg2rad(angle - 90)) * (size // 2)
        
        # 创建线条作为运动模糊核
        kernel = np.zeros((size, size), dtype=np.float32)
        cv2.line(kernel, 
                (size//2 - int(ax), size//2 - int(ay)), 
                (size//2 + int(ax), size//2 + int(ay)), 
                1.0, 1)
        
        # 归一化
        kernel /= np.sum(kernel)
        
        return kernel


class RandomLighting:
    """
    随机光照变化增强
    模拟不同场地的灯光条件（室内反光、夜间灯光等）
    """
    def __init__(self, probability=0.3, brightness=0.2, contrast=0.2, saturation=0.2):
        """
        Args:
            probability: 应用增强的概率
            brightness: 亮度调整范围
            contrast: 对比度调整范围
            saturation: 饱和度调整范围
        """
        self.probability = probability
        self.brightness = brightness
        self.contrast = contrast
        self.saturation = saturation
    
    def __call__(self, img):
        if random.random() < self.probability:
            return img
        
        import cv2
        
        # 转换为 numpy 数组
        if isinstance(img, torch.Tensor):
            img_np = img.numpy()
            img_np = np.transpose(img_np, (1, 2, 0))
        else:
            img_np = np.array(img)
        
        # 随机调整
        # 1. 亮度
        if random.random() < 0.5:
            alpha = random.uniform(1 - self.brightness, 1 + self.brightness)
            img_np = cv2.convertScaleAbs(img_np, alpha=alpha, beta=0)
        
        # 2. 对比度
        if random.random() < 0.5:
            alpha = random.uniform(1 - self.contrast, 1 + self.contrast)
            beta = random.uniform(-20, 20)
            img_np = cv2.convertScaleAbs(img_np, alpha=alpha, beta=beta)
        
        # 3. 饱和度（转换到 HSV 空间）
        if random.random() < 0.5:
            hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv)
            s = s.astype(np.float32)
            s = s * random.uniform(1 - self.saturation, 1 + self.saturation)
            s = np.clip(s, 0, 255).astype(np.uint8)
            hsv = cv2.merge([h, s, v])
            img_np = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        # 转回
        if isinstance(img, torch.Tensor):
            img_np = np.transpose(img_np, (2, 0, 1))
            return torch.from_numpy(img_np)
        else:
            return Image.fromarray(img_np)
