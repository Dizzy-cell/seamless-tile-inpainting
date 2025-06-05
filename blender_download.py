import bpy

def focus_on_object(obj_name):
    # 取消所有选中
    bpy.ops.object.select_all(action='DESELECT')
    
    # 获取目标对象
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"找不到名为 {obj_name} 的物体")
        return
    
    # 选中该物体并设为活动对象
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # 遍历所有视图区域并设置视角
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            region = None
            for reg in area.regions:
                if reg.type == 'WINDOW':
                    region = reg
                    break
            if region:
                # 设置视角为中心点
                space.region_3d.view_location = obj.location.copy()
                space.region_3d.view_distance = 10.0  # 调整距离
                space.region_3d.view_rotation.identity()
# 示例调用
focus_on_object("Cube")
bpy.ops.scene.blenderkit_download(asset_index=1, target_object="Cube", material_target_slot=0, model_location=(1, 0.201052, 0.281936), model_rotation=(0, 0, 0))


