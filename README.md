# Prolific Cost Report Script

A Python script that generates detailed cost reports for Prolific projects. It fetches data for all completed studies in the project via the Prolific API and outputs a timestamped cost report as a CSV file.

---

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Output](#output)

---

## Features

* Fetches all completed studies for a given Prolific project
* Calculates:
  * Estimated and average participant time
  * Intended and average reward per hour
  * Total study hours, rewards, and cost
* Outputs results in a CSV with a default or custom filename

## Prerequisites

* Python 3.8 or higher
* A valid Prolific project ID for the target project
* A valid Prolific API token with access to the target project

## Installation

1. **Clone this repository** (or download `prolific_cost_report.py`):

   ```bash
   git clone https://github.com/mhamada-ai2/prolific-cost-report.git
   cd prolific-cost-report
   ```
2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # macOS/Linux
   .venv\\Scripts\\activate     # Windows
   ```
3. **Install dependencies**

   ```bash
   pip install requests
   ```

## Configuration

1. **Generate an API token** on Prolific.
   * Log in to Prolific at [https://www.prolific.com/](https://www.prolific.com/).
   * Navigate to **API Tokens** in the sidebar.
   * Click **Create API token**, give the token a name, and copy the value.
2. **Set your Prolific API token** as an environment variable:

   ```bash
   export PROLIFIC_API_TOKEN="your_token_here"    # macOS/Linux
   set PROLIFIC_API_TOKEN=your_token_here         # Windows cmd.exe
   $env:PROLIFIC_API_TOKEN="your_token_here"      # Windows PowerShell
   ```

## Usage

1. **Find your Project ID** on Prolific.

   * Log in to Prolific at [https://www.prolific.com/](https://www.prolific.com/).
   * Navigate to **Projects** in the sidebar and open the desired project.
   * In your browser’s address bar, the URL will look like `https://app.prolific.com/researcher/workspaces/projects/PROJECT_ID`.
   * Copy the `PROJECT_ID` portion of that URL for use below.

2. In the **Command Line**:

    ```bash
    python3 prolific_project_cost.py <project_id> [-o output.csv]
    ```

    * `<project_id>`: your Prolific project identifier (required if not prompted). Substitute with `PROJECT_ID`.
    * `-o`, `--output`: optional path for the CSV. If omitted, defaults to `./cost_reports/{Project Name} - Cost Report - YYYY-MM-DD.csv`

### Examples

* **Prompt for project ID** using default filename:

  ```bash
  python3 prolific_project_cost.py
  ```
* **Specify project ID** using default filename:

  ```bash
  python3 prolific_project_cost.py PROJECT_ID
  ```
* **Specify project ID & output path**:

  ```bash
  python3 prolific_project_cost.py PROJECT_ID -o reports/my_report.csv
  ```

## Output

The script writes a CSV with columns:

| Column Name                 | Description                                                       |
| --------------------------- | ----------------------------------------------------------------- |
| study\_name                 | The public-facing title of the study.                             |
| internal\_name              | The internal Prolific identifier/name for the study.              |
| study\_id                   | The unique Prolific study identifier (see study link).            |
| published\_at               | Date the study was published (YYYY-MM-DD).                        |
| total\_available\_places    | Number of participant slots allocated to the study.               |
| estimated\_completion\_time | Estimated time per participant in hours.                          |
| average\_completion\_time   | Median actual time participants took in hours.                    |
| intended\_reward\_per\_hour | Reward rate (USD/hour) based on the estimated completion time.    |
| average\_reward\_per\_hour  | Mean actual reward rate (USD/hour) paid to participants.          |
| total\_study\_hours         | Total estimated hours across all slots (estimated\_time × slots). |
| total\_study\_rewards       | Sum of all reward payouts (including bonuses) in USD.             |
| total\_study\_cost          | Total cost including rewards, fees, and taxes in USD.             |

Each row will correspond to one study in the specified Prolific project.
