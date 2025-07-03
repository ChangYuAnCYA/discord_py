from huggingface_hub import model_info
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, DiffusionPipeline, EulerAncestralDiscreteScheduler, DPMSolverSDEScheduler
from os.path import dirname
import time
import numpy as np
from PIL import Image

class Anything():
    def __init__(self):  
        self.model_path = "AnythingV5Ink_ink"
        self.model_path = "cuteyukimixAdorable_specialchapter"

        self.pipe_no_lora = StableDiffusionPipeline.from_single_file(f"./model/base_model/{self.model_path}.safetensors", 
                                                        torch_dtype=torch.float16, 
                                                        use_safetensors=True, 
                                                        safety_checker=None, 
                                                        requires_safety_checker=False).to("cuda")

        self.pipe_no_lora.scheduler = EulerAncestralDiscreteScheduler.from_config(self.pipe_no_lora.scheduler.config)
        self.pipe_no_lora.safety_checker = None
        self.pipe_no_lora.requires_safety_checker = False
        self.pipe_no_lora.set_progress_bar_config(disable=True)

        self.generator = torch.Generator("cuda").manual_seed(int(time.time()))

    def run(self, p, np, step, scale, height, width):
        prompt = "(masterpiece)," + p
        num_inference_steps = step
        guidance_scale = scale
        negative_prompt = "(worst quality),(low quality),normal quality,watermark,text,error,blurry,signature,artist name,lipstick, bad anatomy,EasyNegative,tattoo,text,colored skin,red pupils"
        hand = "(bad arms),(missing arms),(crossed arms),(arm arm support),(bad hands),(missing fingers),(worst hands),(Extra fingers),(strange fingers)"
        feet = "(three crus),(extra crus),(fused crus),(crossed legs),(bad feet:1.3),(fused feet),(worst feet),(three legs),(missing legs),(fused thigh),(three thigh),(fused thigh),(extra thigh),(worst thigh)"
        negative_prompt = negative_prompt + hand + feet + np
        image = self.pipe_no_lora(prompt=prompt, 
                            negative_prompt=negative_prompt, 
                            num_inference_steps=num_inference_steps, 
                            guidance_scale=guidance_scale, 
                            generator=self.generator, 
                            height=height, width=width).images[0]
        
        return image