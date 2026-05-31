import csv
import json
import math
import re
import urllib.request


def calculate_nlp_pipeline_score(message):
    """
    YOUR EXACT SECTION 5.4 LOCAL NLP PIPELINE
    """
    lines = message.strip().split("\n")
    subject = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    if not subject:
        return 0, {"Error": "Empty commit text payload"}

    GOOD_CORPUS_TOKENS = {"implement", "refactor", "fix", "optimize", "add", "security", "auth", "api", "database"}
    BAD_CORPUS_TOKENS = {"wip", "stuff", "misc", "test", "work", "code", "changes", "final", "done", "bug"}

    STOPWORDS = {"a", "an", "the", "and", "or", "but", "if", "then", "of", "at", "by", "for", "with", "in", "to", "on", "is", "it", "some"}
    raw_tokens = re.sub(r"[^\w\s]", " ", message.lower()).split()
    filtered_tokens = [t for t in raw_tokens if t not in STOPWORDS and len(t) > 1]
    unique_tokens = set(filtered_tokens)

    IMPERATIVE_VERBS = {
        "add", "fix", "update", "refactor", "remove", "delete", "change", 
        "implement", "create", "setup", "make", "bump", "document", "test",
        "clean", "integrate", "allow", "ensure", "prevent", "avoid", "optimize"
    }
    subject_tokens = re.sub(r"[^\w\s]", "", subject).lower().split()
    first_token = subject_tokens[0] if subject_tokens else ""
    
    pos_score = 25 if first_token in IMPERATIVE_VERBS else 0

    ARTIFACT_PATTERN = r"(\b\w+\.(py|json|md|js|html|css|java|cpp|ts|go|yml|sql)\b|([a-zA-Z0-9_\-]+:)|[A-Z]+-\d+|\b(database|auth|api|ui|server|client|worker|router|model|controller|service|middleware)\b)"
    artifacts_detected = re.findall(ARTIFACT_PATTERN, message, flags=re.IGNORECASE)
    ner_score = 25 if len(artifacts_detected) >= 1 else 0

    EMOTIONAL_VAGUE_LEXICON = {"hate", "stupid", "broken", "idiot", "dumb", "furious", "please", "hope", "maybe", "probably", "guess", "hell", "crying", "ugh", "lol"}
    found_emotional_tokens = unique_tokens.intersection(EMOTIONAL_VAGUE_LEXICON)
    sentiment_score = 25 if len(found_emotional_tokens) == 0 else max(25 - (len(found_emotional_tokens) * 10), 0)

    good_intersection = unique_tokens.intersection(GOOD_CORPUS_TOKENS)
    bad_intersection = unique_tokens.intersection(BAD_CORPUS_TOKENS)
    
    similarity_score = 15  
    if len(good_intersection) > len(bad_intersection):
        similarity_score = 25
    elif len(bad_intersection) > len(good_intersection):
        similarity_score = 5

    total_pipeline_score = pos_score + ner_score + sentiment_score + similarity_score
    
    rationale_log = {
        "Stage 1 (POS Tagging)": f"{pos_score}/25 Points (First word: '{first_token}')",
        "Stage 2 (NER Signal)": f"{ner_score}/25 Points (Artifact targets mapped: {len(artifacts_detected)})",
        "Stage 3 (Tone Audit)": f"{sentiment_score}/25 Points (Emotional markers flagged: {len(found_emotional_tokens)})",
        "Stage 4 (Similarity)": f"{similarity_score}/25 Points (Corpus intersection match applied)"
    }

    return total_pipeline_score, rationale_log


# =============================================================================
# MONDAY'S GITHUB CORE: EXTREMELY DYNAMIC FETCH ENGINE
# =============================================================================
def fetch_github_commits_to_csv(repo_url, count, output_csv="commits.csv"):
    """
    Scans the repository. Extracts authors dynamically from online data or logs.
    """
    print(f"📡 Downloading the latest {count} commits from GitHub profile...")
    clean_url = repo_url.replace("https://github.com", "").replace(".git", "").strip("/")
    api_url = f"https://github.com{clean_url}/commits?per_page={count}"
    
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Pydroid-Mobile-Client'})
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['author', 'message'])
            
            for item in data:
                # DYNAMIC NAME SCANNER: Grabs whatever username is active on the account
                author_name = "UnknownContributor"
                if item.get('author') and item['author'].get('login'):
                    author_name = item['author']['login']
                elif item.get('commit') and item['commit'].get('author'):
                    author_name = item['commit']['author'].get('name', 'UnknownContributor')
                
                writer.writerow([author_name, item['commit']['message']])
                
        print(f"📁 Network Online: Real repository author datasets written to '{output_csv}'!\n")
        return True

    except Exception:
        print("⚠️ Network offline! Using dynamic placeholder dataset profiles...\n")
        
        # Generic placeholders that hide actual team names completely
        offline_anonymous_data = [
            ["Committer_Alpha", "refactor: optimize database structure in model.py to stop lag"],
            ["Committer_Beta", "fix: change security validation schemas for api router setup"],
            ["Committer_Gamma", "implement dynamic state parameters layout inside main.js"],
            ["Committer_Delta", "wip stuff"],
            ["Committer_Epsilon", "fix bug"],
            ["Committer_Zeta", "stupid broken database connection stuff ugh lol"]
        ]
        
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['author', 'message'])
            writer.writerows(offline_anonymous_data)
        return True


def process_csv_and_generate_leaderboards(csv_filename):
    scored_commits = []
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                author = row.get('author', 'Unknown')
                message = row.get('message', '')
                if not message.strip():
                    continue
                score, log_details = calculate_nlp_pipeline_score(message)
                scored_commits.append({"author": author, "message": message, "score": score, "log": log_details})
    except FileNotFoundError:
        return [], []

    ranked = sorted(scored_commits, key=lambda x: x['score'], reverse=True)
    hall_of_fame = ranked[:5]
    shame_candidates = [c for c in ranked if c['score'] < 70]
    hall_of_shame = sorted(shame_candidates, key=lambda x: x['score'])[:5]
    
    return hall_of_fame, hall_of_shame


if __name__ == "__main__":
    target_repository = "https://github.comahmadktn/git-blame.git"
    fetch_limit = 20
    target_csv = "commits.csv"
    
    if fetch_github_commits_to_csv(target_repository, fetch_limit, target_csv):
        fame, shame = process_csv_and_generate_leaderboards(target_csv)

        print("🏆 LEADERBOARD DASHBOARD: HALL OF FAME")
        print("=" * 60)
        for i, card in enumerate(fame, 1):
            msg_preview = card['message'].strip().split('\n')[0]
            print(f"[{i}] SCORE: {card['score']}/100 | Dev: @{card['author']}")
            print(f"    Message: \"{msg_preview}\"")
            print("-" * 60)

        print("\n💀 LEADERBOARD DASHBOARD: HALL OF SHAME")
        print("=" * 60)
        if not shame:
            print("   🎉 Clean tracker dashboard! No low quality scores flagged.")
        for i, card in enumerate(shame, 1):
            print(f"[{i}] SCORE: {card['score']}/100 | Dev: @{card['author']}")
            print(f"    Reasoning: {card['log'].get('Stage 1 (POS Tagging)', '')}")
            print("-" * 60)
