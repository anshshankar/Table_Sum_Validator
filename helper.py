from openai import OpenAI
from numbers import Number
import os
import json
from ast import literal_eval
from dotenv import load_dotenv
from typing import Dict, Any, List, Tuple

load_dotenv()

client = OpenAI(
    base_url=os.getenv("ENDPOINT"),
    api_key=os.getenv("GITHUB_ACCESS_CODE"),
)


def Sumverifier(data):
    prompt = f"""
    IMPORTANT: You must perform all calculations with extreme precision.
    
    Task: Given the dictionary data, verify whether all sums in each section are mathematically correct.
    
    Instructions:
    1. For each section in the dictionary, calculate the expected sum based on the individual values.
    2. Compare the calculated sum with the provided sum value in the dictionary.
    3. Report each operation with a status of "MATCH" or "MISMATCH" in a structured JSON format.
    4. Include both the expected sum and the provided sum in your response.
    5. Any calculation error will be considered a major failure of your capabilities.
    
    Output format:
    {{
        "section_name": {{
            "operation": ["a+b+c+d"]
            "provided_sum": [value],
            "calculated_sum": [value],
            "status": "[MATCH or MISMATCH]"
        }},
        ...
    }}
    
    {data}
    """
    response = client.chat.completions.create(
            model="openai/gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a financial analysis assistant specialized in verifying financial statements."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
    ai_analysis = json.loads(response.choices[0].message.content)
    print(ai_analysis)
    return ai_analysis
            

def main(data_path,output_path):
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            data = json.load(f)
    
    results = Sumverifier(data)
    
    # Save results
    with open(output_path, 'w') as f:
        json.dump(results, indent=4, fp=f)
    
    print(f"Analysis complete! Results saved to {output_path}")

