import os 
from dotenv import load_dotenv
import requests
import json
from groq import Groq

load_dotenv()

client = Groq(api_key= os.getenv("GROQ_API_KEY_2"))

def target_link(data:str):
    try:
        clean_input = data[1:5000].rsplit('\n', 1)[0]
        llm_prompt = f"""
        You are a cybersecurity analyst. Analyze the following input and return a JSON object with this format:
        {{"summary": "<cybersecurity-related summary>" }}
        Only output JSON. Do not include explanations.

        INPUT DATA:
        {clean_input}
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



my_data = {
    "page_text": "Events\nResources\nBlogs\nMerchandise\nContact us\nSign in\nEmpowering Future Tech Leaders\n\nJoin our vibrant community of aspiring developers, innovators, and tech enthusiasts. We're dedicated to fostering growth, collaboration, and excellence in computer science.\n\nJoin the Society\nLearn More...",
    "script_sources": [
        "https://www.thecssknust.com/assets/index-BVllUoTA.js"
    ],
    "link_sources": [
        "https://www.thecssknust.com/apple-touch-icon.png",
        "https://www.thecssknust.com/favicon-32x32.png",
        "https://www.thecssknust.com/favicon-16x16.png",
        "https://www.thecssknust.com/site.webmanifest",
        "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap",
        "https://www.thecssknust.com/assets/index-C1S2Kc_l.css",
        "https://clickloom-scraper.onrender.com/docs"
    ]
}


def iterate_links(mydict: dict):
    new_list = []
    for key in ['script_sources', 'link_sources']:
        if key in mydict:
            new_list.extend(mydict[key])
    return new_list


def check_links(mylist: list):
    scraper_url = "https://clickloom-scraper.onrender.com/scrape"
    summaries = []
    for link in mylist:
        try:
            payload = {"url": link}
            response = requests.post(scraper_url, json=payload)
            response.raise_for_status()  # Raise error if not 200
            output = response.json()
            summarize_link = target_link(output["page_text"])
            summaries.append(summarize_link)
        except Exception as e:
            summaries.append(str(e)) 
    return summaries


def map_urls_to_summaries(urls, summaries):
    mapped_results = []
    for url, summary_dict in zip(urls, summaries):
        mapped_results.append({
            "url": url,
            "summary": summary_dict.get("summary", "No summary available")
        })
    return mapped_results


# all_links = iterate_links(my_data)
# results = check_links(all_links)


# from pprint import pprint
# pprint(map_urls_to_summaries(all_links, results))
