import os
import openai
import requests
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from config import OPENAI_API_KEY


class OpenAIImageGenerator:
    def __init__(self, api_key, output_dir="generated_images", image_size="1024x1024"):
        """
        Initialize the OpenAIImageGenerator with API key, output directory, and image size.
        """
        self.api_key = api_key
        self.output_dir = output_dir
        self.image_size = image_size
        openai.api_key = self.api_key

    def generate_images(self, prompt, num_images):
        """
        Generates images based on the given prompt and saves them to the output directory.

        :param prompt: The prompt to generate images.
        :param num_images: Number of images to generate.
        """
        self._ensure_output_dir()

        """
        client = OpenAI(
            # This is the default and can be omitted
            api_key=api_key,
        )

        response = client.images.generate(prompt=prompt)
        """
        
        for i in range(num_images):
            print(f"Generating image {i + 1} of {num_images}...")
            response = openai.images.generate(prompt=prompt, n=1, size=self.image_size)
            image_url = response.data[0].url

            self._save_image(image_url, f"image_{i + 1}.png")

    def _ensure_output_dir(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _save_image(self, url, filename):
        """Download and save an image from the given URL."""
        response = requests.get(url)
        image_path = os.path.join(self.output_dir, filename)
        with open(image_path, "wb") as f:
            f.write(response.content)
        print(f"Image saved to {image_path}")


class TestOpenAIImageGenerator(unittest.TestCase):
    @patch("openai.Image.create")
    @patch("requests.get")
    def test_generate_images(self, mock_requests_get, mock_openai_image_create):
        # Mock OpenAI response
        mock_openai_image_create.return_value = {
            "data": [{"url": "http://example.com/fake_image.png"}]
        }

        # Mock requests response
        mock_requests_get.return_value = MagicMock(content=BytesIO(b"fake_image_data").read())

        # Instantiate the generator
        api_key = "fake_api_key"
        output_dir = "test_images"
        generator = OpenAIImageGenerator(api_key, output_dir)

        # Generate images
        generator.generate_images(prompt="Test prompt", num_images=2)

        # Assertions
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "image_1.png")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "image_2.png")))

        # Cleanup test artifacts
        for filename in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, filename))
        os.rmdir(output_dir)

        # Ensure the OpenAI API and requests were called correctly
        self.assertEqual(mock_openai_image_create.call_count, 2)
        self.assertEqual(mock_requests_get.call_count, 2)


def main():
    api_key = "fake_api_key"
    output_dir = "test_images"
    generator = OpenAIImageGenerator(OPENAI_API_KEY, output_dir)

    # Generate images
    generator.generate_images(prompt="Test prompt", num_images=2)


if __name__ == "__main__":
    main()
    #unittest.main()
