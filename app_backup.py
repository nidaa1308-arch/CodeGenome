import csv
import io
import sqlite3
from datetime import date
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DB_PATH = Path(__file__).with_name("tasktangle.db")

st.set_page_config(page_title="TaskTangle", layout="wide", initial_sidebar_state="expanded")

# ------------------------------ Styling -------------------------------------
st.markdown("""
<style>
:root { --ink:#17233b; --muted:#69758b; --line:#e7ebf2; --blue:#315efb; --teal:#159d91; --paper:#f7f9fc; }
.stApp { background:var(--paper); color:var(--ink); }
.block-container { padding-top:1.6rem; padding-bottom:3rem; max-width:1450px; }
section[data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top:1.5rem; }
h1,h2,h3 { color:var(--ink); letter-spacing:-.025em; }
h1 { font-size:2rem !important; font-weight:750 !important; }
h2 { font-size:1.4rem !important; font-weight:700 !important; }
h3 { font-size:1.05rem !important; font-weight:700 !important; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:14px; padding:16px 18px; }
[data-testid="stMetricLabel"] { color:var(--muted); }
[data-testid="stMetricValue"] { color:var(--ink); }
div[data-testid="stForm"] { background:#fff; border:1px solid var(--line); border-radius:14px; padding:18px; }
.stButton > button, .stDownloadButton > button { border-radius:9px; font-weight:600; min-height:2.5rem; }
.stButton > button[kind="primary"] { background:var(--blue); border-color:var(--blue); }
.panel { background:#fff; border:1px solid var(--line); border-radius:14px; padding:18px 20px; margin-bottom:12px; }
.eyebrow { color:var(--muted); font-size:.78rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase; }
.small-note { color:var(--muted); font-size:.9rem; }
.module-tag { display:inline-block; padding:5px 9px; border-radius:7px; background:#edf2ff; color:#315efb; font-size:.78rem; font-weight:700; }
hr { border-color:var(--line); }
</style>
""", unsafe_allow_html=True)

