"""Dash App to Allow Interactivity with NAPLAN Data."""

from typing import List, Optional

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dcc, html
from dash_bootstrap_templates import load_figure_template
from plotly import graph_objs as go

load_figure_template("bootstrap")

BASE_PATH = "data"

enrolments_df = pd.read_csv(f"{BASE_PATH}/enrolments.csv")
naplan_results_df = pd.read_csv(f"{BASE_PATH}/naplan_results.csv")
recurrent_income_df = pd.read_csv(f"{BASE_PATH}/recurrent_income.csv")

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
    title="NAPLAN Analysis",
)

server = app.server

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Historical NAPLAN Performance", href="#"),
            dbc.Nav(
                [
                    dbc.NavItem(
                        dbc.Button(
                            [
                                html.Img(
                                    src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg",
                                    height="25px",
                                ),
                                "  View Source",
                            ],
                            href="https://github.com/diabolical-ninja/naplan-performance",
                            target="_blank",
                            color="light",
                            className="mr-2",
                        )
                    )
                ],
                className="ml-auto",
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    style={"margin-bottom": 20},
)

historical_domain_performance_tab = html.Div(
    [
        dcc.Dropdown(
            ["All"] + naplan_results_df["domain"].unique().tolist(),
            value="All",
            id="result-domain",
        ),
        dcc.Dropdown(
            naplan_results_df["school_name"].unique(), multi=True, id="school-selection"
        ),
        dcc.Graph(id="average-naplan-results"),
    ]
)

top_schools_tab = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        [
                            "All",
                            "Reading",
                            "Writing",
                            "Spelling",
                            "Grammar",
                            "Numeracy",
                        ],
                        value="All",
                        id="top-n-skill-selection",
                    ),
                    width=5,
                ),
                dbc.Col(width=5),
            ],
            justify="around",
            style={"margin-top": 20},
        ),
        dbc.Row(
            [
                dcc.Dropdown(
                    ["All"] + naplan_results_df["results_year"].unique().tolist(),
                    value="All",
                    id="results-year",
                ),
                dcc.Graph(id="top-schools"),
            ]
        ),
    ]
)

income_distribution_tab = html.Div(
    [
        dcc.Dropdown(
            recurrent_income_df["school_name"].unique(),
            multi=True,
            id="income-distribution-school-selection",
        ),
        dcc.Graph(id="income-distribution"),
    ]
)

recurrent_income_tab = html.Div(
    [
        dcc.Dropdown(
            recurrent_income_df["school_name"].unique(),
            multi=True,
            id="recurrent-income-school-selection",
        ),
        dcc.Graph(id="recurrent-income"),
    ]
)

app.layout = dbc.Container(
    [
        navbar,
        dbc.Tabs(
            [
                dbc.Tab(
                    historical_domain_performance_tab,
                    label="Historical NAPLAN Results",
                    tab_id="historical-naplan_results",
                ),
                dbc.Tab(top_schools_tab, label="Top Schools", tab_id="top-schools"),
                dbc.Tab(
                    recurrent_income_tab,
                    label="Recurrent Income",
                    tab_id="recurrent-income",
                ),
                dbc.Tab(
                    income_distribution_tab,
                    label="Income Distribution",
                    tab_id="income-distribution",
                ),
            ],
            id="tabs",
            active_tab="historical-naplan_results",
        ),
        html.Div(id="tab-content", className="p-4"),
    ]
)


@callback(
    Output("income-distribution", "figure"),
    Input("income-distribution-school-selection", "value"),
)
def update_income_distribution(school_selection: Optional[List[str]]) -> go.Figure:

    if school_selection is None:
        school_selection = []

    income_fields = [
        "Australian government recurrent funding",
        "State / territory government recurring funding",
        "Fees, charges and parent contributions",
        "Other private sources",
        # "Total gross income",
    ]

    plot_df = recurrent_income_df[
        (recurrent_income_df["Net recurrent income"].isin(income_fields))
        & (recurrent_income_df["school_name"].isin(school_selection))
    ]

    colordict = {
        f: px.colors.qualitative.Plotly[i] for i, f in enumerate(income_fields)
    }

    fig = px.area(
        plot_df,
        x="year",
        y="$ per student",
        color="Net recurrent income",
        color_discrete_map=colordict,
        facet_col="school_name",
        facet_col_wrap=1,
        facet_row_spacing=0.2,
    )

    # Increase spacing between facets
    fig.update_layout(height=max(300 * len(school_selection), 300))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    return fig


@callback(
    Output("recurrent-income", "figure"),
    Input("recurrent-income-school-selection", "value"),
)
def update_recurrent_income(school_selection: Optional[List[str]]) -> go.Figure:

    if school_selection is None:
        school_selection = []

    income_fields = [
        "Total gross income",
    ]

    plot_df = recurrent_income_df[
        (recurrent_income_df["Net recurrent income"].isin(income_fields))
        & (recurrent_income_df["school_name"].isin(school_selection))
    ]

    fig = px.line(
        plot_df,
        x="year",
        y="$ per student",
        color="school_name",
    )

    # Increase spacing between facets
    fig.update_layout(height=max(300 * len(school_selection), 300))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    return fig


@callback(
    Output("average-naplan-results", "figure"),
    Input("school-selection", "value"),
    Input("result-domain", "value"),
)
def update_naplan_results_per_year(school_selection, result_domain):
    background_colour = "#e5ecf6"
    if school_selection is None:
        school_selection = []
        background_colour = "white"

    if result_domain == "All":
        plot_df = (
            naplan_results_df[naplan_results_df["school_name"].isin(school_selection)]
            .groupby(["school_name", "results_year", "year_level"])["avg"]
            .mean()
            .reset_index()
        )
    else:
        plot_df = naplan_results_df[
            (naplan_results_df["school_name"].isin(school_selection))
            & (naplan_results_df["domain"] == result_domain)
        ]

    fig_title = f"{result_domain} NAPLAN Results"
    y_axis_title = "Average NAPLAN Score" if result_domain == "All" else "NAPLAN Score"

    fig = px.line(
        plot_df,
        x="results_year",
        y="avg",
        color="school_name",
        title=fig_title,
        facet_row="year_level",
        markers=True,
        height=700,
        facet_row_spacing=0.1,
    )
    fig.update_layout(plot_bgcolor=background_colour)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="LightGray")
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor="LightGray", title_text=y_axis_title
    )
    return fig


@callback(Output("top-schools", "figure"), Input("results-year", "value"))
def update_top_ranked_schools(results_year):
    if results_year == "All":
        plot_df = naplan_results_df.groupby(["school_name"])["avg"].mean().reset_index()
    else:
        plot_df = (
            naplan_results_df[naplan_results_df["results_year"] == results_year]
            .groupby(["school_name", "results_year"])["avg"]
            .mean()
            .reset_index()
        )

    plot_df = plot_df.sort_values(ascending=True, by="avg")

    fig_title = "Top Schools by Average NAPLAN Results"

    fig = px.bar(
        plot_df,
        y="school_name",
        x="avg",
        # color="School Sector",
        orientation="h",
        # hover_data=[
        #     "School Sector",
        #     "School Type",
        # ],
        # color_discrete_map=color_discrete_map,
        title=fig_title,
        height=700,
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True)
