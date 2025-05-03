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
    Given Dict, verify weather all sums in the section are correct are not. Return all operation with status matched or not in json format
    {data}
    """
    response = client.chat.completions.create(
            model="openai/gpt-4o",
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

