# Enhance Image Tool

A powerful plugin for **Open-WebUI** that enhances images by converting them into base64 strings and using them as prompts for AI-based image enhancement. This tool seamlessly processes image URLs, enhances the images, and shares the final three enhanced photos in the chat interface.

## Features

- Converts an image from a URL into a base64-encoded PNG string.
- Uses the base64 string as a prompt to generate enhanced images.
- Displays only the last three enhanced images to avoid cluttering the interface.
- Provides real-time status updates during processing.
- Clearly signals the completion of the enhancement process.

## Requirements

- **Open-WebUI** version `0.4.3` or later.
- Python dependencies:
  - `Pillow` for image processing.

## Installation

1. Open the Open-WebUI **admin panel**.
2. Go to **Image Generation Settings**.
   - Paste in the `img2img` workflow.
   - Change the **prompt key** to `image` and the **prompt node** to `16`.
   - Save your changes.

3. Open the Open-WebUI **sidebar**, go to **Workspace**, then go to **Tools**:
   - Click the **plus** button to create a new tool.
   - Paste the `tool.py` code into the editor and save.

4. Go back to the **admin panel**, navigate to **Settings**, and then to **Models**:
   - Click on **Llama 3.2** and enable the new tool you created using the radio button.

5. Start a new chat. You should see a **yellow icon** above the chat box, indicating the tool is active. Your LLM can now use the new tool!
