import re
import json
from datetime import datetime
from dateutil import parser
from word2number import w2n

def parse_date(text):
    formats = ["%m/%y", "%m/%Y", "%b %Y", "%B %Y", "%Y", "%B %y", "%b %y"]
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except:
            continue
    try:
        return parser.parse(text)
    except:
        return None
    
def split_date_range(text_lower):
    # Date Range
    if " to " in text_lower:
        date_range = [text.strip() for text in text_lower.split("to")]
        return date_range

    if "-" in text_lower:
        date_range = [text.strip() for text in text_lower.split("-")]
        return date_range

    if "till" in text_lower:
        date_range = [text.strip() for text in text_lower.split("till")]
        return date_range

    if "until" in text_lower:
        date_range = [text.strip() for text in text_lower.split("until")]
        return date_range

    range_match = re.search(r'([a-zA-Z]+\s+\d+)\s+(.+)', text_lower)
    if range_match:
        start_date_str = range_match.group(1).strip()
        end_date_str = range_match.group(2).strip()
        return [start_date_str, end_date_str]

    match_since = re.match(r'(?i)since (.+)', text_lower)
    if match_since:
        return [match_since.group(1).strip(), "present"]

    year_range_match = [text.lower().strip() for text in text_lower.split()]
    if len(year_range_match) == 2:
        return year_range_match
    
def calculate_year(text):
    text_lower = text.lower()

    # Match "X years"
    year_match = re.search(r'(\d+(\.\d+)?)\s*\+?\s*(years?|yrs?)', text_lower)
    if year_match:
        return round(float(year_match.group(1)), 2)

    year_str_match = re.search(r'(\w+)\s*\+?\s*(years?|yrs?)', text_lower)
    if year_str_match:
        year_str = year_str_match.group(1)
        try:
            year_num = w2n.word_to_num(year_str)
            return round(year_num, 2)
        except ValueError:
            return 0

    # Match "X months"
    month_match = re.search(r'(\d+(\.\d+)?)\s*\+?\s*months?', text_lower)
    if month_match:
        total_months = float(month_match.group(1))
        return round(total_months / 12, 2)

    month_str_match = re.search(r'(\w+)\s*\+?\s*months?', text_lower)
    if month_str_match:
        month_str = month_str_match.group(1)
        try:
            month_num = w2n.word_to_num(month_str)
            total_months = month_num
            return round(total_months / 12, 2)
        except ValueError:
            return 0

    # Date Range
    date_range = split_date_range(text_lower)
    if date_range is None:
        return 0
    if "from" in date_range[0]:
        date_range[0] = date_range[0].replace("from ", "", 1)

    start_date = parse_date(date_range[0])
    end_str = date_range[1]
    if end_str in ["present", "current", "till date", "date", "now", "today"]:
        end_date = datetime.today()
    else:
        end_date = parse_date(end_str)

    # Calculate
    if start_date and end_date:
        duration = end_date - start_date
        if duration.days < 0:
            return 0
        return round(duration.days / 365, 2)
    else :
        return 0
    
def format_degree(text):
    degree_abbreviation_map = {
        "b": "bachelor",
        "bsc": "bachelor of science",
        "bs": "bachelor of science",
        "ba": "bachelor of arts",
        "bfa": "bachelor of fine arts",
        "bcom": "bachelor of commerce",
        "bba": "bachelor of business administration",
        "bca": "bachelor of computer applications",
        "basc": "bachelor of applied science",
        "bbm": "bachelor of business management",
        "bsed": "bachelor of science in education",
        "bscit": "bachelor of science in information technology",
        "bit": "bachelor of information technology",
        "be": "bachelor of engineering",
        "beng": "bachelor of engineering",
        "btech": "bachelor of technology",
        "bcs": "bachelor of computer science",
        "msc": "master of science",
        "ms": "master of science",
        "ma": "master of arts",
        "mfa": "master of fine arts",
        "mcom": "master of commerce",
        "mba": "master of business administration",
        "msed": "master of science in education",
        "mca": "master of computer applications",
        "me": "master of engineering",
        "med": "master of education",
        "mtech": "master of technology",
        "mcs": "master of computer science",
        "ssc": "secondary school certificate",
        "hsc": "higher secondary certificate",
        "hssc": "higher secondary school certificate",
        "pg diploma": "post graduate diploma",
        "aa" : "associate of arts",
        "as" : "associate of science",
        "jd" : "juris doctor",
        "phd": "doctor of philosophy",
        "edd": "doctor of education",
        "md": "doctor of medicine",
        "psyd": "doctor of psychology",
        "bpharm": "bachelor of pharmacy"
    }

    degree_levels = {"high school": 1, "diploma": 2, "bachelor": 3, "master": 4, "doctor": 5}

    text = text.lower()
    if "(" in text or ")" in text:
        text = re.sub(r'[()]', ' ', text)
    if "/" in text:
        text = " ".join(text.split("/"))
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces
    for abbr, full in degree_abbreviation_map.items():
        pattern = re.compile(r'\b' + re.escape(abbr) + r'\b', flags=re.IGNORECASE)
        text = pattern.sub(full, text).strip()

    deg_level = 0
    for level, score in degree_levels.items():
        if level in text:
            deg_level = score
            break

    return text, deg_level

def skills_str_to_list(text):
    return text.split(";; ")

def skills_str_to_comma(text):
    replaced = text.replace(";; ", ", ")
    return replaced

def datetime_to_str(date):
    formatted = date.strftime("%d %B %Y")
    return formatted

def load_json(data):
    return json.loads(data)

def create_unique_list(list):
    seen = set()
    unique_list= []
    for item in list:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            unique_list.append(item)
    return unique_list

def format_explanation(explanation):
    html_content = f"<p>{explanation.replace('**', '<b>')}</p>"
    html_content = html_content.replace('/*', '</b>')
    html_content = html_content.replace('##', '<i>')
    html_content = html_content.replace('/#', '</i>')
    html_content = html_content.replace('%%', '<i>')
    html_content = html_content.replace('/%', '</i>')
    return html_content