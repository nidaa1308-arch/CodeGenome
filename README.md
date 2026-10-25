# TaskTangle — Smart Task Dependency and Scheduling Analyzer

TaskTangle is a Streamlit application that uses Discrete Mathematics to help users manage task dependencies, build valid schedules, and understand project impact.

## Three team modules

1. **Dependency Manager** — models tasks as sets and dependency relations, visualizes a directed graph, and detects/prevents cycles.
2. **Smart Schedule Planner** — calculates topological order, earliest/latest times, slack, critical path, timeline, and what-if duration changes.
3. **Readiness & Impact Analyzer** — evaluates prerequisite logic, explains transitive dependencies, and identifies downstream tasks affected by a change.

The Dashboard, Projects, Task Manager, Dependency Network, Schedule Planner, Readiness & Impact, Reports, and Settings all work with the same project data.

## Run the application

1. Open this folder in VS Code.
2. Install Python 3.10 or newer if needed.
3. Open the VS Code terminal in this folder.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the website:

   ```bash
   streamlit run app.py
   ```

Streamlit will show a local URL, usually `http://localhost:8501`.

## Save and preserve your work

Projects, tasks, and dependencies are saved in `tasktangle.db` beside `app.py`. The database schema is compatible with the earlier TaskTangle version.

If updating an existing installation, **make a backup copy of `tasktangle.db` first**, then replace only `app.py` and `requirements.txt`. Keep your existing `tasktangle.db` in the same folder. Do not delete it if you want to preserve your projects.

The ZIP package does not include a database file, so it will not overwrite existing project data.

## Notes

- A valid schedule requires an acyclic dependency graph.
- The critical-path estimate assumes fixed task durations and the defined dependencies; it does not model limited staff/resources or calendar weekends.
- What-if calculations do not change saved task durations.
