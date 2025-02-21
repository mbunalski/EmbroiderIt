
char_mapping = {
    "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
    "6": "six", "7": "seven", "8": "eight", "9": "nine",
    "A": "a", "B": "b", "C": "c", "D": "d", "E": "e", "F": "f", "G": "g", "H": "h", "I": "i",
    "J": "j", "K": "k", "L": "l", "M": "m", "N": "n", "O": "o", "P": "p", "Q": "q", "R": "r",
    "S": "s", "T": "t", "U": "u", "V": "v", "W": "w", "X": "x", "Y": "y", "Z": "z"
}

def split_pdf(input_pdf):
    """Splits a 35-page PDF into individual files with formatted names."""
    doc = fitz.open(input_pdf)

    # Ensure the PDF has exactly 36 pages
    if len(doc) != 35:
        raise ValueError("Expected a 35-page PDF but found {}".format(len(doc)))

    # Iterate through pages and save individually
    for i, char in enumerate(list(char_mapping.values())):
        output_filename = f"{char}_floral.pdf"
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=i, to_page=i)
        new_doc.save(output_filename)
        new_doc.close()
        print(f"Saved: {output_filename}")

    doc.close()
def upload_to_s3(file_path, s3_key):
    """Uploads a file to S3."""
    try:
        s3.upload_file(file_path, S3_BUCKET, "temp/" +s3_key)
        return True
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False
from pathlib import Path

from flask import Flask, request, jsonify
import os
import fitz  # PyMuPDF
import math
import json
from datetime import datetime
import boto3
from flask_cors import CORS, cross_origin
from io import BytesIO
import fitz  # PyMuPDF
from PIL import Image
import os

app = Flask(__name__)
CORS(app, support_credentials=True)
USER_COUNT_FILE = "user_counts.json"

# AWS S3 Config
S3_BUCKET = "embroiderit"
S3_REGION = "us-east-1"

s3 = boto3.client("s3")

def open_pdf_from_s3(s3_key):
    """Fetch PDF from S3 and open it in PyMuPDF without local storage."""
    try:
        # Download file into memory
        response = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        pdf_data = response["Body"].read()

        # Load PDF from memory (BytesIO)
        pdf_document = fitz.open("pdf", BytesIO(pdf_data))
        return pdf_document

    except Exception as e:
        print(f"Error opening PDF from S3: {e}")
        return None
def save_pdf_to_s3(pdf_document, s3_key):
    """Saves a PyMuPDF document object to S3 directly."""
    try:
        # Create an in-memory byte stream
        pdf_bytes = BytesIO()

        # Save the modified PDF into the byte stream
        pdf_document.save(pdf_bytes)

        # Reset stream position to the beginning
        pdf_bytes.seek(0)

        # Upload to S3
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=pdf_bytes.getvalue(), ContentType="application/pdf")

        return True

    except Exception as e:
        print(f"Error saving PDF to S3: {e}")
        return False
def generate_presigned_url(s3_key, expiration=300):
    """Generates a pre-signed URL valid for 5 minutes."""
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_key},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None
def get_monthly_count(username):
    current_month = datetime.now().strftime("%Y-%m")
    counts = {}
    if os.path.exists(USER_COUNT_FILE):
        with open(USER_COUNT_FILE, "r") as f:
            counts = json.load(f)
    user_key = f"{username}_{current_month}"
    counts[user_key] = counts.get(user_key, 0) + 1
    with open(USER_COUNT_FILE, "w") as f:
        json.dump(counts, f)
    return counts[user_key]
def create_collage_from_chars(username, characters, font_group, size):
    files = [f"source/{font_group.lower()}/{char}_{font_group.lower()}.pdf" for char in characters]
    monthly_count = get_monthly_count(username)
    output_pdf = f"temp_{username}_{monthly_count}.pdf"
    sample_doc = open_pdf_from_s3(files[0])
    sample_page = sample_doc[0]
    new_doc = fitz.open()
    new_page = new_doc.new_page(width=sample_page.rect.width, height=sample_page.rect.height)
    num_chars = len(files)
    cols = math.ceil(math.sqrt(num_chars))
    rows = math.ceil(num_chars / cols)
    scale_x = (sample_page.rect.width / cols) * float(size)
    scale_y = (sample_page.rect.height / rows) * float(size)
    for i, file in enumerate(files):
        row, col = divmod(i, cols)
        x0, y0 = col * scale_x, row * scale_y
        x1, y1 = x0 + scale_x, y0 + scale_y
        char_doc = open_pdf_from_s3(file)
        new_page.show_pdf_page(fitz.Rect(x0, y0, x1, y1), char_doc, 0)
    save_pdf_to_s3(new_doc, "temp/" + output_pdf)
    return output_pdf

import fitz  # PyMuPDF
from PIL import Image
import os

def convert_pdfs_to_pngs(input_folder, output_folder):
    """
    Converts all PDFs in the input folder to PNG images and saves them in the output folder.
    Each PDF page is converted to an identically named PNG file.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".pdf", ".png"))

            # Open PDF
            pdf_document = fitz.open(pdf_path)
            for page_num in range(len(pdf_document)):
                pix = pdf_document[page_num].get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(output_path, "PNG")

            print(f"Converted: {filename} -> {output_path}")

from PIL import Image
import os
import numpy as np

def trim_whitespace(input_folder, output_folder, buffer=50):
    """
    Trims excess white space from images in a folder while keeping a buffer.

    :param input_folder: Path to the folder containing images.
    :param output_folder: Path to save the trimmed images.
    :param buffer: Extra pixels to keep as border.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path).convert("RGBA")

            # Convert image to numpy array
            img_array = np.asarray(img)

            # Find all non-white pixels (assuming white is (255,255,255,255))
            non_white_pixels = np.where(img_array[:, :, :3] < 250)  # Ignore near-white pixels
            if non_white_pixels[0].size == 0 or non_white_pixels[1].size == 0:
                print(f"Skipping {filename}: No non-white content found.")
                continue

            # Get bounding box of non-white content
            y_min, y_max = non_white_pixels[0].min(), non_white_pixels[0].max()
            x_min, x_max = non_white_pixels[1].min(), non_white_pixels[1].max()

            # Apply buffer (ensure it doesn't go out of bounds)
            y_min = max(y_min - buffer, 0)
            y_max = min(y_max + buffer, img.height)
            x_min = max(x_min - buffer, 0)
            x_max = min(x_max + buffer, img.width)

            # Crop and save
            cropped_img = img.crop((x_min, y_min, x_max, y_max))
            output_path = os.path.join(output_folder, filename)
            cropped_img.save(output_path)

            print(f"Trimmed and saved: {output_path}")




@app.route("/generate-collage", methods=["POST"])
def generate_collage():
    data = request.get_json()
    username = data.get("username")
    characters = data.get("characters")
    font_group = data.get("fontGroup")
    size = data.get("size", 1.0)
    if not username or not characters or not font_group:
        return jsonify({"error": "Missing required parameters."}), 400
    output_pdf = create_collage_from_chars(username, characters, font_group, size)
    return jsonify({"download_url": generate_presigned_url("temp/" + output_pdf, expiration=3000)})

if __name__ == "__main__":
    # Example Usage
    # convert_pdfs_to_pngs("../source/old_floral", "../source/floral")
    trim_whitespace("../source/emblem", "../source/output")
    exit()
    app.run(debug=True)