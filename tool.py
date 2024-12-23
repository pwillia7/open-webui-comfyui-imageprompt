"""
title: Enhance Image
author: Patrick Williams
author_url: https://reticulated.net
git_url: https://github.com/pwillia7/open-webui-comfyui-imageprompt.git
description: A tool that enhances an image by converting it to a base64 string and using it as a prompt in a ComfyUI Workflow. Requires use of workflow loading image via base64 node https://github.com/glowcone/comfyui-base64-to-image and setting the prompt in Open-webui Image Generation settings to this node AND relabeling the input to images.
required_open_webui_version: 0.4.3
requirements: Pillow
version: 1.3
licence: MIT
"""

from pydantic import BaseModel, Field
import base64
import urllib.request
from io import BytesIO
from PIL import Image
from apps.images.main import image_generations, GenerateImageForm
from apps.webui.models.users import Users

class Tools:
    class Valves(BaseModel):
        pass

    class UserValves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    def tools(self):
        return [
            {
                "name": "enhance_image",
                "description": "Enhance an image from a URL by processing it and generating an enhanced version.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "A valid image URL starting with http:// or https://."
                        }
                    },
                    "required": ["image_url"]
                },
            }
        ]

    async def enhance_image(
        self, image_url: str, __user__: dict, __event_emitter__=None
    ) -> str:
        """
        Enhance an image by converting it to a base64 string and using it as a prompt for AI-based enhancement.

        Parameters:
        - image_url (str): A valid URL pointing to the image (must start with http:// or https://).
        - __user__ (dict): User information for permissions and identity.
        - __event_emitter__ (coroutine): Event emitter to pass statuses and messages to the front end.

        Returns:
        - str: Notify the user of the outcome.
        """
        try:
            # Emit a starting status
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Processing the image URL for enhancement...", "done": False},
                    }
                )

            # Validate the URL
            if not image_url.startswith(("http://", "https://")):
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "Error: Invalid URL provided.", "done": True},
                        }
                    )
                return "Error: Invalid URL provided."

            # Fetch and encode the image as Base64
            with urllib.request.urlopen(image_url) as response:
                image_data = response.read()

            pil_image = Image.open(BytesIO(image_data))
            buf = BytesIO()
            pil_image.save(buf, format="PNG")
            buf.seek(0)
            base64_encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")

            # Emit a status indicating the base64 string is ready
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Image processed successfully. Enhancing the image...", "done": False},
                    }
                )

            # Use the Base64 string as the prompt for image enhancement
            images = await image_generations(
                GenerateImageForm(**{"prompt": base64_encoded_image}),
                Users.get_user_by_id(__user__["id"]),
            )

            # Limit the output to the last three images
            final_images = images[-3:]

            # Emit the final three generated images as messages
            for image in final_images:
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "message",
                            "data": {"content": f"![Enhanced Image]({image['url']})"},
                        }
                    )

            # Emit a final summary message
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {"content": "Here are your enhanced photos! This concludes the enhancement process."},
                    }
                )

            # Emit a final "done" status to explicitly mark the process as complete
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Enhancement process completed.", "done": True},
                    }
                )

            return ""

        except Exception as e:
            # Emit an error message and status
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"An error occurred: {e}", "done": True},
                    }
                )
            return f"An error occurred: {e}"
