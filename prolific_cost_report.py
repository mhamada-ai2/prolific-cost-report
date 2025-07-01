#!/usr/bin/env python3
import os
import sys
import csv
import requests
import argparse
import logging
from pathlib import Path
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Base URL for Prolific public API
API_URL = "https://api.prolific.com/api/v1"

# Get Prolific API token from the environment
API_TOKEN = os.getenv("PROLIFIC_API_TOKEN")
if not API_TOKEN:
    logger.error("Please set the PROLIFIC_API_TOKEN environment variable")
    sys.exit(1)

# Prepare a persistent HTTP session
session = requests.Session()
session.headers.update({
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
})


def fetch_studies(project_id: str) -> list:
    """
    Fetch all completed or active studies in the given project,
    following every page until there are no more.
    """
    studies = []
    params = {"state": ["COMPLETED", "ACTIVE", "PAUSED", "AWAITING REVIEW"], "page_size": 100}
    url = f"{API_URL}/projects/{project_id}/studies"

    while url:
        logger.debug(f"GET {url} params={params}")
        resp = session.get(url, params=params)
        resp.raise_for_status()
        payload = resp.json()

        # collect this page’s studies
        studies.extend(payload.get("results", []))

        # advance to the next page (if any)
        next_link = (
            payload
            .get("_links", {})
            .get("next", {})
            .get("href")
        )
        url = next_link
        params = {}  # no need to resend filters once the 'next' URL is absolute

    return studies


def fetch_study_details(study_id: str) -> dict:
    """
    Fetch the full study object given its ID.
    """
    resp = session.get(f"{API_URL}/studies/{study_id}")
    resp.raise_for_status()
    return resp.json()


def get_total_rewards(study_id: str) -> float:
    """
    Fetch cost breakdown and return sum of rewards and bonuses.
    """
    resp = session.get(f"{API_URL}/studies/{study_id}/cost")
    resp.raise_for_status()
    cost_data = resp.json()
    rewards = cost_data["rewards"]["rewards"]["amount"]
    bonuses = cost_data["bonuses"]["rewards"]["amount"]
    return rewards + bonuses


def fetch_project_name(project_id: str) -> str:
    """
    Fetch the project object and return its title.
    """
    resp = session.get(f"{API_URL}/projects/{project_id}")
    resp.raise_for_status()
    return resp.json().get("title", project_id)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Prolific cost reports")
    parser.add_argument("project_id", nargs="?", help="Prolific project ID")
    parser.add_argument("-o", "--output", help="Path to output CSV file")
    return parser.parse_args()


def main(project_id: str = None, output_csv: Path = None):
    if not project_id:
        project_id = input("Enter the project's Prolific ID: ")
    try:
        project_name = fetch_project_name(project_id)
    except requests.HTTPError as e:
        logger.error(f"Unable to retrieve project {project_id}: {e}")
        sys.exit(1)

    if not output_csv:
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (" ", "-", "_"))
        safe_name = safe_name.rstrip()
        reports_dir = Path(__file__).parent / "cost_reports"
        reports_dir.mkdir(exist_ok=True)
        date_str = datetime.today().strftime("%Y-%m-%d %H-%M")
        output_csv = reports_dir / f"{safe_name} - Cost Report - {date_str}.csv"
    output_csv = Path(output_csv)

    logger.info(f"Fetching studies for {project_name}...")
    studies = fetch_studies(project_id)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
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
            "total_study_cost",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        for s in studies:
            study_id = s["id"]
            try:
                details = fetch_study_details(study_id)
            except requests.HTTPError as e:
                logger.error(f"Unable to retrieve study {study_id}: {e}")
                continue

            pacific_tz = pytz.timezone('US/Pacific')
            utc_date = datetime.fromisoformat(s.get("published_at", ""))
            pst_date = utc_date.astimezone(pacific_tz)
            reward_usd = details["reward"] / 100
            total_places = s.get("total_available_places", 0)
            est_hours = details.get("estimated_completion_time", 0) / 60
            median_hours = details.get("average_time_taken_seconds", 0) / 3600
            intended_rph = (reward_usd / est_hours) if est_hours else 0
            average_rph = details.get("average_reward_per_hour", 0) / 100
            total_study_hours = est_hours * total_places
            total_rewards = get_total_rewards(study_id) / 100
            total_cost = s.get("total_cost", 0) / 100

            row = {
                "study_name": s.get("name", ""),
                "internal_name": s.get("internal_name", ""),
                "study_id": study_id,
                "published_at": pst_date,
                "total_available_places": total_places,
                "estimated_completion_time": round(est_hours, 5),
                "average_completion_time": round(median_hours, 5),
                "intended_reward_per_hour": round(intended_rph, 2),
                "average_reward_per_hour": round(average_rph, 2),
                "total_study_hours": round(total_study_hours, 5),
                "total_study_rewards": round(total_rewards, 2),
                "total_study_cost": round(total_cost, 2),
            }
            count += 1
            writer.writerow(row)
            logger.info(f"[DONE] {s.get('internal_name', '')} ({study_id})")

    logger.info(f"Wrote rows for {count}/{len(studies)} studies to {output_csv}")


if __name__ == "__main__":
    args = parse_args()
    main(args.project_id, args.output)
