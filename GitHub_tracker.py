import csv
import re
import requests


def get_commits(repo_url, max_tasks):
    # 1. Clean up the URL to get the 'owner' and 'repo name'
    # Example: https://github.com/octocat/Hello-World -> owner: octocat, repo: Hello-World
    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        print("Invalid GitHub URL. Please check it and try again.")
        return

    owner = match.group(1)
    repo = match.group(2).replace(".git", "")  # Remove .git if present

    # 2. Use the GitHub API URL to fetch commits (tasks/updates)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    # We add a 'per_page' parameter to only grab what you asked for
    params = {"per_page": max_tasks}

    print(f"Fetching the latest {max_tasks} commits from {owner}/{repo}...")

    response = requests.get(api_url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        print(response.json().get("message", ""))
        return

    commits_data = response.json()

    # 3. Save the data into a CSV file
    filename = f"{repo}_latest_tasks.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(["Author", "Date", "Commit Message", "URL"])

        # Loop through each commit and save its details
        for commit in commits_data:
            author = commit["commit"]["author"]["name"]
            date = commit["commit"]["author"]["date"]
            message = commit["commit"]["message"]
            url = commit["html_url"]

            writer.writerow([author, date, message, url])

    print(f"Success! Saved data to {filename}")


# --- How to run it ---
if __name__ == "__main__":
    # You can change these variables to test different repos!
    github_repo = input("Enter GitHub Repo URL: ")
    number_of_tasks = int(input("How many latest tasks/commits to fetch? "))

    get_commits(github_repo, number_of_tasks)
