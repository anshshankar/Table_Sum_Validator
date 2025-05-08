from mistralai import Mistral
import os
from pathlib import Path
from mistralai import DocumentURLChunk, ImageURLChunk, TextChunk
import json
import base64
from dotenv import load_dotenv
from helper import main as helper_main

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def ocr_processor(image_file_path):
    image_file = Path(image_file_path)
    assert image_file.is_file()

    encoded = base64.b64encode(image_file.read_bytes()).decode()
    base64_data_url = f"data:image/jpeg;base64,{encoded}"

    image_response = client.ocr.process(
        document=ImageURLChunk(image_url=base64_data_url),
        model="mistral-ocr-latest"
    )

    response_dict = json.loads(image_response.model_dump_json())
    image_ocr_markdown = image_response.pages[0].markdown

    print(response_dict)

    chat_response = client.chat.complete(
        model="pixtral-12b-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    ImageURLChunk(image_url=base64_data_url),
                    TextChunk(
                        text=(
                            f"This is image's OCR in markdown:\n\n{image_ocr_markdown}\n.\n"
                            "Convert this into a sensible structured json response. "
                            "The output should be strictly be json with no extra commentary"
                        )
                    ),
                ],
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    response_dict = json.loads(chat_response.choices[0].message.content)

    output_path = Path("output")
    output_ocr_file_name = image_file.stem + "_ocr.json"
    output_result_file_name = image_file.stem + "_result.json"
    output_ocr_file_path = output_path / output_ocr_file_name
    output_result_file_path = output_path / output_result_file_name

    with open(output_ocr_file_path, "w") as json_file:
        json.dump(response_dict, json_file, indent=4)

    helper_main(output_ocr_file_path,output_result_file_path)  

from multiprocessing import Process


ocr_processor("input\image.png")