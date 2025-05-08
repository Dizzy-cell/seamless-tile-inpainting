import torch
from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline
from diffusers import AutoPipelineForImage2Image
from diffusers.utils import make_image_grid, load_image

from PIL import Image

from IPython import embed 

def tile_image_fuction(original_image, tile_width_repeat = 2, tile_height_repeat = 2):

    original_width, original_height = original_image.size

    tile_width = original_width * tile_width_repeat
    tile_height = original_height * tile_height_repeat
    tiled_image = Image.new('RGB', (tile_width, tile_height))
    
    for x in range(0, tile_width, original_width):
        for y in range(0, tile_height, original_height):
            tiled_image.paste(original_image, (x, y))

    return tiled_image

def flatten(model: torch.nn.Module):
    children = list(model.children())
    flattened = []

    if children == []:
        return model

    for child in children:
        try:
            flattened.extend(flatten(child))
        except TypeError:
            flattened.append(flatten(child))
    return flattened


def seamless_tiling(pipeline):
    targets = [pipeline.vae, pipeline.text_encoder, pipeline.unet]

    if hasattr(pipeline, "text_encoder_2"):
        targets.append(pipeline.text_encoder_2)
    if pipeline.image_encoder is not None:
        targets.append(pipeline.image_encoder)

    layers = [
        layer
        for target in targets
        for layer in flatten(target)
        if isinstance(layer, (torch.nn.Conv2d, torch.nn.ConvTranspose2d))
    ]

    for layer in layers:
        layer.padding_mode = "circular"


def main(model_id="SG161222/RealVisXL_V4.0"):
    pipeline = AutoPipelineForImage2Image.from_pretrained(
        "stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float16, variant="fp16", use_safetensors=True
    )

    prompt = "A seamless pattern"
    pipeline.enable_model_cpu_offload()

    init_image = load_image('image.png')

    seamless_tiling(pipeline=pipeline)
    image = pipeline(
        prompt=prompt,
        image=init_image,
        width=1024,
        height=1024,
        num_inference_steps=40,
        guidance_scale=3,
        num_images_per_prompt=1,
    ).images[0]

    torch.cuda.empty_cache()
    image.save(f"image2image.png")

    tiled_imaged = tile_image_fuction(image, tile_width_repeat = 2, tile_height_repeat = 2)
    tiled_imaged.save(f"tiled_image.png")

    prompt = "A seamless pattern"
    pipeline.enable_model_cpu_offload()

    init_image = load_image('carpet_13_basecolor-1K.png')

    seamless_tiling(pipeline=pipeline)
    images = pipeline(
        prompt=prompt,
        image=init_image,
        width=1024,
        height=1024,
        num_inference_steps=40,
        guidance_scale=3,
        num_images_per_prompt=5,
    ).images

    for i, image in enumerate(images):
        torch.cuda.empty_cache()
        image.save(f"image_image_{i}.png")

        tiled_imaged = tile_image_fuction(image, tile_width_repeat = 2, tile_height_repeat = 2)
        tiled_imaged.save(f"tiled_image_{i}.png")

    embed()

if __name__ == "__main__":
    main()
