import torch
from sentence_transformers import SentenceTransformer, util
from utils import *

# Load a pre-trained model
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(job_desc, res):
    if job_desc and res:
        # Encode to Embeddings
        embeddings_jd = similarity_model.encode(job_desc, convert_to_tensor=True)
        embeddings_res = similarity_model.encode(res, convert_to_tensor=True)

        # Compute pairwise cosine similarity matrix (embeddings_jd = Rows, embeddings_res = Cols)
        cos_sim_matrix = util.cos_sim(embeddings_jd, embeddings_res)

        return cos_sim_matrix
    else:
        return 0
    
def calculate_average(cos_sim):
    # Find best match from res for each item in job_desc
    similarities = []
    for i in range(len(cos_sim)):
        max_score = max(cos_sim[i])
        similarities.append(max_score.item())

    # Average similarity across all item
    if len(cos_sim) > 0:
        average_similarity = sum(similarities) / len(cos_sim)
    else:
        average_similarity = 0.0

    return round(average_similarity, 2)

def skill_similarity(res_skills, jd_skills):
    jd_skills_set = set([s.lower().strip() for s in jd_skills])
    res_skills_set = set([s.lower().strip() for s in res_skills])

    skill_intersection = res_skills_set.intersection(jd_skills_set)
    skill_match_count = 0
    if len(skill_intersection) > 0:
        skill_match_count = round(len(skill_intersection) / len(jd_skills_set), 2)

    skill_cosine = calculate_similarity(list(jd_skills_set), list(res_skills_set))
    if isinstance(skill_cosine, int) and skill_cosine == 0:
        return skill_cosine, skill_match_count
    return calculate_average(skill_cosine), skill_match_count

def designation_similarity(res_des, jd_des):
    res_des_set = list(set([s.lower().strip() for s in res_des]))

    designation_cosine = calculate_similarity(jd_des, res_des_set)
    if isinstance(designation_cosine, int) and designation_cosine == 0:
        return designation_cosine
    return calculate_average(designation_cosine)

def degree_similarity(res_deg, jd_deg):
    res_deg_level = list(set(map(format_degree, [s.lower().strip() for s in res_deg])))
    res_deg_set = [item[0] for item in res_deg_level]

    jd_deg_set = jd_deg
    jd_deg_level = format_degree(jd_deg)

    degree_cosine = calculate_similarity(jd_deg_set, res_deg_set)

    if isinstance(degree_cosine, int) and degree_cosine == 0:
        return 0.0
    else:
        degree_cosine = degree_cosine.tolist()

    for idx, deg in enumerate(res_deg_level):
        if deg[1] == jd_deg_level[1]:
            continue
        elif deg[1] > jd_deg_level[1]:
            degree_cosine[0][idx] += 0.1
        else:
            degree_cosine[0][idx] -= 0.1

    return calculate_average(torch.tensor(degree_cosine))

def exp_similarity(res_exp, jd_exp, jd_des):
    if type(jd_exp) is str:
        jd_exp = calculate_year(jd_exp)

    total_exp = 0
    for exp in res_exp:
        des_sim =calculate_similarity(exp['designation'], jd_des)
        if isinstance(des_sim, int) and des_sim == 0:
            continue
        else:
            des_sim = round(des_sim.tolist()[0][0], 2)
            if des_sim >= 0.6:
                total_exp += calculate_year(exp['exp_range'])

    exp_match = 0 # False
    if total_exp >= jd_exp:
        exp_match = 1 # True

    return exp_match, round(total_exp, 2)

def similarity_score(job_desc, res):
    combine_skill = res['Tech Tools'] + res['Job Specific Skills'] + res['Soft Skills']

    designation_score = designation_similarity(res['Designation'], job_desc['Required Designation'])
    skill_score, skill_match_ratio = skill_similarity(combine_skill, job_desc['Required Skills'])
    degree_score = degree_similarity(res['Degree'], job_desc['Required Degree'])
    exp_match, total_exp = exp_similarity(res['Years of Experience'], job_desc['Required Years of Experience'], job_desc['Required Designation'])

    return {
        "designation_score" : designation_score,
        "skill_score" : skill_score,
        "skill_match_ratio" : skill_match_ratio,
        "degree_score" : degree_score,
        "exp_match" : exp_match,
        "total_exp" : total_exp
    }

def total_score(sim_score):
    score_ratio = {
        "designation": 0.3,
        "skill": 0.4,
        "degree": 0.1,
        "exp": 0.2
    }

    return round(
        (sim_score['designation_score'] * score_ratio['designation'] +
        sim_score['skill_score'] * score_ratio['skill'] +
        sim_score['degree_score'] * score_ratio['degree'] +
        sim_score['exp_match'] * score_ratio['exp']) * 100,
        2)