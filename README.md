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

* Fetches all completed studies in a Prolific project
* Calculates:
  * Estimated vs actual participant time
  * Intended and average reward per hour
  * Total study hours, rewards, and cost
* Outputs results in a CSV via a customizable filename

## Prerequisites

* Python 3.8 or higher
* A valid Prolific API token with access to the target project

## Installation

1. **Clone this repository**

   ```bash
   git clone https://github.com/mhamada-ai2/prolific-cost-report.git
   cd prolific-cost-report
   ```
2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\\Scripts\\activate     # Windows
   ```
3. **Install dependencies**

   ```bash
   pip install requests
   ```

## Configuration

1. **Set your Prolific API token** as an environment variable:

   ```bash
   export PROLIFIC_API_TOKEN="your_token_here"    # macOS/Linux
   set PROLIFIC_API_TOKEN=your_token_here         # Windows cmd.exe
   $env:PROLIFIC_API_TOKEN="your_token_here"      # Windows PowerShell
   ```

## Usage

```bash
python prolific_project_cost.py <project_id> [-o output.csv]
```

* `<project_id>`: your Prolific project identifier (required if not prompted)
* `-o`, `--output`: optional path for the CSV. If omitted, defaults to `./cost_reports/{Project Name} - Cost Report - YYYY-MM-DD.csv`

### Examples

* **Prompt for project ID** and default filename:

  ```bash
  python prolific_project_cost.py
  ```
* **Specify project ID & output path**:

  ```bash
  python prolific_project_cost.py 67f4171a84db67b4ae80447e -o reports/my_report.csv
  ```

## Output

The script writes a CSV with columns:

| study\_name | internal\_name | study\_id | published\_at | total\_available\_places | estimated\_completion\_time | average\_completion\_time | intended\_reward\_per\_hour | average\_reward\_per\_hour | total\_study\_hours | total\_study\_rewards | total\_study\_cost |
| ----------- | -------------- | --------- | ------------- | ------------------------ | --------------------------- | ------------------------- | --------------------------- | -------------------------- | ------------------- | --------------------- | ------------------ |

Each row corresponds to one study in the specified Prolific project.
