# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------

from PIL import Image

from qai_hub_models.models._shared.depth_estimation.app import DepthEstimationApp
from qai_hub_models.utils.args import (
    demo_model_from_cli_args,
    get_model_cli_parser,
    get_on_device_demo_parser,
    validate_on_device_demo_args,
)
from qai_hub_models.utils.asset_loaders import CachedWebModelAsset, load_image
from qai_hub_models.utils.base_model import BaseModel
from qai_hub_models.utils.display import display_or_save_image

from IPython import embed
import numpy as np


# The demo will display a heatmap of the estimated depth at each point in the image.
def depth_estimation_demo(
    model_cls: type[BaseModel],
    model_id,
    default_image: CachedWebModelAsset,
    is_test: bool = False,
):
    parser = get_model_cli_parser(model_cls)
    parser = get_on_device_demo_parser(parser, add_output_dir=True)
    parser.add_argument(
        "--image",
        type=str,
        default=default_image,
        help="image file path or URL",
    )
    args = parser.parse_args([] if is_test else None)
    model = demo_model_from_cli_args(model_cls, model_id, args)
    validate_on_device_demo_args(args, model_id)

    # Load image
    (_, _, height, width) = model_cls.get_input_spec()["image"][0]
    image = load_image(args.image)

    print("Image size ",image.size)
    print("Model Loaded")

    app = DepthEstimationApp(model, height, width)
    heatmap_image = app.estimate_depth(image)
    assert isinstance(heatmap_image, Image.Image)

    image_array = np.array(heatmap_image)
    print(heatmap_image.size)
    heatmap_image.save("depth_heatmap.png")

    embed()


    if not is_test:
        # Resize / unpad annotated image
        display_or_save_image(
            heatmap_image, args.output_dir, "out_heatmap.png", "heatmap"
        )

from qai_hub_models.models.depth_anything_v2.model import (
    MODEL_ASSET_VERSION,
    MODEL_ID,
    DepthAnythingV2,
)
from qai_hub_models.utils.asset_loaders import CachedWebModelAsset

INPUT_IMAGE_ADDRESS = CachedWebModelAsset.from_asset_store(
    MODEL_ID, MODEL_ASSET_VERSION, "test_input_image.jpg"
)

print(INPUT_IMAGE_ADDRESS)

def main(is_test: bool = False):
    depth_estimation_demo(DepthAnythingV2, MODEL_ID, INPUT_IMAGE_ADDRESS, is_test)


if __name__ == "__main__":
    main()

import bpy
import numpy as np
from PIL import Image

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
    y += 232
    
    #if 0 <= x < width and 0 <= y < height:
    z_value = depth_data[y, x]  # 高度缩放系数
    #vertex.co.z = 0 # z_value * 20
    scale = (1 - z_value) / 0.5
    
    #scale = 1
    vertex.co.x = vertex.co.x * scale
    vertex.co.y = vertex.co.y * scale
    vertex.co.z = 6.46 * (1 - scale)

# 更新网格
mesh.update()
