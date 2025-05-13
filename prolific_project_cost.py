import os
import sys
import csv
import requests
from pathlib import Path
import datetime

# Base URL for Prolific public API
API_URL = "https://api.prolific.com/api/v1"

# Get Prolific API token from the environment
API_TOKEN = os.getenv("PROLIFIC_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Please set the PROLIFIC_API_TOKEN environment variable")

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}


def fetch_studies(project_id):
    """
    Fetch all completed (non‑draft) studies in the given project.
    Uses the 'status=COMPLETED' and 'project_id' query params.
    """
    studies = []
    params = {
        "project_id": project_id,
        "status": "COMPLETED",
        "page_size": 100
    }
    url = f"{API_URL}/projects/{project_id}/studies"
    while url:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        payload = resp.json()
        studies.extend(payload["results"])
        url = payload.get("links", {}).get("next")
        params = {}
    return studies


def fetch_study_details(study_id):
    """
    Fetch the full study object given study_id for additional details.
    """
    resp = requests.get(f"{API_URL}/studies/{study_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def get_total_rewards(study_id):
    """
    Fetch the full study cost object and calculate total rewards, including bonuses.
    """
    resp = requests.get(f"{API_URL}/studies/{study_id}/cost", headers=HEADERS)
    resp.raise_for_status()
    cost_data = resp.json()
    rewards = cost_data["rewards"]["rewards"]["amount"]
    bonuses = cost_data["bonuses"]["rewards"]["amount"]
    return rewards + bonuses


def fetch_project_name(project_id):
    """
    Fetch the full project object and return its name (title).
    """
    resp = requests.get(f"{API_URL}/projects/{project_id}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("title", project_id)


def main(project_id=None, output_csv=None):
    if not project_id:
        project_id = input("Enter the project's Prolific ID: ")
    try: 
        project_name = fetch_project_name(project_id)
    except:
        print("[ERROR] Unable to retrive project with given ID.")
        return
        
    if not output_csv:
        safe_name = "".join(c for c in project_name
                            if c.isalnum() or c in (" ", "-", "_")).rstrip()
        reports_dir = Path(__file__).parent / "cost_reports"
        reports_dir.mkdir(exist_ok=True)
        date_str = datetime.date.today().isoformat()
        output_csv = reports_dir / f"{safe_name} - Cost Report - {date_str}.csv"
    output_csv = str(output_csv)

    print(f"Fetching studies for {project_name} ({project_id})...")
    studies = fetch_studies(project_id)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "study_name",
            "internal_name",
            "study_id",
            "published_at",
            "total_available_places",
            "estimated_completion_time",
            "average_completion_time",
            "intended_reward_per_hour",
            "average_reward_per_hour",
            "total_study_hours",
            "total_study_rewards",
            "total_study_cost"
        ])

        for s in studies:
            try: 
                details = fetch_study_details(s["id"])
            except:
                print(f"[ERROR] Unable to retrieve study details: {s["internal_name"]} ({s["id"]})")
            else:
                reward_usd         = details["reward"] / 100
                total_places       = s["total_available_places"]
                est_hours          = details["estimated_completion_time"] / 60
                median_hours       = details["average_time_taken_seconds"] / 60 / 60
                intended_rph       = (reward_usd / est_hours) if est_hours else 0
                average_rph        = details["average_reward_per_hour"] / 100
                total_study_hours  = est_hours * total_places
                total_rewards      = get_total_rewards(s["id"]) / 100
                total_cost         = s["total_cost"] / 100

                writer.writerow([
                    s["name"],
                    s["internal_name"],
                    s["id"],
                    s["published_at"].split("T")[0],
                    total_places,
                    round(est_hours, 5),
                    round(median_hours, 5),
                    round(intended_rph, 2),
                    round(average_rph, 2),
                    round(total_study_hours, 5),
                    round(total_rewards, 2),
                    round(total_cost, 2)
                ])
                print(f"[DONE] {s["internal_name"]} ({s["id"]})")
    
    print(f"Wrote cost report to {output_csv}")


if __name__ == "__main__":
    if len(sys.argv) > 3:
        print("Usage: python prolific_project_cost.py [project_id] [output_csv]")
        sys.exit(1)
    proj_id = sys.argv[1] if len(sys.argv) >= 2 else None
    out_csv = sys.argv[2] if len(sys.argv) >= 3 else None
    main(proj_id, out_csv)
