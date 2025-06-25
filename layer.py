import numpy as np

from IPython import embed
from PIL import Image

# 设置图像路径（替换为你自己的路径）
image_path = "/Users/honor/OneDrive/blender/depth_ori.png"

image_ori_path = "/Users/honor/OneDrive/blender/pxfuel_ori.png"

img_ori = Image.open(image_ori_path).convert("RGB")  # 确保图像是 RGB 模式
img_ori_np = np.array(img_ori)

print(img_ori.size)

# 加载图像并转换为 NumPy 数组
img = Image.open(image_path).convert("L")  # "L" 表示灰度图
width, height = img.size
depth_data = np.array(img) / 255.0  # 归一化到 [0, 1]

print(img.size)

for i in range(0, 20, 1):
    l = i * 1.0 / 20.0
    r = l + 0.05
    mask_bool = ((depth_data >= l) & (depth_data < r))
    mask = mask_bool.astype(np.uint8)  # 0 or 1

    # 转换为图像（放大 255 以可视化）
    mask_img = Image.fromarray(mask * 255)
    mask_img.save(f"depth_mask_{l:.2f}_{r:.2f}.png")
    print(f"Saved: depth_mask_{l:.2f}_{r:.2f}.png → shape: {mask.shape}")
    
    masked_img_np = img_ori_np.copy()
    masked_img_np[~mask_bool] = (0, 0, 0)
    Image.fromarray(masked_img_np).save(f"masked_depth_{l:.2f}_{r:.2f}.png")

    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    rgba[..., :3] = img_ori_np

    # 设置 Alpha 通道：mask 为 True 的位置 alpha = 255，其他为 0（透明）
    rgba[..., 3] = (mask_bool * 255).astype(np.uint8)
    out_path = f"masked_transparent_{l:.2f}_{r:.2f}.png"
    Image.fromarray(rgba).save(out_path)

#embed()
