from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from openai import OpenAI
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


# OpenAI configuration
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    return OpenAI(api_key=api_key)


# Initialize OpenAI client
client = None
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def encode_image_from_file_object(file_object):
    file_object.seek(0)  # Reset file pointer to the beginning
    return base64.b64encode(file_object.read()).decode("utf-8")


def analyze_image(file_object):
    global client
    if client is None:
        client = get_openai_client()

    image_data = encode_image_from_file_object(file_object)

    query = """
    Analyze the provided image and describe the main object in detail.
    Identify the object, its attributes, and any text or numbers present.
    Highlight all visible aspects, focus on possible faults or damages, and provide a comprehensive description.
    If the object is a vehicle, tool, phone, machine, or any other item, try to identify its type, brand and model.
    If the object is a property, apartment or house, describe its features and any visible details.
    If the object is a document or a paper read and summarize the text, highlighting its important details.
    Ignore the background and focus solely on the main object.
    Ensure the description is comprehensive and detailed, covering all visible aspects of the object.
    """

    messages = [
        {
            "role": "system",
            "content": "You are an expert in image analysis and object recognition.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": query,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
            ],
        },
    ]

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


def aggregate_descriptions(descriptions):
    global client
    if client is None:
        client = get_openai_client()

    combined_descriptions = "\n\n---\n\n".join(
        [f"Description {i+1}:\n{desc}" for i, desc in enumerate(descriptions)]
    )

    query = f"""
    You are given multiple detailed descriptions of different parts and components of the same object.
    Please aggregate these descriptions into a comprehensive, well-organized summary report.

    Follow the schema format below. For each heading, create concise bullet points with only essential information (1-5 words per bullet point). Use specific field names where applicable and focus on factual details only.

    ### Identification & General Data
    Include identification details such as brand, model, type, manufacturer, year, registration information, technical specifications, mileage and any visible text or numbers from the descriptions.

    ### Condition Assessment
    Summarize the overall condition. Include details on any visible faults, damages or issues, and the general state of the object based on the descriptions provided.

    ### Documentation & Accessories
    List any documentation (registration certificates, technical data sheets, service books), accessories, keys, and inspection materials mentioned in the descriptions. Specify what is present, missing, or not visible.

    Instructions:
    - Keep each bullet point to 1-5 words maximum
    - Use consistent field names (e.g. **Asset:**, **Manufacturer:**, **Model:**)
    - Write "Not mentioned" or "Not visible" for any missing or unavailable information
    - Focus on factual details only, no subjective opinions or interpretations
    - Ensure the report is well-organized and easy to read
    - Only extend the headings from the schema, do not create new headings or sections

    Here are the descriptions:

    {combined_descriptions}
    """

    messages = [
        {
            "role": "system",
            "content": "You are an expert in object inspection and documentation who can synthesize multiple detailed observations into comprehensive reports.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": query,
                },
            ],
        },
    ]

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            max_tokens=1500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error aggregating descriptions: {str(e)}"


def process_images(file_objects):
    individual_descriptions = []

    for file_object, filename in file_objects:
        try:
            description = analyze_image(file_object)
            individual_descriptions.append(description)
        except Exception as e:
            individual_descriptions.append(f"Error processing {filename}: {str(e)}")

    aggregated_report = aggregate_descriptions(individual_descriptions)
    return aggregated_report


@app.route("/analyze", methods=["POST"])
def analyze_images():
    try:
        if "images" not in request.files:
            return jsonify({"error": "No images provided"}), 400
        files = request.files.getlist("images")
        if not files or files[0].filename == "":
            return jsonify({"error": "No images provided"}), 400

        file_objects_with_names = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_objects_with_names.append((file, filename))

        if not file_objects_with_names:
            return jsonify({"error": "No valid images provided"}), 400

        aggregated_report = process_images(file_objects_with_names)

        return jsonify({"report": aggregated_report})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return (
        jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}),
        200,
    )


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() in ["true", "1", "yes"]
    app.run(host="0.0.0.0", port=port, debug=debug)
