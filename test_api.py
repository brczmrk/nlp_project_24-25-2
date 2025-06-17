import requests
import sys
import os
from pathlib import Path

API_BASE_URL = "http://localhost:8000"


def test_image_analysis(image_paths):
    print(f"\nTesting image analysis with {len(image_paths)} images...")

    files = []
    for path in image_paths:
        if os.path.exists(path):
            files.append(
                ("images", (os.path.basename(path), open(path, "rb"), "image/jpeg"))
            )
        else:
            print(f"File not found: {path}")

    if not files:
        print("No valid image files to test.")
        return

    try:
        response = requests.post(f"{API_BASE_URL}/analyze", files=files)

        for _, file in files:
            file[1].close()

        if response.status_code == 200:
            result = response.json()
            print("Image analysis successful. Report:")
            print(result.get("report", "No report found in response."))
            report_file = Path("image_analysis_report.md")
            with report_file.open("w") as f:
                f.write(result.get("report", "No report found in response."))
            return True
        else:
            print(f"Failed to analyze images. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while testing image analysis: {e}")

    return False


def main():
    print("Starting image analysis tests...")

    print("Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("Health check passed.")
            print(response.json())
        else:
            print(f"Health check failed. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during health check: {e}")

    test_images = []
    dataset_path = Path("./dataset/158220")
    if dataset_path.exists():
        test_images = list(dataset_path.glob("*.jpg"))

    if not test_images:
        print("No test images found in the dataset directory.")
        return

    print(f"Found {len(test_images)} images in the dataset directory.")

    success = test_image_analysis(test_images)
    if success:
        print("All tests passed successfully.")
    else:
        print("Some tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
