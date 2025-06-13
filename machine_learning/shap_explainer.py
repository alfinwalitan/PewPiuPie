import os
import shap
import joblib
import pandas as pd
from .classifier import classify_res, load_rf_model

rf_model = load_rf_model()
features_map = {
    "designation_score" : "Designation Similarity",
    "skill_score" : "Skill Similarity",
    "skill_match_ratio" : "Skill Match Ratio",
    "degree_score" : "Degree Similarity",
    "exp_match" : "Experience Match",
    "total_exp" : "Years of Experience"
}
class_labels = rf_model.classes_.tolist()

def shap_explain(features, model = rf_model):
    explainer = shap.TreeExplainer(model)
    df = pd.DataFrame([features])
    shap_values = explainer.shap_values(df)
    return shap_values

def format_list_with_and(items):
    if not items:
        return ""
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        return f"{', '.join(items[:-1])}, and {items[-1]}"

def summary_text(features):
    shap_val = shap_explain(features)[0]  # shape: (num_features, num_classes)
    features_name = list(features.keys())
    predicted_class = classify_res(features)

    # Always explain against a positive class
    target_class = "Highly Suitable"
    class_index = class_labels.index(target_class)

    # Pair each feature with its SHAP impact
    impacts = []
    for i, feature in enumerate(features_name):
        value = shap_val[i][class_index]
        readable_name = features_map[feature]
        impacts.append((readable_name, value))

    # Sort by impact
    positive = sorted([(f, v) for f, v in impacts if v > 0], key=lambda x: x[1], reverse=True)
    negative = sorted([(f, v) for f, v in impacts if v < 0], key=lambda x: x[1])

    summary = f"The model classify this candidate as **{predicted_class}/*."

    # Add positive contributors
    if positive:
        pos_factors = [f"%%{name}/% (##impact score: {abs(val):.2f}/#)" for name, val in positive[:]]
        joined_pos = format_list_with_and(pos_factors)
        summary += f" The {joined_pos} contribute positively to the candidate’s suitability."

    # Add negative contributors
    if negative:
        neg_factors = [f"%%{name}/% (##impact score: {abs(val):.2f}/#)" for name, val in negative[:]]
        joined_neg = format_list_with_and(neg_factors)
        summary += f" {'However' if positive else 'Because'}, the {joined_neg} reduced the candidate's suitability."

    return summary