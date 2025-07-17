# Match Scheduling System (AREENA Take-Home Challenge) ⚽

This project implements a lightweight API to manage sports match schedules, focusing on essential functionalities and critical business rules like preventing double-booking for teams. The goal is to demonstrate the ability to build, test, and set up continuous integration for a Python microservice with GraphQL.

---

## 🚀 Tech Stack

* **Python 3.9:** Primary programming language.
* **Flask:** Web microframework for building the API.
* **GraphQL:** Query language for APIs.
* **Graphene:** Python library for building GraphQL APIs.
* **Graphene-SQLAlchemy:** Graphene integration with SQLAlchemy for ORM mapping.
* **SQLAlchemy:** ORM (Object-Relational Mapper) for database interaction.
* **Flask-SQLAlchemy:** Extension to simplify SQLAlchemy usage with Flask.
* **SQLite:** Lightweight relational database (for local development and in-memory testing).
* **Pytest:** Testing framework for ensuring code quality.
* **GitHub Actions:** For Continuous Integration (CI) automation.

---

## ✨ Implemented Functionalities

The GraphQL API offers the following match and team management operations:

### Data Models
* `Team`: Represents a sports team (`id`, `name`).
* `Match`: Represents a match, with home and away teams, and start/end times (`id`, `home_team`, `away_team`, `start_time`, `end_time`).

### Queries (Read Operations)
* `allTeams`: Returns a list of all teams.
* `teamByName(name: String!)`: Returns a specific team by its name.
* `allMatches`: Returns a list of all scheduled matches.
* `matchById(id: Int!)`: Returns a specific match by its ID.

### Mutations (Write Operations)
* `createMatch(input: CreateMatchInput!)`: Schedules a new match.
    * **Constraint:** Ensures that **no team is double-booked** for the same time slot (prevents time overlaps).
    * **Validations:** Prevents home and away teams from being the same, and ensures start time is before end time.
* `deleteMatch(id: Int!)`: Deletes an existing match by its ID.
* `swapTeams(input: SwapTeamsInput!)`: Swaps teams between an existing match.
    * **Constraint:** The "double-booking" validation is **re-applied** for the new teams, ensuring they don't conflict with other existing games at the match's time.

---

## 🛠️ How to Run the Project Locally

