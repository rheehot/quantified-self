# -*- coding: utf-8 -*-

import arrow
import datetime
from dateutil import parser
import math

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.figure_factory as ff
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from data_handler import DataHandler


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config["suppress_callback_exceptions"] = True

data_handler = DataHandler()


DAILY_TAP = "daily"
WEEKLY_TAP = "weekly"
MONTHLY_TAP = "monthly"
QUATERLY_TAP = "quarterly"

tab_list = [DAILY_TAP, WEEKLY_TAP]


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "17rem",
    "padding": "2rem 1rem",
    "background-color": "#f4f7fc",
}

sidebar = html.Div(
    [
        html.H2("Quantified Self", className="display-5"),
        html.Hr(),
        html.P("BeHappy Project", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink(tab.capitalize(), href=f"/{tab}", id=f"{tab}-link")
                for tab in tab_list
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"{tab}-link", "active") for tab in tab_list], [Input("url", "pathname")]
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True
    return [pathname == f"/{tab}" for tab in tab_list]


def make_card_html(body, title_text=None, size=12):
    card_html = html.Div(
        [
            html.Div(
                [html.Div(body, className="card-body")],
                className="card mb-3 text-center",
            )
        ],
        className=f"col-sm-{size}",
    )

    if title_text is not None:
        title = html.H6(title_text, className="card-title")
        card_html.children[0].children[0].children.insert(0, title)

    return card_html


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == f"/{DAILY_TAP}":

        # Daily Dashboard
        daily_task_hour_card = make_card_html(
            [html.P("8")], title_text="Task Hour", size=2
        )

        daily_sleep_hour_card = make_card_html(
            [html.P("8")], title_text="Sleep Hour", size=2
        )

        daily_remain_hour_card = make_card_html(
            [html.P("8")], title_text="Remain Hour", size=2
        )

        daily_exercise_card = make_card_html(
            [html.P("O")], title_text="Exercise", size=2
        )

        daily_diary_card = make_card_html([html.P("O")], title_text="Diary", size=2)

        daily_bat_card = make_card_html([html.P("O")], title_text="BAT", size=2)

        # Daily - Schedule
        daily_schedule_card = make_card_html(
            [
                html.Div(
                    [
                        html.Span(
                            "Date:", style={"font-size": "1.5em", "margin-right": "5px"}
                        ),
                        dcc.DatePickerSingle(
                            id="date-picker-daily-schedule",
                            date=arrow.now().datetime,
                            max_date_allowed=arrow.now().datetime,
                        ),
                    ],
                    style={"text-align": "center"},
                ),
                dcc.Graph(id="live-daily-schedule"),
                dcc.Interval(
                    id="interval-component1",
                    interval=10 * 60 * 1000,  # every 10 mins
                    n_intervals=0,
                ),
            ]
        )

        # Daily - Calendar Heatmap
        daily_cal_heatmap_card = make_card_html(
            [
                html.Div(
                    [
                        html.Span(
                            "DateRange:",
                            style={"font-size": "1.5em", "margin-right": "5px"},
                        ),
                        dcc.DatePickerRange(
                            id="date-picker-range-calendar-heatmap",
                            first_day_of_week=1,  # Monday
                            start_date=arrow.now().shift(days=-30).datetime,
                            end_date=arrow.now().datetime,
                            max_date_allowed=arrow.now().datetime,
                        ),
                    ],
                    style={"text-align": "center"},
                ),
                dcc.Graph(id="live-calendar-heatmap"),
                dcc.Interval(
                    id="interval-component4",
                    interval=60 * 60 * 24 * 1000,  # every 1 day
                    n_intervals=0,
                ),
            ]
        )

        # Daily - Summary Chart
        daily_summary_card = make_card_html(
            [
                dcc.Graph(id="live-daily-chart"),
                dcc.Interval(
                    id="interval-component3",
                    interval=60 * 60 * 24 * 1000,  # every 1 day
                    n_intervals=0,
                ),
            ]
        )

        return html.Div(
            [
                daily_task_hour_card,
                daily_sleep_hour_card,
                daily_remain_hour_card,
                daily_exercise_card,
                daily_diary_card,
                daily_bat_card,
                daily_schedule_card,
                daily_cal_heatmap_card,
                daily_summary_card,
            ],
            className="container-fluid row",
        )

    elif pathname == f"/{WEEKLY_TAP}":

        # Weekly Dashboard
        weekly_task_total_hour_card = make_card_html(
            [html.P("51")], title_text="Total Hour", size=3
        )

        weekly_exercise_card = make_card_html(
            [html.P("5")], title_text="Exercise Count", size=3
        )

        weekly_diary_card = make_card_html(
            [html.P("5")], title_text="Diary Count", size=3
        )

        weekly_bat_card = make_card_html([html.P("5")], title_text="BAT Count", size=3)

        # Weekly Task - Stack Bar Chart
        weekly_task_card = make_card_html(
            [
                html.Div(
                    [
                        html.Span(
                            "DateRange:",
                            style={"font-size": "1.5em", "margin-right": "5px"},
                        ),
                        dcc.DatePickerRange(
                            id="date-picker-range-weekly",
                            first_day_of_week=1,  # Monday
                            start_date=arrow.now().shift(days=-30).datetime,
                            end_date=arrow.now().datetime,
                            max_date_allowed=arrow.now().datetime,
                        ),
                    ],
                    style={"text-align": "center"},
                ),
                dcc.Graph(id="live-weekly-stack-reports"),
                dcc.Interval(
                    id="interval-component2",
                    interval=60 * 60 * 24 * 1000,  # every 1 day
                    n_intervals=0,
                ),
                dcc.Graph(id="live-weekly-pie-reports"),
                dcc.Interval(
                    id="interval-component5",
                    interval=60 * 60 * 24 * 1000,  # every 1 day
                    n_intervals=0,
                ),
            ]
        )

        return html.Div(
            [
                weekly_task_total_hour_card,
                weekly_exercise_card,
                weekly_diary_card,
                weekly_bat_card,
                weekly_task_card,
            ],
            className="container-fluid row",
        )

    elif pathname == "tab-2":
        return html.Div([html.H3("Tab content 2")])


@app.callback(
    Output("live-daily-schedule", "figure"),
    [
        Input("interval-component1", "n_intervals"),
        Input("date-picker-daily-schedule", "date"),
    ],
)
def make_daily_schedule_fig(n, date):

    timedelta = arrow.now() - arrow.get(date, tzinfo="Asia/Seoul")
    days_diff = timedelta.days

    if days_diff < 0:
        pass  # Can't handle future!"
    elif days_diff == 0:
        record_data = data_handler.read_record(redownload=True)
    else:
        record_data = data_handler.read_record(days=-days_diff)

    activity_data = record_data["activity"]
    task_data = activity_data["task"]

    toggl_projects = [data["project"] for data in task_data]
    colors = {}
    for data in task_data:
        colors[data["project"]] = data["color"]

    base_date = date
    tomorrow_base_date = arrow.get(base_date).shift(days=+1).format("YYYY-MM-DD")

    df = [  # Labeling scores
        dict(Task=5, Start=base_date, Finish=base_date, Resource=toggl_projects[0]),
        dict(Task=4, Start=base_date, Finish=base_date, Resource=toggl_projects[0]),
        dict(Task=3, Start=base_date, Finish=base_date, Resource=toggl_projects[0]),
        dict(Task=2, Start=base_date, Finish=base_date, Resource=toggl_projects[0]),
        dict(Task=1, Start=base_date, Finish=base_date, Resource=toggl_projects[0]),
    ]

    # Labeling projects
    for project in toggl_projects:
        df.append(
            dict(
                Task=1,
                Start=tomorrow_base_date,
                Finish=tomorrow_base_date,
                Resource=project,
            )
        )

    for data in task_data:
        task = {
            "Task": data.get("score", 3),
            "Start": arrow.get(data["start_time"]).format("YYYY-MM-DD HH:mm:ss"),
            "Finish": arrow.get(data["end_time"]).format("YYYY-MM-DD HH:mm:ss"),
            "Resource": data["project"],
            "Description": data["description"],
        }
        df.append(task)

    fig = ff.create_gantt(
        df,
        colors=colors,
        index_col="Resource",
        title="Daily Schedule",
        group_tasks=True,
        show_colorbar=True,
        bar_width=0.3,
        showgrid_x=True,
        showgrid_y=True,
        width=1000,
        height=600,
    )

    happy_data = activity_data["happy"]

    if len(happy_data) > 0:
        xs = [arrow.get(d["time"]).format("YYYY-MM-DD HH:mm:ss") for d in happy_data]
        ys = [d["score"] - 1 for d in happy_data]

        scatter_trace = dict(
            type="scatter",
            mode="markers",
            marker=dict(size=10, color="#439C59", line=dict(width=2)),
            name="Happy",
            x=xs,
            y=ys,
        )
        fig.add_trace(scatter_trace)

    # Annotations
    annotations = []
    for index, d in enumerate(fig["data"]):
        if d["text"] is None:
            continue

        data_count = len(d["x"])
        for i in range(0, data_count, 2):

            text = d["text"][i]
            if text is None:
                continue

            start_date = d["x"][i]
            end_date = d["x"][i + 1]

            start_score = d["y"][i]
            end_score = d["y"][i + 1]

            if start_date == end_date or start_score != end_score:
                continue

            description = d["text"][i]
            project_names = list(colors.keys())

            project_name = "Empty"
            for p_name in project_names:
                if description.startswith(p_name):
                    project_name = p_name
                    break

            if type(start_date) != datetime.datetime:
                start_date = parser.parse(start_date)
            if type(end_date) != datetime.datetime:
                end_date = parser.parse(end_date)

            up_ays = [-50, -90, -70, -110]
            down_ays = [50, 90, 70, 110]

            if start_score > 2:  # large than 3
                ays = up_ays
            else:
                ays = down_ays

            ay = ays[index % len(ays)]

            annotations.append(
                go.layout.Annotation(
                    x=start_date + (end_date - start_date) / 2,
                    y=start_score,
                    xref="x",
                    yref="y",
                    text=description,
                    font=dict(family="Courier New, monospace", size=12, color="#fff"),
                    bgcolor=colors.get(project_name, "#DEDEDE"),
                    bordercolor="#666",
                    borderpad=2,
                    arrowhead=7,
                    ax=0,
                    ay=ay,
                    opacity=0.7,
                )
            )

    fig.update_layout(annotations=annotations)

    return fig


def get_base_of_range(start_date, end_date, weekday_value=0):
    # if start_date.weekday() != weekday_value:
    # start_date = start_date.shift(days=-(start_date.weekday() - weekday_value))
    if end_date.weekday() != weekday_value:
        end_date = end_date.shift(days=+(abs(end_date.weekday() - weekday_value)))

    base_dates = []
    for r in arrow.Arrow.range("day", start_date, end_date):
        if r.weekday() == weekday_value:
            base_dates.append(r)
    return base_dates


@app.callback(
    Output("live-weekly-stack-reports", "figure"),
    [
        Input("interval-component2", "n_intervals"),
        Input("date-picker-range-weekly", "start_date"),
        Input("date-picker-range-weekly", "end_date"),
    ],
)
def make_stacked_bar_fig(n, start_date, end_date):
    start_date = arrow.get(start_date)
    end_date = arrow.get(end_date)

    categories = [
        "Article",
        "Blog",
        "Book",
        "Develop",
        "Exercise",
        "Hobby",
        "Management",
        "Meeting",
        "MOOC",
        "Planning",
        "Research",
        "Review",
        "Seminar",
        "Think",
        "Empty",
    ]
    task_reports = {}

    colors = {"Empty": "#DEDEDE"}

    WEEKDAY_SUNDAY = 6
    sunday_dates = get_base_of_range(start_date, end_date, weekday_value=WEEKDAY_SUNDAY)

    for c in categories:
        task_reports[c] = [0] * len(sunday_dates)

    weekly_index = 0
    for r in arrow.Arrow.range("day", start_date, end_date):
        offset_day = (arrow.now() - r).days
        record_data = data_handler.read_record(days=-offset_day)

        for weekly_index, base_date in enumerate(sunday_dates):
            days_diff = (base_date - r).days
            if days_diff < 7 and days_diff >= 0:
                break

        activity_data = record_data.get("activity", {})
        task_data = activity_data.get("task", [])
        for t in task_data:
            project = t["project"]

            duration = (arrow.get(t["end_time"]) - arrow.get(t["start_time"])).seconds
            duration_hours = round(duration / 60 / 60, 1)

            task_reports[project][weekly_index] += duration_hours

            # Color
            if project not in colors:
                colors[project] = t["color"]

    data = []
    for category, task_report in task_reports.items():

        differ_with_last_weeks = [f"{task_report[0]} (0)"]
        for i in range(1, len(task_report)):
            last_week_task_time = task_report[i - 1]
            task_time = task_report[i]
            differ_time = round(task_time - last_week_task_time, 2)
            plus_and_minus = "+"
            if differ_time < 0:
                plus_and_minus = ""

            differ_with_last_weeks.append(
                f"{round(task_time, 2)} ({plus_and_minus}{differ_time})"
            )

        data.append(
            go.Bar(
                x=sunday_dates,
                y=task_report,
                name=category,
                marker=dict(
                    color=colors.get(category, "#DEDEDE"),
                    line=dict(color="#222", width=1),
                ),
                hovertext=differ_with_last_weeks,
                opacity=0.8,
            )
        )

    layout = go.Layout(
        autosize=True, barmode="stack", title="Weekly Task Report (Stack Bar)"
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


@app.callback(
    Output("live-weekly-pie-reports", "figure"),
    [
        Input("interval-component2", "n_intervals"),
        Input("date-picker-range-weekly", "start_date"),
        Input("date-picker-range-weekly", "end_date"),
    ],
)
def make_pie_chart_fig(n, start_date, end_date):
    start_date = arrow.get(start_date)
    end_date = arrow.get(end_date)

    categories = [
        "Article",
        "Blog",
        "Book",
        "Develop",
        "Exercise",
        "Hobby",
        "Management",
        "Meeting",
        "MOOC",
        "Planning",
        "Research",
        "Review",
        "Seminar",
        "Think",
        "Empty",
    ]
    task_reports = {}

    colors = {"Empty": "#DEDEDE"}

    WEEKDAY_SUNDAY = 6
    sunday_dates = get_base_of_range(start_date, end_date, weekday_value=WEEKDAY_SUNDAY)

    for c in categories:
        task_reports[c] = [0] * len(sunday_dates)

    weekly_index = 0
    for r in arrow.Arrow.range("day", start_date, end_date):
        offset_day = (arrow.now() - r).days
        record_data = data_handler.read_record(days=-offset_day)

        for weekly_index, base_date in enumerate(sunday_dates):
            days_diff = (base_date - r).days
            if days_diff < 7 and days_diff >= 0:
                break

        activity_data = record_data.get("activity", {})
        task_data = activity_data.get("task", [])
        for t in task_data:
            project = t["project"]

            duration = (arrow.get(t["end_time"]) - arrow.get(t["start_time"])).seconds
            duration_hours = round(duration / 60 / 60, 1)

            task_reports[project][weekly_index] += duration_hours

            # Color
            if project not in colors:
                colors[project] = t["color"]

    pie_chart_count = weekly_index + 1

    COL_COUNT = 4
    ROW_COUNT = math.ceil(pie_chart_count / COL_COUNT)

    pie_values = []
    for i in range(pie_chart_count):
        pie_values.append([])

    subplots_specs = []
    for r in range(ROW_COUNT):
        row_specs = []
        for c in range(COL_COUNT):
            row_specs.append({"type": "domain"})
        subplots_specs.append(row_specs)

    fig = make_subplots(rows=ROW_COUNT, cols=COL_COUNT, specs=subplots_specs)

    pie_colors = []
    for category, task_values in task_reports.items():
        for i, v in enumerate(task_values):
            pie_values[i].append(v)
        pie_colors.append(colors.get(category, "#DEDEDE"))

    for i, pie_value in enumerate(pie_values):
        col_index = int((i % COL_COUNT)) + 1
        row_index = int((i / COL_COUNT)) + 1
        fig.add_trace(
            go.Pie(
                labels=categories,
                values=pie_value,
                name=sunday_dates[i].format("MMM D"),
            ),
            row=row_index,
            col=col_index,
        )
    # Use `hole` to create a donut-like pie chart
    fig.update_traces(
        hole=.3, hoverinfo="label+percent+name", marker={"colors": pie_colors}
    )

    return fig


def make_weekly_dates(N):
    format_date_list = []
    now = arrow.now()
    for i in range(-(N - 1), 1, 1):
        date = now.shift(days=i)
        format_date_list.append(date.format("YYYY-MM-DD"))
    return format_date_list


@app.callback(
    Output("live-daily-chart", "figure"), [Input("interval-component3", "n_intervals")]
)
def make_scatter_line_fig(n):
    week_days = 7

    weekly_data = []
    for i in range(-(week_days - 1), 1):
        record_data = data_handler.read_record(days=i)
        if "summary" not in record_data:
            record_data = data_handler.read_record(days=i, redownload=True)
        weekly_data.append(record_data)

    dates = make_weekly_dates(week_days)

    def get_score(data, category):
        summary = data.get("summary", {})
        return summary.get(category, 0)

    attention_scores = [get_score(data, "attention") for data in weekly_data]
    happy_scores = [get_score(data, "happy") for data in weekly_data]
    productive_scores = [get_score(data, "productive") for data in weekly_data]
    sleep_scores = [get_score(data, "sleep") for data in weekly_data]
    repeat_task_scores = [get_score(data, "repeat_task") for data in weekly_data]
    total_scores = [get_score(data, "total") for data in weekly_data]

    names = ["attention", "happy", "productive", "sleep", "repeat_task", "total"]
    ys = [
        attention_scores,
        happy_scores,
        productive_scores,
        sleep_scores,
        repeat_task_scores,
        total_scores,
    ]

    # Create traces
    data = []
    for name, y in zip(names, ys):
        data.append(go.Scatter(x=dates, y=y, mode="lines+markers", name=name))

    layout = go.Layout(autosize=True, title="Summary Chart")

    fig = go.Figure(data=data, layout=layout)
    return fig


@app.callback(
    Output("live-calendar-heatmap", "figure"),
    [
        Input("interval-component4", "n_intervals"),
        Input("date-picker-range-calendar-heatmap", "start_date"),
        Input("date-picker-range-calendar-heatmap", "end_date"),
    ],
)
def make_calendar_heatmap_fig(n, start_date, end_date):
    start_date = arrow.get(start_date)
    end_date = arrow.get(end_date)

    categories = ["BAT", "Diary", "Exercise"]

    dates = []

    z = []
    for _ in categories:
        z.append([])

    for r in arrow.Arrow.range("day", start_date, end_date):
        offset_day = (arrow.now() - r).days
        record_data = data_handler.read_record(days=-offset_day)
        summary = record_data.get("summary", {})

        for i, category in enumerate(categories):
            do_category = summary.get(f"do_{category.lower()}", False)
            z[i].append(int(do_category))

        dates.append(r.format("YYYY-MM-DD"))

    categories.append("All")
    z_do_all = []

    for i in range(len(dates)):
        do_all = 0
        for item in z:
            do_all += item[i]
        z_do_all.append(do_all)
    z.append(z_do_all)

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            text=z,
            x=dates,
            y=categories,
            colorscale=[[0, "#FFFFFF"], [1, "#19410a"]],
            xgap=7,
            ygap=7,
        )
    )

    fig.update_layout(
        title="BAT, Diary, Exercise per day",
        height=300,
        xaxis={
            "tickformat": "%a-%m-%d",
            "tickangle": 75,
            "showticklabels": True,
            "dtick": 86400000.0 * 1,  # 1 day
        },
    )

    return fig


# # Selectors -> well text
# @app.callback(
# Output("well_text", "children"),
# [
# Input('url', 'value')
# ],
# )
# def update_well_text(t):
# return 100


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8000)