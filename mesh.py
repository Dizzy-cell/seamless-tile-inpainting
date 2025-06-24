import bpy
import numpy as np
from PIL import Image
import bmesh

import bpy
import math
import mathutils

import numpy as np

def get_3x4_RT_matrix_from_blender(cam):
    """从相机对象中提取 3x4 的外参矩阵 [R | t]"""
    cam_matrix = cam.matrix_world.normalized().to_4x4()
    cam_rot = cam_matrix.to_quaternion().to_matrix().transposed()
    cam_pos = cam_matrix.translation

    RT = mathutils.Matrix((
        cam_rot[0][:] + (-cam_rot[0].dot(cam_pos), ),
        cam_rot[1][:] + (-cam_rot[1].dot(cam_pos), ),
        cam_rot[2][:] + (-cam_rot[2].dot(cam_pos), )
    ))

    return RT

def project_point(world_point, K, RT):
    """
    投影一个 3D 世界坐标点到 2D 图像平面
    :param world_point: (x, y, z) 世界坐标点
    :param K: 内参矩阵 (3x3)
    :param RT: 外参矩阵 (3x4)
    :return: (u, v) 图像坐标
    """
    point = np.array([*world_point, 1])  # 齐次坐标
    
    uvw = K @ RT @ point
    u, v, w = uvw
    
    return round(u/w), round(v/w), w
    #return (int(u / w), int(v / w))

def unproject_pixel(uvw, K, RT):
    """
    已知图像坐标 (u, v, w)，内参 K 和外参 RT，计算空间点
    :param uvw: (u, v, w) 归一化图像坐标（齐次）
    :param K: 内参矩阵 (3x3)
    :param RT: 外参矩阵 (3x4)
    :return: 相机坐标系和世界坐标系下的 3D 点
    """
    u, v, w = uvw

    # Step 1: 图像坐标 → 相机坐标
    xyz_cam = np.linalg.inv(K) @ np.array([u, v, w])
    P_camera = xyz_cam * 1  # 如果已知真实深度，可以乘上 depth

    # Step 2: 相机坐标 → 世界坐标
    RT_inv = invert_RT(RT)
    P_world = RT_inv @ np.append(P_camera, 1)

    return P_camera, P_world

def invert_RT(RT):
    """求外参矩阵的逆"""
    R = RT[:, :3].T
    t = -R @ RT[:, 3]
    return np.hstack((R, t.reshape(3, 1)))

# 获取当前场景中的相机对象
camera = bpy.context.scene.camera
if not camera:
    raise Exception("没有激活的相机")

# 获取相机数据
cam_data = camera.data

# =============================
# 🔹 获取相机内参 (Intrinsic)
# =============================

# 图像分辨率（渲染设置）
render = bpy.context.scene.render
width = render.resolution_x * render.resolution_percentage / 100
height = render.resolution_y * render.resolution_percentage / 100

print(width, height)
#(1920, 1080)

# 焦距（以像素为单位）
sensor_width = cam_data.sensor_width  # 模拟传感器宽度（mm）
focal_length = cam_data.lens           # 焦距（mm）

print(sensor_width, focal_length)
# (36, 50)

# 计算像素焦距（fx, fy）
scale_x = width / sensor_width * focal_length
scale_y = height / sensor_width * focal_length

print(scale_x, scale_y)
#(2667, 1500)

# 主点（图像中心）
cx = width / 2.0
cy = height / 2.0

K = [[scale_x, 0, cx],
     [0, scale_y, cy],
     [0, 0, 1]]

print("📸 相机内参矩阵 K:")
for row in K:
    print(row)

# =============================
# 🔸 获取相机外参 (Extrinsic)
# =============================

# 获取相机的世界变换矩阵
matrix_world = camera.matrix_world

# 提取旋转和平移
R = matrix_world.to_euler('XYZ').to_matrix().to_3x3()
t = matrix_world.translation

# 构建外参矩阵 [R | t]
extrinsic = matrix_world.to_3x3()

print("\n🌍 相机外参矩阵 [R | t]:")
for row in extrinsic:
    print(row[:])

print(R)
print(t)

origin = (0, 0, 0)

world_point = (0, 0, 0)  # 世界坐标
#K = np.array(K)  # 示例内参
#R = np.array(R)
#t = np.array(t).reshape(3,1)
#print(K.shape, t.shape)
#RT = np.hstack((R, t))  # 示例外参（相机在原点）
#print(RT.shape)

#screen_point = project_point(world_point, K, RT)
#print("图像坐标:", screen_point)

world_point = (0, 0, 0)  # 世界坐标

#K = np.array([[1000, 0, 960], [0, 1000, 540], [0, 0, 1]])  # 示例内参
#RT = np.hstack((np.eye(3), np.zeros((3, 1))))  # 示例外参（相机在原点）

RT = get_3x4_RT_matrix_from_blender(camera)
print("RT", RT)
RT = np.array(RT)

screen_point = project_point(world_point, K, RT)
print("图像坐标:", screen_point)


import bpy
import math
import mathutils

import numpy as np

def get_3x4_RT_matrix_from_blender(cam):
    """从相机对象中提取 3x4 的外参矩阵 [R | t]"""
    cam_matrix = cam.matrix_world.normalized().to_4x4()
    cam_rot = cam_matrix.to_quaternion().to_matrix().transposed()
    cam_pos = cam_matrix.translation

    RT = mathutils.Matrix((
        cam_rot[0][:] + (-cam_rot[0].dot(cam_pos), ),
        cam_rot[1][:] + (-cam_rot[1].dot(cam_pos), ),
        cam_rot[2][:] + (-cam_rot[2].dot(cam_pos), )
    ))

    return RT

