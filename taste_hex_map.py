# taste_hex_map.py
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Dict, Tuple, List

DEFAULT_SCORE = 3.0
TASTE_AXES: List[Tuple[str, Tuple[str, ...]]] = [
    ("🌶️ 매운맛", ("capsaicin", "pepper", "garlic_onion")),
    ("🍋 신맛", ("sourness")),
    ("🍭 단맛", ("sugar", "sweetener")),
    ("🧂 짠맛", ("overall_saltiness")),
    ("🧈 고소함", ("nuttiness", "richness")),
    ("☕ 쓴맛", ("bitterness")),
]

def load_korean_font():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(base_dir, "font")
    font_prop = fm.FontProperties(fname=os.path.join(font_dir, "NanumGothic.ttf"))
    bold_font_prop = fm.FontProperties(fname=os.path.join(font_dir, "NanumGothicBold.ttf"))
    plt.rcParams["font.family"] = font_prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False
    return font_prop, bold_font_prop

def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _flatten_preferences(source: Dict) -> Dict[str, float]:
    if not source:
        return {}
    if "taste_preferences" in source:
        source = source["taste_preferences"]
    flat = {}
    for key, value in source.items():
        if isinstance(value, dict):
            flat.update({k: v for k, v in value.items() if isinstance(v, (int, float))})
        elif isinstance(value, (int, float)):
            flat[key] = value
    return flat

def _axis_average(flat_pref: Dict[str, float], aliases: Tuple[str, ...]) -> float:
    values = [flat_pref[k] for k in aliases if k in flat_pref]
    if not values:
        return DEFAULT_SCORE
    return float(np.clip(np.mean(values), 1, 5))

def plot_user_taste_hexagon(pref_source: Dict,
                            font_prop,
                            bold_font_prop,
                            output_path: str | None = None):
    flat_pref = _flatten_preferences(pref_source)
    labels = [label for label, _ in TASTE_AXES]
    scores = [_axis_average(flat_pref, aliases) for _, aliases in TASTE_AXES]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    score_cycle = scores + scores[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
    ax.plot(angles, score_cycle, color="#fe9600", linewidth=2.5)
    ax.fill(angles, score_cycle, color="#fe9600", alpha=0.25)
    ax.set_ylim(0, 5)
    ax.set_yticks(range(1, 6))
    ax.set_yticklabels([str(v) for v in range(1, 6)], fontproperties=font_prop, fontsize=10)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontproperties=bold_font_prop, fontsize=12)

    for angle, score in zip(angles[:-1], scores):
        ax.text(angle, score + 0.25, f"{score:.1f}",
                ha="center", va="center",
                fontproperties=font_prop, fontsize=10, color="#1c2445")

    ax.set_title("나의 입맛 HEXACO 프로필", fontproperties=bold_font_prop, fontsize=16, pad=20)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
    return fig, dict(zip(labels, scores))

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "./data")
    output_dir = os.path.join(base_dir, "./data/user")

    user_vector = load_json(os.path.join(data_dir, "./user/user_taste_vector.json"))
    user_id = user_vector["user_id"]
    survey_path = os.path.join(data_dir, "user", f"{user_id}_survey.json")
    map_output_path = os.path.join(output_dir, f"{user_id}_taste_hex.png")

    font_prop, bold_font_prop = load_korean_font()
    survey = load_json(survey_path)

    fig, axis_scores = plot_user_taste_hexagon(survey, font_prop, bold_font_prop, map_output_path)
    print("✅ 축별 점수:", axis_scores)