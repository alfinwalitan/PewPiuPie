from .preprocess import pdf_to_text
from .ner_model import extract_ner
from .scoring import similarity_score, total_score
from .classifier import classify_res
from .shap_explainer import summary_text

def run_system(pdf_path, job_desc):
    try:
        text = pdf_to_text(pdf_path)
        info = extract_ner(text)

        sim_score = similarity_score(job_desc, info)
        score = total_score(sim_score)

        cls = classify_res(sim_score)
        summary = summary_text(sim_score)

        result = {
            "Score" : score,
            "Resume Classification" : cls,
            "Summary" : summary,
            "Resume Information" : info
        }
        return True, result
    except Exception as  e:
        return False, str(e)