def project_point(world_point, K, RT):
    """
    投影一个 3D 世界坐标点到 2D 图像平面
    :param world_point: (x, y, z) 世界坐标点
    :param K: 内参矩阵 (3x3)
    :param RT: 外参矩阵 (3x4)
    :return: (u, v) 图像坐标
    """
    point = np.array([*world_point, 1])  # 齐次坐标
    
    uvw = K @ RT @ point
    u, v, w = uvw
    
    return round(u/w), round(v/w), w
    #return (int(u / w), int(v / w))

# 获取当前场景中的相机对象
camera = bpy.context.scene.camera
if not camera:
    raise Exception("没有激活的相机")

# 获取相机数据
cam_data = camera.data

# =============================
# 🔹 获取相机内参 (Intrinsic)
# =============================

# 图像分辨率（渲染设置）
render = bpy.context.scene.render
width = render.resolution_x * render.resolution_percentage / 100
height = render.resolution_y * render.resolution_percentage / 100

print(width, height)
#(1920, 1080)

# 焦距（以像素为单位）
sensor_width = cam_data.sensor_width  # 模拟传感器宽度（mm）
focal_length = cam_data.lens           # 焦距（mm）

print(sensor_width, focal_length)
# (36, 50)

# 计算像素焦距（fx, fy）
scale_x = width / sensor_width * focal_length
scale_y = height / sensor_width * focal_length

print(scale_x, scale_y)
#(2667, 1500)

# 主点（图像中心）
cx = width / 2.0
cy = height / 2.0

K = [[scale_x, 0, cx],
     [0, scale_y, cy],
     [0, 0, 1]]

print("📸 相机内参矩阵 K:")
for row in K:
    print(row)

# =============================
# 🔸 获取相机外参 (Extrinsic)
# =============================

# 获取相机的世界变换矩阵
matrix_world = camera.matrix_world

# 提取旋转和平移
R = matrix_world.to_euler('XYZ').to_matrix().to_3x3()
t = matrix_world.translation

# 构建外参矩阵 [R | t]
extrinsic = matrix_world.to_3x3()

print("\n🌍 相机外参矩阵 [R | t]:")
for row in extrinsic:
    print(row[:])

print(R)
print(t)

origin = (0, 0, 0)

world_point = (0, 0, 0)  # 世界坐标

RT = get_3x4_RT_matrix_from_blender(camera)
print("RT", RT)
RT = np.array(RT)

screen_point = project_point(world_point, K, RT)
print("图像坐标:", screen_point)


dis = -5
world_point = unproject_pixel((960 * dis, 540 * dis, dis), K, RT)
print("wold point", world_point)

x,y = 0, 0
world_point = unproject_pixel((x * dis, y * dis, dis), K, RT)
print("wold point", x,y, world_point)

x,y = 1920, 1080
world_point = unproject_pixel((x * dis, y * dis, dis), K, RT)
print("wold point", x,y, world_point)

#for x in range(10):
#    for y in range(10):
#        world_point = unproject_pixel((x * dis, y * dis, dis), K, RT)
#        print("wold point", x, y, world_point)
        


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
    x_subdivisions=20,
    y_subdivisions=10,
    size=1.0  # 先用单位大小创建，后面再缩放
)

#(-0.5, 0.5)

grid_obj = bpy.context.active_object

## 缩放物体以匹配图像宽高比
grid_obj.scale.x = 2.0 * 1.8 # 因为 size 是“从中心到边缘”的距离
grid_obj.scale.y = 1.0 * 1.8
grid_obj.scale.z = 1.0  # Z 不缩放

# apply the scale
bpy.context.view_layer.objects.active = grid_obj  # 确保它是活动对象
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


## 更新变换
#grid_obj.data.update()
#mesh = grid_obj.data

## 创建基础网格（平面）
##bpy.ops.mesh.primitive_grid_add(x_subdivisions=width, y_subdivisions=height, size=8)
##mesh_obj = bpy.context.active_object
##mesh = mesh_obj.data

## 修改顶点 Z 值
#for i, vertex in enumerate(mesh.vertices):
#    x = int(vertex.co.x * width)  # 映射 UV 到图像坐标
#    y = int(vertex.co.y * height)
#    
#    x += 371
#    y += 231
#     
#    #if 0 <= x < width and 0 <= y < height:
#    z_value = depth_data[y, x]  # 高度缩放系数
#    #vertex.co.z = 0 # z_value * 20
#    scale = (1 - z_value) / 0.5
#    
#    #print(vertex.co.xy)
#    scale = 1
#    vertex.co.x = vertex.co.x * scale * 3.6
#    vertex.co.y = vertex.co.y * scale * 3.6
#    vertex.co.z = 5 * (1 - scale)

## 更新网格
#mesh.update()


#    grid_obj = bpy.context.active_object
#    mesh = grid_obj.data

#    bpy.context.view_layer.objects.active = grid_obj
#    bpy.ops.object.mode_set(mode='EDIT')

#    faces_to_delete = []

#    # 获取网格数据
#    bm = bmesh.from_edit_mesh(mesh)

#    # 遍历所有面
#    for i, face in enumerate(bm.faces):
#        # 获取面的中心坐标
#        # center = face.calc_center_median()
#        
#        z = None
#        for vert in face.verts:
#            if z is None:
#                z = vert.co.z
#            elif z != vert.co.z:
#                faces_to_delete.append(face)
#                break

#    print(faces_to_delete)

#    # 删除指定的面
#    bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')

#    # 更新网格并返回物体模式
#    bmesh.update_edit_mesh(mesh)
#    bpy.ops.object.mode_set(mode='OBJECT')
