import csv
import json
import re
import urllib.request

def generate_local_summary_notes(message, score, pos, ner, sentiment, similarity):
    """
    Completely local alternative to OpenRouter. Generates clean feedback 
    phrases dynamically without hitting external network servers.
    """
    if score == 100:
        return "Excellent commit structure. Follows conventional standards and names specific artifacts."
    
    issues = []
    if pos == 0:
        issues.append("does not start with an imperative command verb")
    if ner == 0:
        issues.append("fails to specify system files or layers")
    if sentiment < 25:
        issues.append("contains highly informal or emotional language")
    if similarity == 5:
        issues.append("uses vague corpus placeholders like 'wip' or 'stuff'")
        
    if not issues:
        return f"Solid message layout scoring {score}/100. Minor metadata optimization recommended."
        
    return f"Commit text code quality drops because it " + ", and it ".join(issues) + "."


def calculate_nlp_pipeline_score(message):
    lines = message.strip().split("\n")
    # Safely targets the first text string element from the split list
    subject = lines[0].strip() if lines else ""
    
    if not subject:
        return 0, "Empty payload"

    GOOD_CORPUS = {"implement", "refactor", "fix", "optimize", "add", "security", "auth", "api", "database"}
    BAD_CORPUS = {"wip", "stuff", "misc", "test", "work", "code", "changes", "final", "done", "bug"}
    STOPWORDS = {"a", "an", "the", "and", "or", "but", "of", "to", "on", "is", "it"}

    raw_tokens = re.sub(r"[^\w\s]", " ", message.lower()).split()
    unique_tokens = {t for t in raw_tokens if t not in STOPWORDS and len(t) > 1}

    # 1. Imperative Command Verb Check (25 Pts)
    IMPERATIVE_VERBS = {"add", "fix", "update", "refactor", "remove", "delete", "change", "implement", "create", "setup"}
    subject_tokens = re.sub(r"[^\w\s]", "", subject).lower().split()
    first_token = subject_tokens[0] if subject_tokens else ""
    pos_score = 25 if first_token in IMPERATIVE_VERBS else 0

    # 2. Artifact Specificity Check (25 Pts)
    ARTIFACT_PATTERN = r"(\b\w+\.(py|json|md|js|yml|sql)\b|\b(database|auth|api|ui|server)\b)"
    artifacts_detected = re.findall(ARTIFACT_PATTERN, message, flags=re.IGNORECASE)
    ner_score = 25 if len(artifacts_detected) >= 1 else 0

    # 3. Tone/Vagueness Guardrails (25 Pts)
    EMOTIONAL_LEXICON = {"hate", "stupid", "broken", "idiot", "dumb", "please", "hope", "maybe", "ugh", "lol"}
    found_bad_words = unique_tokens.intersection(EMOTIONAL_LEXICON)
    sentiment_score = max(25 - (len(found_bad_words) * 10), 0)

    # 4. Keyword Similarity Match (25 Pts)
    good_match = unique_tokens.intersection(GOOD_CORPUS)
    bad_match = unique_tokens.intersection(BAD_CORPUS)
    similarity_score = 15
    if len(good_match) > len(bad_match): similarity_score = 25
    elif len(bad_match) > len(good_match): similarity_score = 5

    total_score = pos_score + ner_score + sentiment_score + similarity_score
    notes = generate_local_summary_notes(message, total_score, pos_score, ner_score, sentiment_score, similarity_score)
    
    return total_score, notes


def fetch_github_commits_to_csv(repo_url, count, output_csv="commits.csv"):
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
                author_name = "UnknownContributor"
                if item.get('author') and item['author'].get('login'):
                    author_name = item['author']['login']
                elif item.get('commit') and item['commit'].get('author'):
                    author_name = item['commit']['author'].get('name', 'UnknownContributor')
                writer.writerow([author_name, item['commit']['message']])
        print(f"📁 Network Online: Real repository datasets written to '{output_csv}'!\n")
        return True
    except Exception:
        print("⚠️ Running with mobile test data profiles...\n")
        offline_data = [
            ["Ahmad", "refactor: optimize database structure in model.py to stop lag"],
            ["User_Mmeky", "fix: change security validation schemas for api router setup"],
            ["Junior_Dev", "wip stuff"],
            ["Ghost_User", "fix bug"],
            ["Stressed_Coder", "stupid broken database connection stuff ugh lol"]
        ]
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['author', 'message'])
            writer.writerows(offline_data)
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
                
                score, notes = calculate_nlp_pipeline_score(message)
                scored_commits.append({"author": author, "message": message, "score": score, "notes": notes})
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
            msg_preview = card['message'].strip().replace('\n', ' ')
            print(f"[{i}] SCORE: {card['score']}/100 | Dev: @{card['author']}")
            print(f"    Message: \"{msg_preview}\"")
            print(f"    Summary: {card['notes']}")
            print("-" * 60)

        print("\n💀 LEADERBOARD DASHBOARD: HALL OF SHAME")
        print("=" * 60)
        if not shame:
            print("   🎉 Clean tracker dashboard! No low quality scores flagged.")
        for i, card in enumerate(shame, 1):
            msg_preview = card['message'].strip().replace('\n', ' ')
            print(f"[{i}] SCORE: {card['score']}/100 | Dev: @{card['author']}")
            print(f"    Message: \"{msg_preview}\"")
            print(f"    Summary: {card['notes']}")
            print("-" * 60)
