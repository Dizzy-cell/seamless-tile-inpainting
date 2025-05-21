import bpy
import numpy as np
from PIL import Image, ImageDraw
import sys
print(sys.executable)

text_name = "DebugOutput"
txt = bpy.data.texts.get(text_name)
if not txt:
    txt = bpy.data.texts.new(text_name)

txt.clear()
txt.write("以下是雕饰区域的信息:\n")


# 设置输出路径
output_path = "/tmp/"

# 设置图像大小
image_size = (1024, 1024)

# 获取当前活动对象
obj = bpy.context.active_object
me = obj.data

# 获取 UV 数据
uv_layer = me.uv_layers.active.data

# 获取顶点组
vertex_group_name = "Group"  # 替换为你自己的顶点组名称
vg = obj.vertex_groups.get(vertex_group_name)
if not vg:
    raise Exception(f"顶点组 {vertex_group_name} 不存在")

# 创建 mask 图像
width, height = image_size
mask_image = np.zeros((height, width), dtype=np.uint8)

vertex_groups = obj.vertex_groups

for vg in vertex_groups:
    group_name = vg.name
    txt.write(f" -> 正在处理顶点组: {group_name}\n")
    
    width, height = image_size
    mask_image = np.zeros((height, width), dtype=np.uint8)
    # 遍历所有面
    for face_index, poly in enumerate(me.polygons):
        points = []
        for loop_index in poly.loop_indices:
            loop = me.loops[loop_index]
            uv = uv_layer[loop.index].uv
            x = int(uv.x * (width - 1))
            y = int((1.0 - uv.y) * (height - 1))  # Flip Y to match image coordinates
            
            try:
                vert_idx = loop.vertex_index
                weight = vg.weight(vert_idx)
            except:
                continue

            if weight > 0.5:
                if 0 <= x < width and 0 <= y < height:
                    points.append((x, y))
        
        txt.write(f"{points}\n")
        
        # 如果有至少三个点，进行填充
        if len(points) >= 3:
            # 创建临时图像用于绘制多边形
            temp_img = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(temp_img)
            draw.polygon(points, fill=255)  # 每个面一个编号（从 1 开始）
            mask_data = np.array(temp_img)
            mask_image[mask_data > 0] =  255 # 保留编号信息


    #np.save(f"{output_path}/mask.npy", mask_image)

    ## 保存图像

    img = Image.fromarray(mask_image, mode='L')
    img.save(f"/Users/honor/Downloads/future/MiniCPM-o/mask_{group_name}.png")

    txt.write("顶点组 Mask 图像已保存！")
