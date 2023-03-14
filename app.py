import os
import glob
import contextlib
from PIL import Image
from dotenv import load_dotenv
from io import BytesIO
import openai
import requests
import uuid
import sys

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def create_result_directory(base_path) -> str:
    folder_name = str(uuid.uuid4())
    folder_path = os.path.join(base_path, folder_name)
    os.makedirs(folder_path)
    return folder_path


def request_and_save_images_from_open_ai(result_path: str, prompt: str):
    response = openai.Image.create(prompt=prompt, n=10, size="1024x1024")
    for image in response["data"]:
        image_url = image["url"]

        request = requests.get(image_url)
        image = Image.open(BytesIO(request.content))

        file_name = f"{uuid.uuid4()}.png"
        file_path = os.path.join(result_path, file_name)
        image.save(file_path)


def generate_gif(result_path: str):
    file_path_in = os.path.join(result_path, "*.png")
    file_path_out = os.path.join(result_path, "result.gif")

    with contextlib.ExitStack() as stack:
        imgs = (
            stack.enter_context(Image.open(file_path))
            for file_path in sorted(glob.glob(file_path_in))
        )

        img = next(imgs)

        img.save(
            fp=file_path_out,
            format="GIF",
            append_images=imgs,
            save_all=True,
            duration=800,
            loop=0,
        )


if __name__ == "__main__":
    base_path = sys.argv[1]
    prompt = sys.argv[2]

    result_path = create_result_directory(base_path)
    request_and_save_images_from_open_ai(result_path, prompt)
    generate_gif(result_path)