Follow these steps to set up and run the API on your machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/areena-match-scheduler.git](https://github.com/YOUR_USERNAME/areena-match-scheduler.git) # Replace with your username and repo name
    cd areena-match-scheduler
    ```

2.  **Create and activate the virtual environment (Python 3.9):**
    ```bash
    python3.9 -m venv .venv_py39
    # On Windows (PowerShell):
    .\.venv_py39\Scripts\Activate.ps1
    # On Linux/macOS:
    source ./.venv_py39/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create the local database directory:**
    *The SQLite database will be created in `C:\temp_db_areena\site.db`.*
    ```bash
    mkdir C:\temp_db_areena # Create this folder manually before starting the app
    ```
    *(**Note:** The DB path is configured in `config.py`. In a production environment, a persistent database like MongoDB or PostgreSQL would be used, and the URI configured via environment variables.)*

5.  **Start the Flask server:**
    ```bash
    python app.py
    ```

6.  **Initialize the database and add test teams:**
    * Access `http://127.0.0.1:5000/init-db` in your browser.
    * You should see a success message like `{"message": "Database initialized and test teams added!"}`.
    * "Team Alpha", "Team Beta", "Team Gamma", "Team Delta" will be added as test teams.

7.  **Access GraphiQL (API testing environment):**
    * Open `http://127.0.0.1:5000/graphql` in your browser.
    * You can use this interface to explore the schema (`Docs` button in the top right) and execute queries and mutations.

---

## ✅ How to Run Tests

To execute the automated test suite:

1.  **Activate your virtual environment** (if not already active).
2.  **From the project root**, run Pytest:
    ```bash
    pytest -s
    ```
    *All create, delete, and swap match tests (including conflict validation) should pass.*

---

## 🌐 Continuous Integration (CI) with GitHub Actions

This project is configured with a basic CI workflow using GitHub Actions.

* The configuration file is located at `.github/workflows/ci.yml`.
* Whenever a `push` or `pull request` is made to the `main` branch, the tests (`pytest`) will automatically run in an Ubuntu environment with Python 3.9.
* You can monitor the status of runs in the "Actions" tab of the GitHub repository.

---

## 🧠 Assumptions & Challenges Faced

### Assumptions Made
* Teams are identified by a unique `id` and a `name`.
* A match is defined by two teams (`home_team`, `away_team`) and a time interval (`start_time`, `end_time`).
* The "double-booking" rule is the primary scheduling constraint.
* Time conflicts are based on any overlap of `start_time` and `end_time`.
* For the initial solution, business logic was placed directly within mutations for simplicity, but ideally, it would be moved to a dedicated service layer.

### Notable Challenges & Solutions
1.  **Graphene Compatibility with Python 3.11+:**
    * **Challenge:** `Flask-GraphQL` and its dependencies (`graphql-server`) exhibited incompatibilities (`ImportError: MutableMapping`) with Python 3.11 due to their inactive maintenance.
    * **Solution:** It was necessary to **downgrade Python to 3.9** and pin specific versions (`Flask-GraphQL==2.0.0`, `graphene==2.1.9`, `graphql-server-core==1.2.0`) to ensure compatibility.
2.  **`AssertionError: Found different types with the same name in the schema: Output, Output.`:**
    * **Challenge:** Mutations with identically named nested `Output` classes (`Output` by default) caused a schema naming conflict in Graphene.
    * **Solution:** Explicitly define a **unique `name`** for each `Output` class within its `class Meta` (e.g., `CreateMatchPayload`, `DeleteMatchPayload`).
3.  **`sqlite3.OperationalError: unable to open database file` in Local Development (Windows):**
    * **Challenge:** SQLAlchemy failed to create/open the `site.db` file in certain paths (like the original `Desktop/Backup/...`), even with seemingly correct permissions and existing `instance` folder. This issue persisted despite extensive troubleshooting attempts including:
        * Verifying explicit folder permissions (`Full Control` for `Everyone`).
        * Disabling anti-ransomware protection (`Windows Defender Controlled Folder Access`).
        * Checking for lingering `python.exe` processes.
        * Trying to create the DB via a separate script.
    * **Solution:** The most effective workaround was to **change the `SQLALCHEMY_DATABASE_URI` to a simpler and more "permissive" path** like `C:\temp_db_areena\site.db`. This suggests an underlying sensitivity in the Windows file system or security policies regarding nested/complex paths for SQLite database file creation.

---

## 🚀 Preparation for the Follow-Up Call

I am prepared to discuss the following points during the technical conversation:

* **Design Decisions and Code Walkthrough:** I can walk you through the project structure, the data models (Team, Match) with SQLAlchemy, how Graphene types are mapped, and the implementation of queries and mutations, including the business logic for double-booking constraints.
* **Tradeoffs and Limitations:** I can discuss why certain choices were made (e.g., SQLite for local dev, specific Graphene versions for Python 3.9 compatibility) and the limitations encountered (e.g., the persistent SQLite `OperationalError` and its workaround).
* **Extending Functionality / Adding a New Feature Live:** I am ready to implement a new feature live on screen. A good candidate for this would be:
    * **Adding a Query to List Matches by a Specific Team ID:** This would demonstrate adding a new query field, filtering data with SQLAlchemy, and returning a list of related objects.
    * **Updating an Existing Match's Time:** This would be a more complex mutation, showcasing the reuse of the `check_team_availability` logic for re-validation.
* **Discussion on Testing:** I can elaborate on the current test suite, its coverage, and discuss in detail how I would improve test quality, including:
    * Adding more **edge cases** for time overlaps.
    * Implementing **parameterized tests** (`pytest.mark.parametrize`) for comprehensive validation.
    * Structuring **unit tests** (e.g., by creating a `services/match_service.py` layer for business logic isolation).
    * Discussing the difference between unit, integration, and end-to-end tests, mocking, and stubbing.
* **QA/DevOps Mindset:** I can discuss how this project aligns with a QA/DevOps role, focusing on ensuring code quality, reliability, CI automation, and problem-solving.
