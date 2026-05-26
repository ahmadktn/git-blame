import csv
import re
import requests


def calculate_commit_score(message):
    """
    Scoring Engine matching Section 5.2 PRD rules and weights.
    Returns a total score out of 100.
    """
    score = 0
    
    # Split message into subject line and body
    lines = message.strip().split("\n")
    subject = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    
    # -------------------------------------------------------------------------
    # 1. Message Length & Line Length (15% + 15% = 30% Weight total)
    # -------------------------------------------------------------------------
    length_score = 0
    if len(subject) < 10:
        length_score += 0   
    elif 20 <= len(subject) <= 72:
        length_score += 15  
    else:
        length_score += 5   
        
    if len(subject) <= 72:
        length_score += 15  
        
    score += length_score

    # -------------------------------------------------------------------------
    # 2. Sentence Casing (10% Weight)
    # -------------------------------------------------------------------------
    if subject and subject[0].isupper():
        score += 10

    # -------------------------------------------------------------------------
    # 3. No Trailing Period (5% Weight)
    # -------------------------------------------------------------------------
    if subject and not subject.endswith("."):
        score += 5

    # -------------------------------------------------------------------------
    # 4. Imperative Verb Detection (20% Weight)
    # -------------------------------------------------------------------------
    IMPERATIVE_VERBS = {
        "add", "fix", "update", "refactor", "remove", "delete", "change", 
        "implement", "create", "setup", "make", "bump", "document", "test",
        "clean", "integrate", "allow", "ensure", "prevent", "avoid"
    }
    
    words_list = re.sub(r"[^\w\s]", "", subject).split()
    first_word = words_list[0].lower() if words_list else ""
    
    if first_word in IMPERATIVE_VERBS:
        score += 20

    # -------------------------------------------------------------------------
    # 5. Generic Word Detection (20% Weight)
    # -------------------------------------------------------------------------
    blacklist = {"fix", "wip", "update", "change", "stuff", "misc", "final"}
    words = set(re.sub(r"[^\w\s]", "", subject).lower().split())
    
    if not words.intersection(blacklist):
        score += 20

    # -------------------------------------------------------------------------
    # 6. Body Presence (15% Weight)
    # -------------------------------------------------------------------------
    if len(body) > 10:  
        score += 15

    return score


def get_commits(repo_url, max_tasks):
    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        print("Invalid GitHub URL. Please check it and try again.")
        return

    owner = match.group(1)
    repo = match.group(2).replace(".git", "") 

    api_url = f"https://github.com{owner}/{repo}/commits"
    params = {"per_page": max_tasks}

    print(f"\nFetching the latest {max_tasks} commits from {owner}/{repo}...")
    response = requests.get(api_url, params=params)

    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return

    commits_data = response.json()
    filename = f"{repo}_scored_commits.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Author", "Date", "Commit Message", "Lines Added", "Lines Deleted", "Engine Score (Out of 100)", "URL"])

        for commit in commits_data:
            author = commit["commit"]["author"]["name"]
            date = commit["commit"]["author"]["date"]
            message = commit["commit"]["message"]
            url = commit["html_url"]
            
            detail_url = commit["url"] 
            detail_response = requests.get(detail_url)
            
            additions = 0
            deletions = 0
            
            if detail_response.status_code == 200:
                stats = detail_response.json().get("stats", {})
                additions = stats.get("additions", 0)
                deletions = stats.get("deletions", 0)

            score = calculate_commit_score(message)
            writer.writerow([author, date, message, additions, deletions, score, url])

    print(f"Success! Saved scored data to {filename}")


if __name__ == "__main__":
    print("=== SCORING ENGINE TERMINAL ACTIVE ===")
    github_repo = input("Enter GitHub Repo URL: ")
    number_of_tasks = int(input("How many latest tasks/commits to fetch? "))
    get_commits(github_repo, number_of_tasks)
        
