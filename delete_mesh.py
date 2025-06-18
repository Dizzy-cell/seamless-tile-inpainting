import bpy
import numpy as np
from PIL import Image
import bmesh

# 设置图像路径（替换为你自己的路径）
image_path = "/Users/honor/OneDrive/blender/depth_heatmap.png"


# 加载图像并转换为 NumPy 数组
img = Image.open(image_path).convert("L")  # "L" 表示灰度图
width, height = img.size
depth_data = np.array(img) / 255.0  # 归一化到 [0, 1]

depth_data = np.flipud(depth_data)

base_size_y = 8
base_size_x = base_size_y * (width / height)  # 根据图像宽高比计算 X 方向长度

# 创建网格平面（默认是正方形）
bpy.ops.mesh.primitive_grid_add(
    x_subdivisions=width,
    y_subdivisions=height,
    size=1.0  # 先用单位大小创建，后面再缩放
)

grid_obj = bpy.context.active_object

# 缩放物体以匹配图像宽高比
grid_obj.scale.x = base_size_x / 2  # 因为 size 是“从中心到边缘”的距离
grid_obj.scale.y = base_size_y / 2
grid_obj.scale.z = 1.0  # Z 不缩放

# 更新变换
grid_obj.data.update()
mesh = grid_obj.data

# 创建基础网格（平面）
#bpy.ops.mesh.primitive_grid_add(x_subdivisions=width, y_subdivisions=height, size=8)
#mesh_obj = bpy.context.active_object
#mesh = mesh_obj.data

# 修改顶点 Z 值
for i, vertex in enumerate(mesh.vertices):
    x = int(vertex.co.x  * width)  # 映射 UV 到图像坐标
    y = int(vertex.co.y * height)
    
    x += 371
    y += 231
     
    #if 0 <= x < width and 0 <= y < height:
    z_value = depth_data[y, x]  # 高度缩放系数
    #vertex.co.z = 0 # z_value * 20
    scale = (1 - z_value) / 0.5
    
    scale = 1
    vertex.co.x = vertex.co.x * scale
    vertex.co.y = vertex.co.y * scale
    vertex.co.z = 5 * (1 - scale)

# 更新网格
mesh.update()


grid_obj = bpy.context.active_object
mesh = grid_obj.data

bpy.context.view_layer.objects.active = grid_obj
bpy.ops.object.mode_set(mode='EDIT')

faces_to_delete = []

# 获取网格数据
bm = bmesh.from_edit_mesh(mesh)

# 遍历所有面
for i, face in enumerate(bm.faces):
    # 获取面的中心坐标
    # center = face.calc_center_median()
    
    z = None
    for vert in face.verts:
        if z is None:
            z = vert.co.z
        elif z != vert.co.z:
            faces_to_delete.append(face)
            break

print(faces_to_delete)

# 删除指定的面
bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')

# 更新网格并返回物体模式
bmesh.update_edit_mesh(mesh)
bpy.ops.object.mode_set(mode='OBJECT')
