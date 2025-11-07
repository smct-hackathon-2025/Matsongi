import json
from openai import OpenAI

def load_api_client(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        keys = json.load(f)
    client = OpenAI(api_key=keys["SOLAR_API_KEY"], base_url=keys["SOLAR_ENDPOINT"])
    return client


def solar_translate_kor_to_eng(client, korean_text):
    prompt = f"""
    Translate the following Korean food ingredient into natural English food ingredient name.
    Keep it concise and output only the English term.
    Korean: "{korean_text}"
    """
    response = client.chat.completions.create(
        model="solar-pro2",
        messages=[
            {"role": "system", "content": "You are a professional translator for Korean food ingredients."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def solar_match_candidate(client, ingredient_eng, candidates):
    prompt = f"""
    You are an expert ingredient normalizer for FlavorGraph.
    Choose the most semantically similar name among:
    {candidates}

    Input: "{ingredient_eng}"
    Output JSON only: {{"normalized_ingredient": "<best_match>"}}
    """
    response = client.chat.completions.create(
        model="solar-pro2",
        messages=[
            {"role": "system", "content": "Return one JSON only."},
            {"role": "user", "content": prompt},
        ],
    )
    result = response.choices[0].message.content.strip()
    try:
        parsed = json.loads(result)
        return parsed.get("normalized_ingredient", candidates[0])
    except:
        return candidates[0]
