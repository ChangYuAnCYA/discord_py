import torch, logging
## disable warnings
logging.disable(logging.WARNING)  
## Imaging  library
from PIL import Image
from torchvision import transforms as tfms
## Basic libraries
import numpy as np
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
#%matplotlib inline
from IPython.display import display
import shutil
import os
## For video display
from IPython.display import HTML
from base64 import b64encode
 
## Import the CLIP artifacts 
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers import AutoencoderKL, UNet2DConditionModel, LMSDiscreteScheduler
from torchvision.utils import save_image

class Diffusion():
    def __init__(self):
        ## Initiating tokenizer and encoder.
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14", torch_dtype=torch.float16)
        self.text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-large-patch14", torch_dtype=torch.float16).to("cuda")
        ## Initiating the VAE
        self.vae = AutoencoderKL.from_pretrained("runwayml/stable-diffusion-v1-5", subfolder="vae", torch_dtype=torch.float16).to("cuda")
        ## Initializing a scheduler and Setting number of sampling steps
        self.scheduler = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear", num_train_timesteps=1000)
        self.scheduler.set_timesteps(50)
        ## Initializing the U-Net model
        self.unet = UNet2DConditionModel.from_pretrained("runwayml/stable-diffusion-v1-5", subfolder="unet", torch_dtype=torch.float16).to("cuda")

    def load_image(self, p):
        '''
        Function to load images from a defined path
        '''
        return Image.open(p).convert('RGB').resize((512,512))
    def pil_to_latents(self, image):
        '''
        Function to convert image to latents
        '''
        init_image = tfms.ToTensor()(image).unsqueeze(0) * 2.0 - 1.0
        init_image = init_image.to(device="cuda", dtype=torch.float16) 
        init_latent_dist = self.vae.encode(init_image).latent_dist.sample() * 0.18215

        return init_latent_dist

    def latents_to_pil(self, latents):
        '''
        Function to convert latents to images
        '''
        latents = (1 / 0.18215) * latents
        with torch.no_grad():
            image = self.vae.decode(latents).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.detach().cpu().permute(0, 2, 3, 1).numpy()
        images = (image * 255).round().astype("uint8")
        pil_images = [Image.fromarray(image) for image in images]

        return pil_images

    def text_enc(self, prompts, maxlen=None):
        '''
        A function to take a texual promt and convert it into embeddings
        '''
        if maxlen is None: maxlen = self.tokenizer.model_max_length
        inp = self.tokenizer(prompts, padding="max_length", max_length=maxlen, truncation=True, return_tensors="pt")

        return self.text_encoder(inp.input_ids.to("cuda"))[0].half()

    def prompt_2_img(self, prompts, g=7.5, seed=100, steps=70, dim=512, save_int=False):
        """
        Diffusion process to convert prompt to image
        """
        
        # Defining batch size
        bs = len(prompts) 
        
        # Converting textual prompts to embedding
        text = self.text_enc(prompts) 
        
        # Adding an unconditional prompt , helps in the generation process
        uncond =  self.text_enc([""] * bs, text.shape[1])
        emb = torch.cat([uncond, text])
        
        # Setting the seed
        #if seed:
        #    torch.manual_seed(seed)
        
        # Initiating random noise
        latents = torch.randn((bs, self.unet.in_channels, dim//8, dim//8))
        
        # Setting number of steps in scheduler
        self.scheduler.set_timesteps(steps)
        
        # Adding noise to the latents 
        latents = latents.to("cuda").half() * self.scheduler.init_noise_sigma
        
        # Iterating through defined steps
        for i, ts in enumerate(self.scheduler.timesteps):
            # We need to scale the i/p latents to match the variance
            inp = self.scheduler.scale_model_input(torch.cat([latents] * 2), ts)
            
            # Predicting noise residual using U-Net
            with torch.no_grad():
                # print(inp.shape)
                # print(emb.shape)
                # print(emb.shape)
                u, t = self.unet(inp, ts, encoder_hidden_states=emb).sample.chunk(2)
                
            # Performing Guidance
            pred = u + g*(t-u)
            
            # Conditioning  the latents
            latents = self.scheduler.step(pred, ts, latents).prev_sample
            
            # Saving intermediate images
            if save_int: 
                if not os.path.exists(f'./steps'):
                    os.mkdir(f'./steps')
                self.latents_to_pil(latents)[0].save(f'steps/{i:04}.jpeg')
                
        # Returning the latent representation to output an image of 3x512x512
        return self.latents_to_pil(latents)

    def run(self, prompt):
        image = self.prompt_2_img([prompt], save_int=False)
        
        return image[0]