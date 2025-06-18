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

world_point = unproject_pixel((960, 540, 1), K, RT)
print("wold point", world_point)
