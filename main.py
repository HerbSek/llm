from fastapi import FastAPI, HTTPException 
import json 
import os 
from groq import Groq 
from dotenv import load_dotenv
import requests 

app=FastAPI(title = "LLM GROQ API")

load_dotenv()

client = Groq(api_key= os.getenv("GROQ_API_KEY"))

def llm(data):
    try:
        llm_prompt = f"""
        You are a web threat analysis engine.

        Analyze the following webpage data for signs of phishing, scams, malware, or suspicious intent. 
        Based on the input below, extract security-relevant insights and return a JSON object ONLY — no extra text.

        ---

        INPUT DATA:

        - Page Text:
        {data["page_text"]}

        - Script Sources:
        {data["script_sources"]}

        - Link Sources:
        {data["link_sources"]}

        ---

        Your task is to return a security report in the following **JSON format** in this bracket :(
  {{
        "verdict": "<Safe / Suspicious / Malicious>",
        "summary": "<A deep analyzed description/summary of what this page appears to be doing and checking how legit it is>",
        "recommendations": "<An advice on what the user should do or what you will recommend the user do>",
        "page_text_findings": {{
            "suspicious_phrases": ["<list any suspicious phrases or keywords>"],
            "phishing_indicators": <true/false>
        }},
        "script_analysis": {{
            "total_scripts": <number>,
            "external_scripts": <number>,
            "suspicious_domains": ["<list domains if any>"],
            "minified_or_encoded": <true/false>
        }},
        "link_analysis": {{
            "total_links": <number>,
            "external_links": <number>,
            "redirect_services_used": ["<bit.ly>", "<t.co>", ...],
            "phishing_like_links": ["<list if any links mimic legitimate services>"]
        }},
        "risk_score": <float score between 0 and 10>,
        }} )

        Strict rules:
        - If no suspicious signs are found, fields should return empty lists or false, not null.
        - Only return valid JSON — do NOT include markdown and nothing to enclose the output with like ''' or ```
        """

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": llm_prompt}],
            model="llama-3.3-70b-versatile",
        )

        output_f = chat_completion.choices[0].message.content.strip()

        try:
            return json.loads(output_f)
        except json.JSONDecodeError as je:
            return {"error": f"JSON parsing failed: {je}", "raw": output_f}
        except KeyError as ke:
            return {"error": f"Network Problems. Try again later "}

    except Exception as e:
        return {"error": f"LLM call failed: {e}"}


def function_scrape(url,payload):
    request = requests.get(url = url , params = payload)
    my_request = request.json()
    return my_request

def function_scrape_post(url, payload):
    response = requests.post(url=url, json=payload)
    return response.json()
# ////////////////////////////////////////////

@app.get("/healthy")
async def function():
    return {"message": "App is healthy"}


@app.post("/call_llm")
async def get_llm(data:dict):
    my_data = llm(data)
    if not my_data:
        raise HTTPException(status_code = 404, detail="No data found")
    return my_data

@app.get("/results")
async def llm_scraper(link:str):
    url = "https://apexherbert200-clickloom-scraper-2.hf.space/scrape" 
    payload = {"url": link}
    try:
        my_scrape = function_scrape_post(url,payload)  # In case we pivot to hugging face, then we add screenshot and from here we work with the data structure 
    except Exception as ee:
        return {"msg": f"Unable to call : {ee}"}
    try:
        output = llm(my_scrape)
        return output
    except Exception as e:
        raise HTTPException(404, "Unable to provide request at this time")

     





