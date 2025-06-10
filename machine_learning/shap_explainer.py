import os
import shap
import joblib
import pandas as pd
from .classifier import classify_res

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rf_model_path = os.path.join(BASE_DIR, "models", "random_forest", "random_forest_model_97.pkl")
rf_model = joblib.load(rf_model_path)
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

def shap_summary(features):
    shap_val = shap_explain(features)[0]
    features_name = list(features.keys())
    summary_list = []
    for class_index, class_name in enumerate(class_labels):
        summary_item = {
            "class_name" : f"SHAP Summary for Class: {class_name}",
            "feature_item": []
        }
        for feature in range(len(features_name)):
            value = shap_val[feature][class_index]
            direction = "decreases" if value < 0 else "increases"
            symbol = "-" if value < 0 else "+"
            feature_text = f"{symbol} Feature '{features_map[features_name[feature]]}' {direction} the likelihood of '{class_name}' by {symbol}{abs(value):.3f}"
            summary_item['feature_item'].append(feature_text)
        summary_list.append(summary_item)
    return summary_list

def summary_text(features):
    shap_val = shap_explain(features)[0]
    features_name = list(features.keys())
    class_name = classify_res(features)
    class_index = class_labels.index(class_name)

    impacts = []
    for i, feature in enumerate(features_name):
        value = shap_val[i][class_index]
        impacts.append((features_map[feature], value))

    # Separate positive and negative contributions
    positive_impacts = [(name, val) for name, val in impacts if val > 0]
    negative_impacts = [(name, val) for name, val in impacts if val < 0]
    negative_impacts.sort(key=lambda x: x[1])  # sort by most negative first
    positive_impacts.sort(key=lambda x: x[1], reverse=True)

    # Format helpers
    def format_contrib(name, val):
        symbol = "+" if val >= 0 else "-"
        return f"**{name}/* (##impact score: {abs(val):.2f}/#)"

    if "not" in class_name.lower():
        if positive_impacts:
            top_neg = positive_impacts[:2]
            other_neg = positive_impacts[2:]
            neg_text = " and ".join([format_contrib(n, v) for n, v in top_neg])
            others_text = ", ".join([format_contrib(name, val) for name, val in other_neg])
            summary = (f"This resume is **{class_name}/* because the {neg_text} significantly lowered the candidate's fit."
                        + (f" Other factors such as {others_text} also lowered the suitability but to a lesser extent." if others_text else ""))

        if negative_impacts:
            pos_text = ", ".join([format_contrib(n, v) for n, v in negative_impacts])
            summary += f" Some positive factors include {pos_text}, but they were not enough to improve the suitability score."
    else:
        top_pos = positive_impacts[:2]
        other_pos = positive_impacts[2:]

        top_text = " and ".join([format_contrib(name, val) for name, val in top_pos])
        others_text = ", ".join([format_contrib(name, val) for name, val in other_pos])

        summary = (f"This resume is **{class_name}/* because the {top_text} are the biggest positive contributors."
                   + (f" Other factors such as {others_text} also support the suitability but to a lesser extent." if others_text else ""))

        if negative_impacts:
            neg_text = ", ".join([format_contrib(n, v) for n, v in negative_impacts[:2]])
            summary += f" Some negative factors include {neg_text}"
    return summary