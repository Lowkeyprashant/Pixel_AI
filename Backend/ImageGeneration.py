import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
from time import sleep
import os

def open_images(prompt):
    folder_path = "data"  # Consistent folder name
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env','HuggingFaceAPIKey')}"}

async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

async def generate_images(prompt: str):
    folder_path = "data"
    os.makedirs(folder_path, exist_ok=True)  # Ensure directory exists
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra high details, high resolution, seed = {randint(0, 1000000)}",
        }
        tasks.append(asyncio.create_task(query(payload)))
        
    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        with open(os.path.join(folder_path, f"{prompt.replace(' ', '_')}{i+1}.jpg"), "wb") as f:
            f.write(image_bytes)

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r+") as f:
            data = f.read()
            prompt, status = data.split(",")

        if status.strip() == "True":
            print(f"Generating Images...{prompt}")
            GenerateImages(prompt=prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            break
        else:
            sleep(1)
    except Exception as e:
        print(f"Error: {e}")
        sleep(1)