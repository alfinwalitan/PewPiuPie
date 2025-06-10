import spacy

model_best_path = "models/roberta/model-best"
model_best = spacy.load(model_best_path)
ner_labels = [
    'Job Specific Skills',
    'Designation',
    'Tech Tools',
    'Degree',
    'Location',
    'Companies worked at',
    'College Name',
    'Soft Skills',
    'Years of Experience',
    'Graduation Year'
]

def connect_designation_exp(designations, exp, MAX_DISTANCE=15):
    used_designations = set()
    mapped = []

    for e in exp:
        # Try to find backward matches first
        backward_matches = [
            des for des in designations
            if des not in used_designations and 0 <= (e[0] - des[0]) <= MAX_DISTANCE
        ]

        selected = None
        if backward_matches:
            # Closest backward match
            selected = min(backward_matches, key=lambda des: e[0] - des[0])
        else:
            # If no backward match, try forward
            forward_matches = [
                des for des in designations
                if des not in used_designations and 0 <= (des[0] - e[0]) <= MAX_DISTANCE
            ]
            if forward_matches:
                selected = min(forward_matches, key=lambda des: des[0] - e[0])

        if selected:
            exp_info = {
                "exp_range": e[2],
                "designation": selected[2],
            }
            if exp_info not in mapped:
                mapped.append(exp_info)
            used_designations.add(selected)
        else:
            mapped.append({
                "exp_range": e[2],
                "designation": None,
            })

    return mapped

def ner_output(doc):
    info = {}

    designations = [(e.start, e.end, e.text) for e in doc.ents if e.label_ == 'Designation']
    experiences = [(e.start, e.end, e.text) for e in doc.ents if e.label_ == 'Years of Experience']

    for e in doc.ents:
        if e.label_ not in info.keys():
            info[e.label_] = [e.text]
        else:
            info[e.label_].append(e.text)

    for label in ner_labels:
        if label not in info.keys():
            info[label] = []

    if info['Years of Experience']:
        info['Years of Experience'] = connect_designation_exp(designations, experiences)

    return info

def extract_ner(text, model = model_best):
    nlp = model
    doc = nlp(text)
    return ner_output(doc)