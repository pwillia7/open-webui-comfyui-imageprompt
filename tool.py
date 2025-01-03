"""
title: Enhance Image
author: Patrick Williams
author_url: https://reticulated.net/
git_url: https://github.com/pwillia7/open-webui-comfyui-imageprompt
description: A toolkit that enhances an image by converting it to a base64 string and using it as a prompt for AI-based enhancement.
required_open_webui_version: 0.5.3
requirements: Pillow
version: 2.1
licence: MIT
"""

from pydantic import BaseModel
import base64
import urllib.request
from io import BytesIO
from PIL import Image
from fastapi import HTTPException, Request
from open_webui.routers.images import GenerateImageForm, image_generations


class User(BaseModel):
    id: str
    email: str
    name: str
    role: str


class Tools:
    def __init__(self):
        pass

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
                            "description": "A valid image URL starting with http:// or https://.",
                        }
                    },
                    "required": ["image_url"],
                },
            }
        ]

    async def enhance_image(
        self,
        image_url: str,
        __user__: dict,
        __request__: Request,
        __event_emitter__=None,
    ) -> str:
        """
        Enhance an image by converting it to a base64 string and using it as a prompt for AI-based enhancement.

        Parameters:
        - image_url (str): A valid URL pointing to the image (must start with http:// or https://).
        - __user__ (dict): User information for permissions and identity.
        - __request__ (Request): FastAPI request object, passed directly to the router.
        - __event_emitter__ (coroutine): Event emitter to pass statuses and messages to the front end.

        Returns:
        - str: Success message after the enhancement process.
        """
        try:
            # Convert __user__ into a Pydantic model
            user = User(**__user__)

            # Emit initial processing status
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Processing the image URL for enhancement...",
                            "done": False,
                        },
                    }
                )

            # Validate image URL
            if not image_url.startswith(("http://", "https://")):
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": "Error: Invalid URL provided.",
                                "done": True,
                            },
                        }
                    )
                return "Invalid URL. Please provide a valid image URL starting with http:// or https://."

            # Fetch the image from the URL
            with urllib.request.urlopen(image_url) as response:
                image_data = response.read()

            # Convert the image to base64
            pil_image = Image.open(BytesIO(image_data))
            buf = BytesIO()
            pil_image.save(buf, format="PNG")
            buf.seek(0)
            base64_encoded_image = base64.b64encode(buf.getvalue()).decode("utf-8")

            # Emit the received image status
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {
                            "content": f"**Original Image:** ![Original Image]({image_url})"
                        },
                    }
                )

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Image processed successfully. Enhancing the image...",
                            "done": False,
                        },
                    }
                )

            # Prepare form data for image generation
            form_data = GenerateImageForm(
                prompt=base64_encoded_image,
                n=3,  # Number of enhanced images to generate
            )

            # Call the image_generations function with the request, form_data, and user
            all_images = await image_generations(__request__, form_data, user)

            # Reorder and limit to the first three images
            reordered_images = [all_images[1], all_images[2], all_images[3]]

            # Emit the enhanced images in the new order
            for idx, image in enumerate(reordered_images, start=1):
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "message",
                            "data": {
                                "content": f"**Enhanced Image {idx}:** ![Enhanced Image]({image['url']})"
                            },
                        }
                    )

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Enhancement process completed.",
                            "done": True,
                        },
                    }
                )

            return "The image has been successfully enhanced. You should see the original and enhanced photos above."

        except Exception as exc:
            # Handle errors and notify the frontend
            error_message = f"An error occurred while enhancing the image: {exc}"
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": error_message, "done": True},
                    }
                )
            raise HTTPException(status_code=500, detail=error_message)