# ------------------------------ Database ------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    # Schema deliberately matches the earlier TaskTangle version so existing databases remain usable.
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            start_date TEXT DEFAULT '',
            deadline TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            duration REAL NOT NULL DEFAULT 1,
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Pending',
            assignee TEXT DEFAULT '',
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS dependencies (
            task_id INTEGER NOT NULL,
            predecessor_id INTEGER NOT NULL,
            PRIMARY KEY(task_id, predecessor_id),
            FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY(predecessor_id) REFERENCES tasks(id) ON DELETE CASCADE
        );
        """)


def query_all(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def execute(sql, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid


def load_projects():
    return query_all("SELECT * FROM projects ORDER BY id DESC")


def load_tasks(project_id):
    return query_all("SELECT * FROM tasks WHERE project_id=? ORDER BY id", (project_id,))


def load_dependencies(project_id):
    return query_all("SELECT d.task_id, d.predecessor_id FROM dependencies d JOIN tasks t ON t.id=d.task_id WHERE t.project_id=?", (project_id,))


def seed_sample_project():
    existing = query_all("SELECT id FROM projects WHERE name=?", ("Website Launch Demo",))
    if existing:
        return existing[0]["id"]
    pid = execute("INSERT INTO projects(name, description, start_date, deadline) VALUES(?,?,?,?)",
                  ("Website Launch Demo", "A sample project showing how task dependencies affect a real schedule.", str(date.today()), ""))
    sample = [
        ("Research requirements", "Collect requirements and confirm the project scope.", 2, "High", "Completed", "Person 1"),
        ("Plan the design", "Create the structure and visual plan.", 3, "Medium", "Pending", "Person 1"),
        ("Build the application", "Implement the main features.", 4, "High", "Pending", "Person 2"),
        ("Test the application", "Check the main workflows and fix issues.", 2, "High", "Pending", "Person 3"),
        ("Prepare final submission", "Package the project and prepare the demonstration.", 1, "Medium", "Pending", "Person 3"),
    ]
    ids = []
    for name, desc, duration, priority, status, assignee in sample:
        ids.append(execute("INSERT INTO tasks(project_id,name,description,duration,priority,status,assignee) VALUES(?,?,?,?,?,?,?)",
                           (pid, name, desc, duration, priority, status, assignee)))
    for task, predecessor in [(ids[2], ids[0]), (ids[2], ids[1]), (ids[3], ids[2]), (ids[4], ids[3])]:
        execute("INSERT OR IGNORE INTO dependencies(task_id, predecessor_id) VALUES(?,?)", (task, predecessor))
    return pid


init_db()
if not load_projects():
    seed_sample_project()

# ------------------------------ Graph logic ---------------------------------
def build_graph(tasks, dependencies):
    graph = nx.DiGraph()
    for task in tasks:
        graph.add_node(int(task["id"]), name=task["name"], duration=float(task["duration"]),
                       status=task["status"], priority=task["priority"], assignee=task["assignee"] or "Unassigned")
    for dep in dependencies:
        predecessor, task = int(dep["predecessor_id"]), int(dep["task_id"])
        if predecessor in graph and task in graph:
            graph.add_edge(predecessor, task)
    return graph


def schedule_graph(graph):
    if not nx.is_directed_acyclic_graph(graph):
        return None
    order = list(nx.topological_sort(graph))
    es, ef = {}, {}
    for node in order:
        es[node] = max((ef[p] for p in graph.predecessors(node)), default=0.0)
        ef[node] = es[node] + graph.nodes[node]["duration"]
    project_duration = max(ef.values(), default=0.0)
    lf, ls = {}, {}
    for node in reversed(order):
        lf[node] = min((ls[s] for s in graph.successors(node)), default=project_duration)
        ls[node] = lf[node] - graph.nodes[node]["duration"]
    slack = {node: round(ls[node] - es[node], 6) for node in order}
    critical = {node for node in order if abs(slack[node]) < 1e-6}
    return {"order": order, "es": es, "ef": ef, "ls": ls, "lf": lf, "slack": slack,
            "duration": project_duration, "critical": critical}


def graph_figure(graph, critical=None):
    critical = critical or set()
    if len(graph) == 0:
        return go.Figure().update_layout(title="Add tasks to see their dependency network")
    if nx.is_directed_acyclic_graph(graph):
        order = list(nx.topological_sort(graph))
        layers = {}
        for node in order:
            layers[node] = max((layers[p] + 1 for p in graph.predecessors(node)), default=0)
    else:
        layers = {node: i % 3 for i, node in enumerate(graph.nodes())}
    by_layer = {}
    for node, layer in layers.items():
        by_layer.setdefault(layer, []).append(node)
    positions = {}
    for layer, nodes in by_layer.items():
        for index, node in enumerate(nodes):
            positions[node] = (layer, -index + (len(nodes)-1)/2)
    edge_x, edge_y = [], []
    for u, v in graph.edges():
        x0, y0 = positions[u]; x1, y1 = positions[v]
        edge_x += [x0, x1, None]; edge_y += [y0, y1, None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1.5, color="#b7c1d4"), hoverinfo="none"))
    arrow_annotations = []
    for u, v in graph.edges():
        x0, y0 = positions[u]; x1, y1 = positions[v]
        arrow_annotations.append(dict(x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
                                      showarrow=True, arrowhead=2, arrowsize=1.1, arrowwidth=1.2, arrowcolor="#9aa8bd",
                                      standoff=15, startstandoff=14))
    node_x = [positions[n][0] for n in graph.nodes()]
    node_y = [positions[n][1] for n in graph.nodes()]
    node_text = [f"{graph.nodes[n]['name']}<br>Duration: {graph.nodes[n]['duration']:g} days<br>Status: {graph.nodes[n]['status']}" for n in graph.nodes()]
    node_colors = ["#159d91" if n in critical else ("#315efb" if graph.nodes[n]["status"] == "Completed" else "#8b9bb4") for n in graph.nodes()]
    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text", text=[graph.nodes[n]["name"] for n in graph.nodes()],
                             textposition="bottom center", hovertext=node_text, hoverinfo="text",
                             marker=dict(size=28, color=node_colors, line=dict(width=2, color="#ffffff"))))
    fig.update_layout(height=max(380, 100*len(by_layer)), margin=dict(l=15,r=15,t=20,b=35), showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="white", xaxis=dict(visible=False), yaxis=dict(visible=False),
                      annotations=arrow_annotations + [dict(x=0.01,y=1.04,xref="paper",yref="paper",text="Blue: completed  ·  Teal: critical path  ·  Grey: other tasks",showarrow=False,font=dict(size=11,color="#69758b"))])
    return fig


def get_predecessor_names(task_id, graph):
    return [graph.nodes[n]["name"] for n in graph.predecessors(task_id)]


def get_downstream(graph, task_id):
    return nx.descendants(graph, task_id) if task_id in graph else set()


def task_frame(tasks):
    return pd.DataFrame([{"ID": t["id"], "Task": t["name"], "Duration (days)": t["duration"], "Priority": t["priority"],
                          "Status": t["status"], "Assignee": t["assignee"] or "Unassigned"} for t in tasks])

# ------------------------------ Sidebar -------------------------------------
with st.sidebar:
    st.markdown("<div style='font-size:1.5rem;font-weight:800;letter-spacing:-.04em;color:#17233b'>TaskTangle</div><div class='small-note'>Plan work with clarity.</div>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("WORKSPACE", ["Dashboard", "My Projects", "Task Manager", "Dependency Network", "Schedule Planner", "Readiness & Impact", "Project Reports", "Settings"], label_visibility="collapsed")
    st.divider()
    st.markdown("<div class='eyebrow'>TEAM MODULES</div>", unsafe_allow_html=True)
    st.markdown("**01 · Dependency Manager**  \n<span class='small-note'>Sets, relations and graph modelling</span>", unsafe_allow_html=True)
    st.markdown("**02 · Smart Schedule Planner**  \n<span class='small-note'>Topological order and critical path</span>", unsafe_allow_html=True)
    st.markdown("**03 · Readiness & Impact Analyzer**  \n<span class='small-note'>Logic and change impact</span>", unsafe_allow_html=True)
    st.divider()
    st.caption("Your projects are saved locally.")

projects = load_projects()
if not projects:
    st.warning("Create a project to get started.")
    st.stop()
labels = [f"{p['name']}  ·  #{p['id']}" for p in projects]
if "active_project_id" not in st.session_state or st.session_state.active_project_id not in [p["id"] for p in projects]:
    st.session_state.active_project_id = projects[0]["id"]
def_idx = next((i for i,p in enumerate(projects) if p["id"] == st.session_state.active_project_id), 0)
selected_label = st.sidebar.selectbox("ACTIVE PROJECT", labels, index=def_idx, key="active_project_select")
project = projects[labels.index(selected_label)]
st.session_state.active_project_id = project["id"]
tasks = load_tasks(project["id"])
dependencies = load_dependencies(project["id"])
graph = build_graph(tasks, dependencies)
schedule = schedule_graph(graph)
task_by_id = {int(t["id"]): t for t in tasks}
completed_ids = {int(t["id"]) for t in tasks if t["status"] == "Completed"}

# ------------------------------ Dashboard -----------------------------------
if page == "Dashboard":
    st.markdown("<div class='eyebrow'>PROJECT OVERVIEW</div>", unsafe_allow_html=True)
    st.title(project["name"])
    st.write(project["description"] or "A clear view of your work, dependencies, and next steps.")
    total = len(tasks); done = len(completed_ids); blocked = sum(1 for t in tasks if any(p not in completed_ids for p in graph.predecessors(int(t["id"]))) and t["status"] != "Completed")
    progress = int(done / total * 100) if total else 0
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total tasks", total)
    m2.metric("Completed", done, f"{progress}% complete")
    m3.metric("Blocked tasks", blocked)
    m4.metric("Estimated duration", f"{schedule['duration']:g} days" if schedule else "Unavailable")
    st.progress(progress/100 if total else 0)
    left,right = st.columns([1.5,1])
    with left:
        st.subheader("Dependency network")
        st.plotly_chart(graph_figure(graph, schedule["critical"] if schedule else set()), use_container_width=True, config={"displayModeBar":False})
    with right:
        st.subheader("What needs attention")
        if not tasks:
            st.info("Add your first task in Task Manager to begin.")
        else:
            blocked_tasks = [t for t in tasks if t["status"] != "Completed" and any(p not in completed_ids for p in graph.predecessors(int(t["id"]))) ]
            if blocked_tasks:
                for t in blocked_tasks[:5]:
                    missing = [graph.nodes[p]["name"] for p in graph.predecessors(int(t["id"])) if p not in completed_ids]
                    st.markdown(f"**{t['name']}**  \nWaiting for: {', '.join(missing)}")
            else:
                st.success("No tasks are currently blocked by unfinished prerequisites.")
            if schedule:
                critical_names = [graph.nodes[n]["name"] for n in schedule["order"] if n in schedule["critical"]]
                st.markdown("**Tasks determining the finish date**")
                st.write(" → ".join(critical_names) if critical_names else "No critical tasks yet.")
            elif tasks:
                st.error("A circular dependency exists. Open Dependency Network to resolve it.")
    st.subheader("Task status")
    if tasks:
        st.dataframe(task_frame(tasks), use_container_width=True, hide_index=True)
    else:
        st.info("Your project is ready. Add tasks to start planning.")

# ------------------------------ Projects ------------------------------------
elif page == "My Projects":
    st.title("My Projects")
    st.write("Keep each piece of work organised in its own workspace.")
    with st.expander("Create a project", expanded=not bool(tasks)):
        with st.form("create_project_form", clear_on_submit=True):
            name = st.text_input("Project name", placeholder="For example, College Event Website")
            description = st.text_area("What is this project about?", height=90)
            c1,c2 = st.columns(2)
            start = c1.date_input("Start date", value=date.today())
            has_deadline = c2.checkbox("Set a deadline")
            deadline = c2.date_input("Deadline", value=date.today()) if has_deadline else None
            submitted = st.form_submit_button("Create project", type="primary")
            if submitted:
                if not name.strip(): st.error("Give your project a name first.")
                elif deadline and deadline < start: st.error("The deadline cannot be before the start date.")
                else:
                    execute("INSERT INTO projects(name,description,start_date,deadline) VALUES(?,?,?,?)", (name.strip(), description.strip(), str(start), str(deadline) if deadline else ""))
                    st.success("Project created.")
                    st.rerun()
    st.subheader("Your workspaces")
    for p in projects:
        ptasks = load_tasks(p["id"]); done_count = sum(t["status"] == "Completed" for t in ptasks)
        with st.container(border=True):
            c1,c2,c3 = st.columns([3,1,1])
            c1.markdown(f"**{p['name']}**")
            c1.caption(p["description"] or "No description added.")
            c2.metric("Tasks", len(ptasks))
            c3.metric("Completed", f"{done_count}/{len(ptasks)}")
            if c1.button("Open project", key=f"open_{p['id']}"):
                st.session_state.active_project_id = p["id"]
                st.rerun()
            with st.expander(f"Edit or remove {p['name']}"):
                with st.form(f"edit_project_{p['id']}"):
                    new_name = st.text_input("Name", value=p["name"])
                    new_desc = st.text_area("Description", value=p["description"] or "")
                    new_deadline = st.text_input("Deadline (YYYY-MM-DD, optional)", value=p["deadline"] or "")
                    save = st.form_submit_button("Save changes")
                    if save:
                        execute("UPDATE projects SET name=?, description=?, deadline=? WHERE id=?", (new_name.strip() or p["name"], new_desc.strip(), new_deadline.strip(), p["id"]))
                        st.success("Project updated."); st.rerun()
                if len(projects) > 1 and st.button("Delete this project and its tasks", key=f"delete_project_{p['id']}"):
                    execute("DELETE FROM projects WHERE id=?", (p["id"],))
                    st.rerun()

# ------------------------------ Task Manager -------------------------------
elif page == "Task Manager":
    st.markdown("<div class='eyebrow'>MODULE 01 · DEPENDENCY MANAGER</div>", unsafe_allow_html=True)
    st.title("Task Manager")
    st.write("Create the work items first. Dependencies can then describe what needs to happen before each task can begin.")
    with st.expander("Add a task", expanded=not bool(tasks)):
        with st.form("add_task_form", clear_on_submit=True):
            name = st.text_input("Task name", placeholder="For example, Design database")
            description = st.text_area("Description", height=75)
            c1,c2,c3 = st.columns(3)
            duration = c1.number_input("Estimated duration (days)", min_value=0.25, value=1.0, step=0.25)
            priority = c2.selectbox("Priority", ["Low", "Medium", "High"])
            status = c3.selectbox("Status", ["Pending", "In Progress", "Completed"])
            assignee = st.text_input("Assigned to", placeholder="Name or team member")
            add = st.form_submit_button("Add task", type="primary")
            if add:
                if not name.strip(): st.error("Enter a task name.")
                elif any(t["name"].strip().casefold() == name.strip().casefold() for t in tasks): st.error("A task with that name already exists in this project.")
                else:
                    execute("INSERT INTO tasks(project_id,name,description,duration,priority,status,assignee) VALUES(?,?,?,?,?,?,?)", (project["id"],name.strip(),description.strip(),duration,priority,status,assignee.strip()))
                    st.success("Task added to this project."); st.rerun()
    st.subheader("Current tasks")
    if not tasks:
        st.info("No tasks yet. Add one above to get started.")
    for t in tasks:
        with st.expander(f"{t['name']}  ·  {t['status']}  ·  {float(t['duration']):g} days"):
            with st.form(f"edit_task_{t['id']}"):
                new_name = st.text_input("Task name", value=t["name"])
                new_desc = st.text_area("Description", value=t["description"] or "")
                c1,c2,c3 = st.columns(3)
                new_duration = c1.number_input("Duration (days)", min_value=0.25, value=float(t["duration"]), step=0.25, key=f"dur_{t['id']}")
                new_priority = c2.selectbox("Priority", ["Low","Medium","High"], index=["Low","Medium","High"].index(t["priority"]), key=f"pri_{t['id']}")
                new_status = c3.selectbox("Status", ["Pending","In Progress","Completed"], index=["Pending","In Progress","Completed"].index(t["status"]), key=f"status_{t['id']}")
                new_assignee = st.text_input("Assigned to", value=t["assignee"] or "")
                save = st.form_submit_button("Save task")
                if save:
                    if not new_name.strip(): st.error("Task name cannot be empty.")
                    else:
                        execute("UPDATE tasks SET name=?,description=?,duration=?,priority=?,status=?,assignee=? WHERE id=?", (new_name.strip(),new_desc.strip(),new_duration,new_priority,new_status,new_assignee.strip(),t["id"]))
                        st.success("Task updated."); st.rerun()
            if st.button("Delete task", key=f"delete_task_{t['id']}"):
                execute("DELETE FROM tasks WHERE id=?", (t["id"],)); st.rerun()
    st.markdown("#### How the data is modelled")
    task_set = {t["name"] for t in tasks}
    completed_set = {t["name"] for t in tasks if t["status"] == "Completed"}
    st.markdown(f"All tasks form the set **T** with {len(task_set)} element(s). The completed-task subset currently contains {len(completed_set)} element(s).")
    st.code("T = {" + ", ".join(repr(x) for x in sorted(task_set)) + "}\nCompleted = {" + ", ".join(repr(x) for x in sorted(completed_set)) + "}", language="text")

# ------------------------------ Dependency Network -------------------------
elif page == "Dependency Network":
    st.markdown("<div class='eyebrow'>MODULE 01 · DEPENDENCY MANAGER</div>", unsafe_allow_html=True)
    st.title("Dependency Network")
    st.write("Connect tasks to show what must happen first. Each arrow points from a prerequisite to the task that depends on it.")
    if tasks:
        task_options = {int(t["id"]): t["name"] for t in tasks}
        with st.form("add_dependency_form"):
            c1,c2 = st.columns(2)
            predecessor = c1.selectbox("Prerequisite task", list(task_options), format_func=lambda x: task_options[x])
            dependent = c2.selectbox("Task that waits", list(task_options), format_func=lambda x: task_options[x])
            add_dep = st.form_submit_button("Add dependency", type="primary")
            if add_dep:
                if predecessor == dependent: st.error("A task cannot depend on itself.")
                elif graph.has_edge(predecessor, dependent): st.info("That dependency already exists.")
                else:
                    graph.add_edge(predecessor, dependent)
                    if not nx.is_directed_acyclic_graph(graph):
                        st.error("This would create a cycle, so the dependency was not saved.")
                    else:
                        execute("INSERT OR IGNORE INTO dependencies(task_id,predecessor_id) VALUES(?,?)", (dependent, predecessor))
                        st.success("Dependency added."); st.rerun()
        st.plotly_chart(graph_figure(graph, schedule["critical"] if schedule else set()), use_container_width=True, config={"displayModeBar":False})
        st.subheader("Current dependency relations")
        dep_rows = [{"Prerequisite": graph.nodes[int(d["predecessor_id"])]["name"], "Must happen before": graph.nodes[int(d["task_id"])]["name"]} for d in dependencies]
        if dep_rows: st.dataframe(pd.DataFrame(dep_rows), use_container_width=True, hide_index=True)
        else: st.info("There are no dependency arrows yet. Independent tasks can still be scheduled.")
        if dependencies:
            with st.expander("Remove a dependency"):
                choices = {f"{graph.nodes[int(d['predecessor_id'])]['name']} → {graph.nodes[int(d['task_id'])]['name']}": (int(d["task_id"]), int(d["predecessor_id"])) for d in dependencies}
                chosen = st.selectbox("Choose relationship", list(choices))
                if st.button("Remove selected dependency"):
                    task_id, pred_id = choices[chosen]
                    execute("DELETE FROM dependencies WHERE task_id=? AND predecessor_id=?", (task_id,pred_id)); st.rerun()
        st.subheader("What the network tells you")
        st.markdown("- **Set:** the vertices represent the tasks in this project.\n- **Relation:** every arrow is an ordered pair (prerequisite, dependent task).\n- **Cycle check:** a valid schedule requires the dependency network to be acyclic.")
        if nx.is_directed_acyclic_graph(graph):
            st.success(f"The network is valid. It contains {graph.number_of_nodes()} task(s) and {graph.number_of_edges()} dependency relationship(s).")
        else:
            st.error("The network contains a cycle. Remove one of the relationships in that loop before scheduling.")
    else:
        st.info("Add tasks in Task Manager before building the dependency network.")

# ------------------------------ Schedule Planner ----------------------------
elif page == "Schedule Planner":
    st.markdown("<div class='eyebrow'>MODULE 02 · SMART SCHEDULE PLANNER</div>", unsafe_allow_html=True)
    st.title("Schedule Planner")
    st.write("Turn the dependency network into a valid order of work, an estimated completion time, and a critical path.")
    if not tasks:
        st.info("Add tasks and dependencies first.")
    elif not schedule:
        st.error("A schedule cannot be calculated while the network contains a cycle. Open Dependency Network and resolve it.")
    else:
        c1,c2,c3 = st.columns(3)
        c1.metric("Estimated project duration", f"{schedule['duration']:g} days")
        c2.metric("Critical-path tasks", len(schedule["critical"]))
        c3.metric("Valid task order", f"{len(schedule['order'])} tasks")
        st.subheader("A valid order of work")
        st.write(" → ".join(graph.nodes[n]["name"] for n in schedule["order"]))
        st.caption("Tasks without a dependency between them may be completed in either order. This order respects every defined prerequisite.")
        rows=[]
        for n in schedule["order"]:
            rows.append({"Task":graph.nodes[n]["name"],"Duration (days)":graph.nodes[n]["duration"],"Earliest start":round(schedule["es"][n],2),"Earliest finish":round(schedule["ef"][n],2),"Latest start":round(schedule["ls"][n],2),"Slack (days)":round(schedule["slack"][n],2),"Critical path":"Yes" if n in schedule["critical"] else "No"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.subheader("Timeline")
        fig=go.Figure()
        for n in schedule["order"]:
            start=schedule["es"][n]; duration=graph.nodes[n]["duration"]
            fig.add_trace(go.Bar(name=graph.nodes[n]["name"], x=[duration], y=[graph.nodes[n]["name"]], orientation="h", base=start,
                                 marker_color="#159d91" if n in schedule["critical"] else "#9aabc4", hovertemplate=f"{graph.nodes[n]['name']}<br>Starts: {start:g}<br>Duration: {duration:g} days<extra></extra>"))
        fig.update_layout(barmode="overlay", height=max(320,45*len(tasks)), xaxis_title="Project day", showlegend=False, paper_bgcolor="white", plot_bgcolor="white", margin=dict(l=10,r=15,t=10,b=35))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        critical_names=[graph.nodes[n]["name"] for n in schedule["order"] if n in schedule["critical"]]
        st.markdown("#### Why these tasks matter")
        st.write("The critical path is the longest-duration path through the dependency network. With the current durations and dependencies, its tasks determine the earliest possible project finish.")
        st.markdown(" → ".join(critical_names))
        with st.expander("How the recurrence works"):
            st.latex(r"EF(v)=d(v)+\max_{u\in Pred(v)} EF(u)")
            st.write("For each task, the earliest finish equals its own duration plus the latest earliest-finish time among its prerequisites. A task with no prerequisites starts at day zero. Processing tasks in topological order ensures the prerequisite values are known first.")
        st.subheader("Try a duration change")
        selected_task=st.selectbox("Choose a task", schedule["order"], format_func=lambda n:graph.nodes[n]["name"], key="whatif_task")
        new_duration=st.number_input("Test duration (days)", min_value=0.25, value=float(graph.nodes[selected_task]["duration"]), step=0.25, key="whatif_duration")
        if st.button("Compare schedule", type="primary"):
            test_graph=graph.copy(); test_graph.nodes[selected_task]["duration"]=new_duration
            test_schedule=schedule_graph(test_graph)
            change=test_schedule["duration"]-schedule["duration"]
            if abs(change)<1e-8: st.info(f"The overall estimated duration remains {schedule['duration']:g} days. This task's change does not extend the longest path.")
            elif change>0: st.warning(f"The estimated finish moves from {schedule['duration']:g} to {test_schedule['duration']:g} days — an increase of {change:g} day(s).")
            else: st.success(f"The estimated duration falls from {schedule['duration']:g} to {test_schedule['duration']:g} days — a reduction of {abs(change):g} day(s).")
            st.caption("This is a what-if calculation only. Your saved task duration has not been changed.")

# ------------------------------ Readiness & Impact --------------------------
elif page == "Readiness & Impact":
    st.markdown("<div class='eyebrow'>MODULE 03 · READINESS & IMPACT ANALYZER</div>", unsafe_allow_html=True)
    st.title("Readiness & Impact Analyzer")
    st.write("Understand why a task can start, which work is waiting, and which parts of the project may be affected by a change.")
    if not tasks:
        st.info("Add tasks and dependencies first.")
    else:
        task_id=st.selectbox("Select a task to inspect", list(task_by_id), format_func=lambda n:task_by_id[n]["name"])
        selected=task_by_id[task_id]
        predecessors=list(graph.predecessors(task_id))
        pending_predecessors=[p for p in predecessors if p not in completed_ids]
        logically_ready=all(p in completed_ids for p in predecessors)
        if selected["status"] == "Completed":
            st.success("This task is already marked completed.")
        elif logically_ready:
            st.success("This task is ready: every direct prerequisite is marked completed.")
        else:
            st.warning("This task is blocked until its prerequisites are completed.")
            st.write("Still waiting for: " + ", ".join(graph.nodes[p]["name"] for p in pending_predecessors))
        st.markdown("#### Readiness rule")
        st.latex(r"Ready(v)=\bigwedge_{u\in Pred(v)} Completed(u)")
        st.write("The AND condition is true only when every direct prerequisite is completed. If a task has no prerequisites, the condition is satisfied automatically.")
        logic_rows=[]
        for p in predecessors:
            logic_rows.append({"Prerequisite":graph.nodes[p]["name"],"Completed?":"True" if p in completed_ids else "False","Required for readiness":"Yes"})
        if logic_rows: st.dataframe(pd.DataFrame(logic_rows),use_container_width=True,hide_index=True)
        else: st.info("This task has no direct prerequisites, so dependency rules do not block it.")
        st.divider()
        st.subheader("Impact if this task changes")
        downstream=get_downstream(graph,task_id)
        downstream_names={graph.nodes[n]["name"] for n in downstream}
        critical_names={graph.nodes[n]["name"] for n in (schedule["critical"] if schedule else set())}
        overlap=downstream_names & critical_names
        a,b,c=st.columns(3)
        a.metric("Downstream tasks",len(downstream))
        b.metric("Affected critical tasks",len(overlap))
        c.metric("Direct prerequisites",len(predecessors))
        if downstream:
            st.write("Tasks that depend on this task, directly or indirectly:")
            st.write(", ".join(graph.nodes[n]["name"] for n in schedule["order"] if n in downstream) if schedule else ", ".join(sorted(downstream_names)))
        else:
            st.info("No other task currently depends on this task.")
        if overlap:
            st.warning("These downstream tasks also lie on the current critical path: " + ", ".join(sorted(overlap)) + ". They deserve particular attention if this task is delayed.")
        elif downstream:
            st.info("The downstream tasks are not currently on the critical path. A change could still matter if durations or dependencies change.")
        st.markdown("#### Set-based impact")
        st.write("The intersection below identifies tasks that are both downstream of the selected task and on the critical path.")
        st.latex(r"Impact(v)=Descendants(v)\cap CriticalPath")
        st.code("Downstream = {"+", ".join(sorted(downstream_names))+"}\nCriticalPath = {"+", ".join(sorted(critical_names))+"}\nIntersection = {"+", ".join(sorted(overlap))+"}",language="text")
        if schedule:
            with st.expander("Test a possible delay"):
                test_duration=st.number_input("Possible duration for this task (days)",min_value=0.25,value=float(selected["duration"]),step=0.25,key="impact_duration")
                if st.button("Calculate impact",type="primary"):
                    test_graph=graph.copy(); test_graph.nodes[task_id]["duration"]=test_duration
                    updated=schedule_graph(test_graph); delta=updated["duration"]-schedule["duration"]
                    st.metric("New estimated project duration",f"{updated['duration']:g} days",f"{delta:+g} days compared with current schedule")
                    if delta>0: st.warning("This change extends the estimated project finish. Review the tasks on the updated critical path.")
                    elif delta<0: st.success("This change shortens the estimated project finish under the current dependency model.")
                    else: st.info("This change does not alter the current estimated finish time.")
                    st.write("Updated critical path: " + " → ".join(graph.nodes[n]["name"] for n in updated["order"] if n in updated["critical"]))
                    st.caption("The test does not modify saved project data.")
        with st.expander("Transitive dependency explanation"):
            if nx.is_directed_acyclic_graph(graph):
                for n in schedule["order"] if schedule else graph.nodes:
                    indirect=[x for x in nx.ancestors(graph,n) if x not in predecessors] if n==task_id else []
                    if n==task_id:
                        st.write(f"Indirect prerequisites of **{graph.nodes[n]['name']}**: " + (", ".join(graph.nodes[x]["name"] for x in indirect) if indirect else "None"))
                        break
            st.write("If A must happen before B, and B must happen before C, then A is an indirect prerequisite of C. The application uses graph reachability to identify these transitive relationships.")

# ------------------------------ Reports -------------------------------------
elif page == "Project Reports":
    st.title("Project Reports")
    st.write("Export a snapshot of the project for documentation, review, or your demonstration.")
    if tasks:
        frame=task_frame(tasks)
        st.subheader("Task summary")
        st.dataframe(frame,use_container_width=True,hide_index=True)
        csv_buffer=io.StringIO(); frame.to_csv(csv_buffer,index=False)
        st.download_button("Download task list (CSV)",csv_buffer.getvalue().encode("utf-8-sig"),file_name="tasktangle_tasks.csv",mime="text/csv")
        dep_rows=[{"Prerequisite":graph.nodes[int(d["predecessor_id"])]["name"],"Dependent task":graph.nodes[int(d["task_id"])]["name"]} for d in dependencies]
        dep_frame=pd.DataFrame(dep_rows,columns=["Prerequisite","Dependent task"])
        dep_buffer=io.StringIO(); dep_frame.to_csv(dep_buffer,index=False)
        st.download_button("Download dependency list (CSV)",dep_buffer.getvalue().encode("utf-8-sig"),file_name="tasktangle_dependencies.csv",mime="text/csv")
        summary_lines=[f"TaskTangle project report: {project['name']}",f"Description: {project['description'] or 'Not provided'}",f"Tasks: {len(tasks)}",f"Completed: {len(completed_ids)}",f"Dependencies: {len(dependencies)}"]
        if schedule:
            summary_lines += [f"Estimated duration: {schedule['duration']:g} days","Valid task order: "+" -> ".join(graph.nodes[n]["name"] for n in schedule["order"]),"Critical path: "+" -> ".join(graph.nodes[n]["name"] for n in schedule["order"] if n in schedule["critical"])]
        else: summary_lines.append("Schedule unavailable: resolve dependency cycles first.")
        st.download_button("Download project summary (TXT)","\n".join(summary_lines),file_name="tasktangle_project_report.txt",mime="text/plain")
    else:
        st.info("Add tasks before exporting a report.")

# ------------------------------ Settings ------------------------------------
elif page == "Settings":
    st.title("Settings")
    st.write("Manage the active project details and sample data.")
    with st.form("settings_form"):
        project_name=st.text_input("Project name",value=project["name"])
        project_description=st.text_area("Description",value=project["description"] or "")
        project_start=st.text_input("Start date (YYYY-MM-DD)",value=project["start_date"] or "")
        project_deadline=st.text_input("Deadline (YYYY-MM-DD, optional)",value=project["deadline"] or "")
        save_settings=st.form_submit_button("Save project details",type="primary")
        if save_settings:
            if not project_name.strip(): st.error("Project name cannot be empty.")
            else:
                execute("UPDATE projects SET name=?,description=?,start_date=?,deadline=? WHERE id=?",(project_name.strip(),project_description.strip(),project_start.strip(),project_deadline.strip(),project["id"]))
                st.success("Project details saved."); st.rerun()
    st.divider()
    st.subheader("Data storage")
    st.write("Projects, tasks, and dependencies are stored in the local SQLite file named `tasktangle.db` beside `app.py`. Keep that file to preserve your work.")
    st.caption(f"Database location: {DB_PATH}")
    st.subheader("About the three modules")
    st.markdown("**01 · Dependency Manager** — models tasks as sets and dependency relations, displays a directed graph, and prevents cycles.\n\n**02 · Smart Schedule Planner** — calculates a topological order, earliest and latest times, slack, and the critical path.\n\n**03 · Readiness & Impact Analyzer** — evaluates prerequisite logic, explains transitive dependencies, and compares what-if schedule changes.")
