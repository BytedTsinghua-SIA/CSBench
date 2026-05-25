#!/usr/bin/env python3
"""
Model downloader for TinyChatEngine
Downloads and prepares LLaMA2-7B-chat models for edge deployment
"""

import os
import sys
import argparse
import urllib.request
import zipfile
import shutil
from pathlib import Path


class ModelDownloader:
    def __init__(self):
        self.models = {
            "LLaMA_7B_2_chat": {
                "QM_x86": {
                    "url": "https://example.com/models/llama2_7b_chat_qm_x86.zip",  # Placeholder URL
                    "size": "3.5GB",
                    "description": "LLaMA2 7B Chat model with x86 quantization (QM_x86)",
                },
                "QM_ARM": {
                    "url": "https://example.com/models/llama2_7b_chat_qm_arm.zip",  # Placeholder URL
                    "size": "3.5GB",
                    "description": "LLaMA2 7B Chat model with ARM quantization (QM_ARM)",
                },
            }
        }

    def download_file(self, url, destination, show_progress=True):
        """Download file with progress indicator"""
        try:
            print(f"Downloading from: {url}")
            print(f"Saving to: {destination}")

            with urllib.request.urlopen(url) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0

                with open(destination, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if show_progress and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            sys.stdout.write(
                                f"\rProgress: {progress:.1f}% ({downloaded}/{total_size} bytes)"
                            )
                            sys.stdout.flush()

            if show_progress:
                print()  # New line after progress
            print("Download completed successfully!")

        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
        return True

    def extract_zip(self, zip_path, extract_to):
        """Extract ZIP file"""
        try:
            print(f"Extracting {zip_path} to {extract_to}")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            print("Extraction completed successfully!")
            return True
        except Exception as e:
            print(f"Error extracting ZIP file: {e}")
            return False

    def download_model(self, model_name, quantization_method):
        """Download and setup model"""
        if model_name not in self.models:
            print(f"Error: Model '{model_name}' not found")
            print(f"Available models: {list(self.models.keys())}")
            return False

        model_info = self.models[model_name]
        if quantization_method not in model_info:
            print(
                f"Error: Quantization method '{quantization_method}' not supported for {model_name}"
            )
            print(f"Available methods: {list(model_info.keys())}")
            return False

        config = model_info[quantization_method]

        # Create INT4 directory if it doesn't exist
        int4_dir = Path("INT4")
        int4_dir.mkdir(exist_ok=True)

        # Model directory
        model_dir = int4_dir / "models" / f"{model_name}"
        model_dir.mkdir(parents=True, exist_ok=True)

        # Download destination
        zip_filename = f"{model_name}_{quantization_method}.zip"
        zip_path = int4_dir / zip_filename

        print(f"Model: {model_name}")
        print(f"Quantization: {quantization_method}")
        print(f"Description: {config['description']}")
        print(f"Size: {config['size']}")
        print()

        # Check if model already exists
        if (model_dir / "completed").exists():
            print("Model already downloaded and ready!")
            return True

        # Download model
        print("Starting download...")
        if not self.download_file(config["url"], zip_path):
            return False

        # Extract model
        print("Extracting model files...")
        if not self.extract_zip(zip_path, model_dir):
            return False

        # Create completion marker
        (model_dir / "completed").touch()

        # Cleanup
        if zip_path.exists():
            zip_path.unlink()
            print("Cleaned up temporary files")

        print(f"Model {model_name} with {quantization_method} quantization is ready!")
        print(f"Location: {model_dir.absolute()}")

        return True

    def list_available_models(self):
        """List all available models and quantization methods"""
        print("Available Models:")
        print("=" * 50)

        for model_name, quantizations in self.models.items():
            print(f"\nModel: {model_name}")
            for qm, config in quantizations.items():
                print(f"  {qm}:")
                print(f"    Description: {config['description']}")
                print(f"    Size: {config['size']}")
                print(f"    URL: {config['url']}")


def main():
    parser = argparse.ArgumentParser(
        description="Download LLaMA2 models for TinyChatEngine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download LLaMA2 7B Chat model for x86
  python download_model.py --model LLaMA_7B_2_chat --QM QM_x86

  # Download LLaMA2 7B Chat model for ARM
  python download_model.py --model LLaMA_7B_2_chat --QM QM_ARM

  # List all available models
  python download_model.py --list
        """,
    )

    parser.add_argument("--model", type=str, help="Model name to download")
    parser.add_argument("--QM", type=str, help="Quantization method (QM_x86 or QM_ARM)")
    parser.add_argument("--list", action="store_true", help="List all available models")

    args = parser.parse_args()

    downloader = ModelDownloader()

    if args.list:
        downloader.list_available_models()
        return

    if not args.model or not args.QM:
        parser.print_help()
        print("\nError: --model and --QM are required unless using --list")
        sys.exit(1)

    success = downloader.download_model(args.model, args.QM)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
