import bpy
import os

# 设置输出路径（你可以改成你自己的路径）
output_path = "/tmp/blender_renders/"

# 创建目录（如果不存在）
os.makedirs(output_path, exist_ok=True)

# 定义要渲染的相机列表
cameras = ["Camera_plane", "Camera_distort"]  # 替换为你自己的相机名称
object_names = ['fabric_plane', 'fabric_didtort_multiresolution']

for filename in ['/tmp/blender_renders/test.png']:
    
    for obj_name in object_names:
        obj = bpy.data.objects.get(obj_name)
        material = obj.data.materials[0]
        
        material.use_nodes=True
        nodes = material.node_tree.nodes
        
        texture_node = nodes.get("Image Texture")
        new_image = bpy.data.images.load(filename)
        texture_node.image = new_image
        
        shader_node = nodes.get("Principled BSDF")
        links = material.node_tree.links
        links.new(texture_node.outputs["Color"], shader_node.inputs["Base Color"])
        
    
    for position in range(-2, -5, -1):
        num = 0
        for i, cam_name in enumerate(cameras):
            # 获取相机对象
            camera = bpy.data.objects.get(cam_name)
            if not camera:
                print(f"找不到相机: {cam_name}")
                continue
            
            camera.location = (i*4, position , 0)  # X, Y, Z
            
            # 设置当前场景相机
            bpy.context.scene.camera = camera
            

            # 设置输出文件名
            bpy.context.scene.render.filepath = os.path.join(output_path, f"{cam_name}_{position}")

            # 渲染并保存图像
            bpy.ops.render.render(write_still=True)
            print(f"已渲染并保存: {cam_name}")
        
