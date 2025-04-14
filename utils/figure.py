import plotly.express as px
import plotly.graph_objects as go

from typing import Optional

from dash import html
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

import math
import polars as pl
import pandas as pd
import numpy as np

import json
import cairosvg  # You'll need to install this: pip install cairosvg
import base64
from PIL import Image
from io import BytesIO

from utils.data_preparer import DataPreparer

data_preparer = DataPreparer()

# Define your total target ARR
TOTAL_TARGET = 1_200_000

class Figure:

    plotly_template = "plotly_white"
    chart_margin = dict(l = 10, r = 10, t = 10, b = 10)
    
    # One for the World color palette
    colors = {
        "primary": "#006466",  # Teal/blue-green
        'secondary': '#065A60',   # Darker teal
        'accent': '#0B525B',      # Another shade
        'light': '#144552',       # Lighter shade
        'text': '#1B3A4B',        # For text
        'highlight': '#F2F2F2',   # Light highlight
        'white': '#FFFFFF'
    }

    freq_type_colors = {
        "Recurring": "#0078D4",     # Communication Blue
        "One-Time": "#006466",      # Persimmon
        "Unspecified": "#498205"    # Fern Green
    }

    custom_colorscale = [
        [0.0, colors['highlight']],     # Start with white
        # [0.25, self.colors['light']],# Move into a light highlight
        # [0.5, self.colors['primary']],    # Use an intermediate accent color
        # [0.75, self.colors['secondary']],# Near the darker teal
        [1.0, colors['secondary']]    # End with primary
    ]

    def __init__(self):
        pass

    def create_line_trace(
        self,
        x_values,
        y_values, 
        markers_mode: str,
        marker_size = None,
        marker_color = None,
        text_values_list = None,
        text_position: str = "bottom right",
        name_for_legend: Optional[str] = None, 
        legend_group: Optional[str] = None,
        line_color: Optional[str] = None, 
        line_type: Optional[str] = None,
        line_shape: Optional[str] = None, 
        line_width: Optional[int] = 3, 
        custom_data = None,
        hover_template = None,
        hover_info = None,
    ) -> go.Scatter:
        """
        Create a line trace which need to be added in the figure.

        Parameters:
        x_col: The x-axis data.
        y_col: The y-axis data.
        name_for_legend (Optional[str]): The name for the legend.
        color (Optional[str]): The color of the line.
        line_type (Optional[str]): The type of the line (e.g., 'dash', 'dot').
        shape (Optional[str]): The shape of the line (e.g., 'linear', 'spline').
        custom_data (Optional[List]): Custom data to attach to each point.

        Returns:
        A line Trace.
        """
        trace = go.Scatter(
            x = x_values,
            y = y_values,
            mode = markers_mode,
            marker = dict(
                size = marker_size,
                color = marker_color,
            ),
            line = dict(
                color = line_color,
                dash = line_type,
                shape = line_shape,
                width = line_width,
            ),
            name = name_for_legend,
            legendgroup = legend_group,
            text = text_values_list,
            textposition = text_position,
            customdata = custom_data,
            hovertemplate = hover_template,
            hoverinfo = hover_info,
        )

        return trace

    def create_kpi_card(self, value, goal, body_text = "Funds Raised"):
        return html.Div([
        html.H3(f"${value:,.2f}", 
                style={
                    'textAlign': 'center',
                    'color': self.colors['primary'],
                    'marginBottom': '5px',
                    'fontSize': '28px'
                }),
        html.P(body_text, 
               style={
                   'textAlign': 'center',
                   'color': self.colors['text']
               }),
        html.P(f"of ${goal:,} goal ({value/goal:.2%})", 
               style={
                   'textAlign': 'center',
                   'color': self.colors['secondary'],
                   'fontSize': '14px'
               })
    ])

    def create_monthly_mm_graph(self, df, y_col_name, target):
        """
        """

        x_vals = df["payment_date_calendar_monthyear"].to_list()
        y_vals = df[y_col_name].to_list()

        current_idx = len(x_vals) - 1

        if len(x_vals) < 12:
            x_vals = x_vals + ["Mar'25", "Apr'25", "May'25", "Jun'25"]     #ISSUE: hardcoded
            y_vals = y_vals + [None] * (12 - len(y_vals)) # + [target]

        fig = go.Figure()

        fig.add_trace(
            self.create_line_trace(
                x_values = x_vals,
                y_values = y_vals,
                markers_mode = "lines+markers+text",
                marker_size = 10,
                marker_color = self.colors['primary'],
                text_values_list = [f"${val:,.2f}" if val is not None else "" for val in y_vals],
                text_position = "top left",
                name_for_legend = "Cumulative Donations",
                # legend_group = "Cumulative Donations",
                line_color = self.colors['primary'],
                line_width = 6,
                hover_template = "%{text}",
            )
        )

        # Mark the current position with a distinct marker.
        fig.add_trace(go.Scatter(
            x = [x_vals[current_idx]],
            y = [y_vals[current_idx]],
            text = [f"{y_vals[current_idx]/target:,.2%} Achieved"],
            mode = 'markers+text',
            textposition = "bottom right",
            marker = dict(
                color = 'white',
                size = 13,
                line = dict(width = 3, color = self.colors['primary'])
            ),
            hoverinfo = 'none',
            showlegend = False
        ))

        # Add dotted goal trend line: from last actual to final FY month (jun'25)
        last_actual_month = x_vals[current_idx]
        last_actual_value = y_vals[current_idx]
        goal_line_x = [last_actual_month, "Jun'25"]
        goal_line_y = [last_actual_value, target]

        fig.add_trace(
            self.create_line_trace(
                x_values=goal_line_x,
                y_values=goal_line_y,
                markers_mode="lines+markers+text",
                marker_size= 6,
                marker_color=self.colors['secondary'],
                text_values_list=[None, f"Target: ${target:,.2f}"],
                text_position="top left",
                name_for_legend="Target",
                line_color=self.colors['secondary'],
                line_type="dot",
                hover_info="none",
                # hover_template="Trend to Goal",
            )
        )

        # Add milestones
        milestones = [0.25, 0.5, 0.75, 1]
        milestone_values = [target * m for m in milestones]

        for value, percent in zip(milestone_values, milestones):
            # label = f"${value:,} ({percent:.0%}) Achieved" if value <= y_vals[current_idx] else f"${value:,} ({percent:.0%})"

            label = ""
            if value <= y_vals[current_idx]:
                label = f"${value/1e6:.1f}M ({percent:.0%}) Achieved"
                if percent == 1:
                    label = f"${value/1e6:.1f}M Target Achieved"
            else:
                label = f"${value/1e6:.1f}M ({percent:.0%})"
                if percent == 1:
                    label = f"${value/1e6:.1f}M Target"

            fig.add_hline(
                y = value,
                line = dict(
                    color = self.colors['secondary'],
                    dash = "dot",
                    width = 1,
                ),
                opacity = 0.5,
                annotation_text = label,
                annotation_position = "top left",
            )

        # To show trimmed values
        fig.update_traces(
            cliponaxis = False,
        )

        fig.update_layout(
            hovermode = "x unified",
            showlegend = False,
            template = self.plotly_template,
            margin =  dict(l = 50, r = 10, t = 10, b = 10),
            xaxis = dict(
                # title = "Month",
                tickvals = x_vals,
                ticktext = x_vals,
                showgrid = False,
                zeroline = False,
                showline = True,
                ticks = "outside",
                tickcolor = self.colors['secondary'],
            ),
            yaxis = dict(
                # title = "Cumulative Donations",
                # range = [0, target * 1.2],
                # tickformat = "$,.0f",
                showgrid = False,
                zeroline = False,
                showline = False,
                showticklabels = False,
                # ticks = "outside",
                # tickcolor = self.colors['secondary'],
            ),
            # title = dict(
            #     text = f"Monthly Cumulative Money Moved",
            #     x = 0.5,
            #     font = dict(size = 24),
            # ),
        )

        return fig

    def create_goal_target_gauge_graph(self, value, goal):
        """
        """
        fig = go.Figure(
            go.Indicator(
                mode = "gauge+number+delta",
                value = value,
                number = dict(prefix = "$", valueformat = ",.0f"),
                delta = dict(
                    reference = goal,
                    position = "top",
                    increasing = dict(color = "green"),
                    decreasing = dict(color = "red")
                ),
                title = dict(text = "Money Moved YTD", font = dict(size = 24)),
                gauge = dict(
                    axis = dict(range = [0, goal], tickformat = "$,.0f"),
                    bar = dict(color = "darkblue"),
                    steps = [
                        dict(range = [0, goal * 0.5], color = "lightcoral"),
                        dict(range = [goal * 0.5, goal * 0.9], color = "gold"),
                        dict(range = [goal * 0.9, goal], color = "lightgreen")
                    ],
                    threshold = dict(
                        line = dict(color = "black", width = 4),
                        thickness = 0.75,
                        value = goal
                    )
                )
            )
        )

        fig.update_layout(
            # margin = self.chart_margin,
            template = self.plotly_template,
        )

        return fig
    
    def create_title_card(self, body_text, header_text = None, footer_text = None, card_width = "18rem"):
        """
        Create a title card.

        Parameters:
        header_text: The header text.
        body_text: The body text.

        Returns:
        A title card.
        """

        return html.Div([
            dbc.Card([
                dbc.CardHeader(header_text, className = "card-title fw-bold") if header_text else None,
                dbc.CardBody([
                    html.H2(body_text, className = "card-text fw-bold"),
                ]),
                dbc.CardFooter(footer_text) if footer_text else None
            ], style = dict(width = card_width, flex = 1),), 
        ])
    
    def create_money_mural_mosaic(self, df: pl.DataFrame):
        """
        Given a Polars DataFrame with columns:
        - 'payment_date_calendar_monthyear' (string, e.g. "Jul '24")
        - 'money_moved_monthly' (float)

        Returns a Plotly Figure in the 'Money Mural' mosaic style.
        """

        # -------------------------
        # 1. Select and Rename for Simplicity (Optional)
        # -------------------------
        # Ensure we have only the needed columns, with intuitive names
        df_mosaic = df.select([
            pl.col("payment_date_calendar_monthyear").alias("month_label"),
            pl.col("money_moved_monthly").alias("monthly_amount")
        ])

        # -------------------------
        # 2. Create Grid Coordinates
        # -------------------------
        # Suppose we want 4 columns for the mosaic:
        cols = 4
        n = df_mosaic.height  # number of months in your DF
        rows = math.ceil(n / cols)

        # Assign each month a (grid_x, grid_y) position
        # We'll place the first month in top-left, next across to the right, etc.
        x_coords = []
        y_coords = []
        for i in range(n):
            x_coords.append(i % cols)        # column index
            # We'll invert row index so the first row is at the top (max y)
            y_coords.append(rows - 1 - (i // cols))

        # Attach them back to df_pd
        df_mosaic = df_mosaic.with_columns([
            pl.lit(x_coords).alias("grid_x"),
            pl.lit(y_coords).alias("grid_y")
        ])

        # df_mosaic["grid_x"] = x_coords
        # df_mosaic["grid_y"] = y_coords

        # -------------------------
        # 3. Build the Mosaic Plotly Figure
        # -------------------------
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df_mosaic["grid_x"],
                y=df_mosaic["grid_y"],
                mode="markers+text",
                text=df_mosaic["month_label"],
                textposition="middle center",
                # The color of the tiles is based on the monthly amount
                marker=dict(
                    symbol="square",
                    size=100,  # fix a tile size; adjust if you want bigger/smaller squares
                    color=df_mosaic["monthly_amount"],
                    colorscale=self.custom_colorscale,           #TODO: change to One for the World colors
                    colorbar=dict(title="Monthly<br>Amount"),
                    showscale=False,
                    line=dict(color="black", width=1)
                ),
                hovertemplate=(
                    "Month: %{text}<br>" +
                    "Monthly Amount: $%{marker.color:,.2f}<extra></extra>"
                ),
                name="MosaicTiles"
            )
        )

        # Remove grid lines, ticks, etc., for a clean “mosaic” look
        fig.update_layout(
            template=self.plotly_template,
            margin=self.chart_margin,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                tickvals=[],
                ticktext=[],
                # side = "top",
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                tickvals=[],
                ticktext=[]
            ),
        )

        return fig
    
    def create_calendarplot(self, df: pl.DataFrame) -> go.Figure:
        """
        """
        pdf = df.to_pandas()

        pivot = pdf.pivot_table(
            index="payment_date_day_of_week",
            columns="payment_date_week_of_fy",
            values="payment_amount_usd",
            aggfunc="sum",
            fill_value=0
        )

        # Create a second pivot table containing the date for each cell.
        # We use the first (or only) payment_date for that cell.
        pivot_date = pdf.pivot_table(
            index="payment_date_day_of_week",
            columns="payment_date_week_of_fy",
            values="payment_date",
            aggfunc='first',
            fill_value="",
        )

        heatmap = go.Heatmap(
            x=pivot.columns,
            y=pivot.index,
            z=pivot.values,
            colorscale=self.custom_colorscale,
            customdata=pivot_date.values,
            hovertemplate=(
                "%{customdata|%b %d, %Y}<br>" +
                # "Week: %{x}<br>" +
                "%{y}<br>" +
                "Amount: $%{z:,.2f}<extra></extra>"
            ),            
            showscale=True,
        )

        fig = go.Figure(data=[heatmap])
        
        month_week_map = (df
            .group_by("payment_date_calendar_monthname")
            .agg([
                pl.col("payment_date_week_of_fy").min().alias("payment_date_week_of_fy")
            ])
            .sort("payment_date_week_of_fy")
        )

        fig.update_layout(
            hovermode = "x unified",
            xaxis = dict(
                title = "Week of FY",
                tickmode = 'array',
                tickvals = month_week_map["payment_date_week_of_fy"],
                ticktext = month_week_map["payment_date_calendar_monthname"],
            ),
            yaxis = dict(
                title = "Day of Week",
                autorange = "reversed",         # Reverse Y so 0=Monday is on top
                tickmode = 'array',
                tickvals = [1,2,3,4,5,6,7],
                ticktext = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            ),
            template = self.plotly_template,
            margin = self.chart_margin,
        )

        return fig
    
    def create_mm_monthly_trendline(self, money_moved_lf, selected_amount_type, selected_drilldown_by):
        fig = go.Figure()
        if selected_drilldown_by:
            lf = (money_moved_lf
                .group_by(["payment_date_fm", selected_drilldown_by])
                .agg([
                    pl.col(selected_amount_type).sum().alias("money_moved_monthly"),
                    # pl.col("payment_cf_amount_usd").sum().alias("cf_money_moved_monthly"),
                    pl.col(["payment_date_calendar_month", "payment_date_calendar_monthyear"]).first(),
                ])
                .sort("payment_date_fm")
            )

            unique_traces = data_preparer.get_col_unique_values_lf(lf, selected_drilldown_by)

            df = lf.collect()

            for trace in unique_traces:
                trace_df = df.filter(pl.col(selected_drilldown_by) == trace).sort("payment_date_fm")

                fig = fig.add_trace(
                    self.create_line_trace(
                        x_values = trace_df["payment_date_calendar_monthyear"],
                        y_values = trace_df["money_moved_monthly"],
                        markers_mode = "lines+markers",
                        marker_size = 8,
                        marker_color = px.colors.qualitative.Set3,
                        # text_values_list = [f"${val:,.2f}" if val is not None else "" for val in y_vals],
                        text_position = "top left",
                        name_for_legend = trace,
                        # legend_group = "Cumulative Donations",
                        # line_color = self.colors['primary'],
                        line_width = 3,
                        hover_template = "%{y}",
                    )
                )
        else:
            df = (money_moved_lf
                .group_by(["payment_date_fm"])
                .agg([
                    pl.col(selected_amount_type).sum().alias("money_moved_monthly"),
                    # pl.col("payment_cf_amount_usd").sum().alias("cf_money_moved_monthly"),
                    pl.col(["payment_date_calendar_month", "payment_date_calendar_monthyear"]).first(),
                ])
                .sort("payment_date_fm")
                .collect()
            )

            y_vals = df["money_moved_monthly"].to_list()

            fig = fig.add_trace(
                    self.create_line_trace(
                        x_values = df["payment_date_calendar_monthyear"],
                        y_values = y_vals,
                        markers_mode = "lines+markers+text",
                        marker_size = 8,
                        marker_color = self.colors['primary'],
                        text_values_list = [f"${val:,.2f}" if val is not None else "" for val in y_vals],
                        text_position = "top left",
                        name_for_legend = "MM",
                        # legend_group = "Cumulative Donations",
                        line_color = self.colors['primary'],
                        line_width = 3,
                        hover_template = "%{text}",
                    )
                )
            
        fig.update_layout(
            hovermode = "x unified",
            # showlegend = False,
            legend = dict(title = dict(text = "Select (Double-Click) / De-Select (One-Click)", side = "top center"), yanchor = "top", y = 1.1, x = 0.5, xanchor = "center", orientation = "h"),
            template = self.plotly_template,
            margin =  self.chart_margin,
            xaxis = dict(
                # title = "Month",
                # tickvals = x_vals,
                # ticktext = x_vals,
                showgrid = False,
                zeroline = False,
                showline = True,
                ticks = "outside",
                tickcolor = self.colors['secondary'],
            ),
            yaxis = dict(
                # title = "Cumulative Donations",
                # range = [0, target * 1.2],
                tickformat = "$,.3s",
                showgrid = False,
                zeroline = False,
                showline = False,
                # showticklabels = False,
                ticks = "outside",
                tickcolor = self.colors['secondary'],
            ),
            # title = dict(
            #     text = f"Monthly Cumulative Money Moved",
            #     x = 0.5,
            #     font = dict(size = 24),
            # ),
        )
            
        return fig
    
    def create_attrition_rate_trendline(self, attrition_lf, selected_drilldown_by):

        lf = attrition_lf

        fig = go.Figure()

        if selected_drilldown_by:
            lf = (lf
                .group_by(["pledge_starts_at_fm", selected_drilldown_by])
                .agg([
                    pl.sum("total_pledge_count").alias("total_pledge_count"),
                    pl.sum("is_cancelled_count").alias("is_cancelled_count"),
                    pl.col(["pledge_starts_at_calendar_month", "pledge_starts_at_calendar_monthyear"]).first(),
                ])
                .with_columns([
                    (pl.col("is_cancelled_count") / pl.col("total_pledge_count")).alias("attrition_rate")
                ])
                .sort("pledge_starts_at_fm")
            )

            unique_traces = data_preparer.get_col_unique_values_lf(lf, selected_drilldown_by)

            df = lf.collect()

            for trace in unique_traces:
                trace_df = df.filter(pl.col(selected_drilldown_by) == trace).sort("pledge_starts_at_fm")
                # print(trace_df)

                fig = fig.add_trace(
                    self.create_line_trace(
                        x_values = trace_df["pledge_starts_at_fm"],
                        y_values = trace_df["attrition_rate"],
                        markers_mode = "lines+markers",
                        marker_size = 8,
                        marker_color = px.colors.qualitative.Set3,
                        # text_values_list = [f"${val:,.2f}" if val is not None else "" for val in y_vals],
                        text_position = "top left",
                        name_for_legend = trace,
                        # legend_group = "Cumulative Donations",
                        # line_color = self.colors['primary'],
                        line_width = 3,
                        hover_template = "%{y}",
                    )
                )
        else:
            df = (lf
                .group_by(["pledge_starts_at_fm"])
                .agg([
                    pl.sum("total_pledge_count").alias("total_pledge_count"),
                    pl.sum("is_cancelled_count").alias("is_cancelled_count"),
                    pl.col(["pledge_starts_at_calendar_month", "pledge_starts_at_calendar_monthyear"]).first(),
                ])
                .with_columns([
                    (pl.col("is_cancelled_count") / pl.col("total_pledge_count")).alias("attrition_rate")
                ])
                .sort("pledge_starts_at_fm")
                .collect()
            )

            y_vals = df["attrition_rate"].to_list()
            x_vals = df["pledge_starts_at_fm"].to_list()

            fig = fig.add_trace(
                    self.create_line_trace(
                        x_values = x_vals,
                        y_values = y_vals,
                        markers_mode = "lines+markers+text",
                        marker_size = 8,
                        marker_color = self.colors['primary'],
                        text_values_list = [f"${val:,.2%}" if val is not None else "" for val in y_vals],
                        text_position = "top left",
                        name_for_legend = "Attrition Rate",
                        # legend_group = "Cumulative Donations",
                        line_color = self.colors['primary'],
                        line_width = 3,
                        hover_template = "%{text}",
                    )
                )
            
            # fig.add_shape(
            #     type="line",
            #     x0=min(x_vals),
            #     x1=max(x_vals),
            #     y0=monthly_target,
            #     y1=monthly_target,
            #     line=dict(color="red", width=2, dash="dash"),
            #     xref="x",
            #     yref="y"
            # )

            # fig.add_annotation(
            #     x=max(x_vals),
            #     y=monthly_target,
            #     text="Monthly Target (1.5%)",
            #     showarrow=False,
            #     font=dict(size=12, color="red"),
            #     xanchor="left",
            #     yanchor="bottom"
            # )
                        
        # Get all unique fiscal months in correct order
        all_months_df = (
            lf
            .select(["pledge_starts_at_fm", "pledge_starts_at_calendar_monthyear"])
            .unique()
            .sort("pledge_starts_at_fm")
            .collect()
        )

        month_keys = all_months_df["pledge_starts_at_fm"].to_list()
        # month_keys = [x - 1 for x in all_months_df["pledge_starts_at_fm"].to_list()]
        month_labels = all_months_df["pledge_starts_at_calendar_monthyear"].to_list()

        fig.update_layout(
            hovermode = "x unified",
            # showlegend = False,
            legend = dict(title = dict(text = "Select (Double-Click) / De-Select (One-Click)", side = "top center"), yanchor = "top", y = 1.1, x = 0.5, xanchor = "center", orientation = "h"),
            template = self.plotly_template,
            margin =  self.chart_margin,
            xaxis = dict(
                # title = "Month",
                tickmode = "array",
                tickvals = month_keys,
                ticktext = month_labels,
                showgrid = False,
                zeroline = False,
                showline = True,
                ticks = "outside",
                tickcolor = self.colors['secondary'],
            ),
            yaxis = dict(
                # title = "Cumulative Donations",
                # range = [0, target * 1.2],
                tickformat = ",.0%",
                showgrid = False,
                zeroline = False,
                showline = False,
                # showticklabels = False,
                ticks = "outside",
                tickcolor = self.colors['secondary'],
            ),
            # title = dict(
            #     text = f"Monthly Cumulative Money Moved",
            #     x = 0.5,
            #     font = dict(size = 24),
            # ),
        )
            
        return fig
    
    # Define the Sankey generator function
    def create_active_pledge_arr_sankey(self, df: pl.DataFrame, view_mode: str = "actual", total_target: float = TOTAL_TARGET) -> go.Figure:

        grouped = df.group_by(["pledge_chapter_type", "pledge_frequency"]).agg(
            pl.col("pledge_contribution_arr_usd").sum().alias("actual_arr")
        ).to_pandas()

        if view_mode == "target":
            total_actual = grouped["actual_arr"].sum()
            grouped["target_arr"] = (grouped["actual_arr"] / total_actual) * total_target
            grouped["gap_arr"] = (grouped["target_arr"] - grouped["actual_arr"]).clip(lower=0)

        chapters = grouped["pledge_chapter_type"].unique().tolist()
        freqs = grouped["pledge_frequency"].unique().tolist()
        sinks = ["Actual ARR"] if view_mode == "actual" else ["Actual ARR", "Gap to Target"]
        all_nodes = chapters + freqs + sinks
        node_idx = {label: idx for idx, label in enumerate(all_nodes)}

        sources, targets, values = [], [], []

        for _, row in grouped.iterrows():
            ch = row["pledge_chapter_type"]
            fr = row["pledge_frequency"]
            actual = row["actual_arr"]

            sources.append(node_idx[ch])
            targets.append(node_idx[fr])
            values.append(actual if view_mode == "actual" else actual + row["gap_arr"])

        flow_to_actual = grouped.groupby("pledge_frequency")["actual_arr"].sum().to_dict()

        flow_to_gap = {}
        if view_mode == "target" and "gap_arr" in grouped.columns:
            flow_to_gap = grouped.groupby("pledge_frequency")["gap_arr"].sum().to_dict()

        for fr in freqs:
            actual_val = flow_to_actual.get(fr, 0)
            gap_val = flow_to_gap.get(fr, 0)

            if actual_val > 0:
                sources.append(node_idx[fr])
                targets.append(node_idx["Actual ARR"])
                values.append(actual_val)

            if view_mode == "target" and gap_val > 0:
                sources.append(node_idx[fr])
                targets.append(node_idx["Gap to Target"])
                values.append(gap_val)

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                label=all_nodes,
                color=[
                    "#006466" if n in chapters else
                    "#0B525B" if n in freqs else
                    "#2D6A4F" if n == "Actual ARR" else
                    "#D00000" if n == "Gap to Target" else
                    "#ccc" for n in all_nodes
                ],
                hovertemplate=(
                    "<b>%{label}</b><br>" +
                    "Total Value Through Node: $%{value:,.3s}<extra></extra>"
                )
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                hovertemplate=(
                    "<b>Flow</b>: %{source.label} → %{target.label}<br>" +
                    "ARR Amount: <b>$%{value:,.3s}</b><extra></extra>"
                ),
                color="rgba(0,100,100,0.3)"
            ),
        )])

        fig.update_layout(
            title=(
                "Annualized Run Rate Flow " + 
                (f"(What it would take to reach ${total_target/1e6:.1f}M)" if view_mode == "target" else "") +
                " : Chapter Type → Frequency → " +
                ("Current ARR" if view_mode == "actual" else f"Current ARR & Remaining")
            ),
            font_size=12,
            margin=dict(t=30, l=10, r=10, b=10),
        )

        return fig
    
    def create_reoccuring_vs_onetime_bar_graph(self, df):
        """
        
        """
        
        fig = go.Figure()

        hover_template = "<br>".join([
            # "%{x}",
            "$%{y:,.2f}",
        ])

        for freq_type in df["pledge_frequency_type"].unique():
            freq_df = df.filter(pl.col("pledge_frequency_type") == freq_type)

            x_vals = freq_df["payment_date_calendar_monthyear"].to_list()

            color = self.freq_type_colors.get(freq_type, self.colors['primary'])  # Fallback to default if unknown

            fig.add_trace(
                go.Bar(
                    x = x_vals,
                    y = freq_df["money_moved_usd"],
                    name = f"{freq_type}",
                    text = freq_df["money_moved_usd"],
                    texttemplate = "$%{text:.3s}",
                    textposition = "outside",
                    hovertemplate = hover_template,
                    marker_color = color,
                    # hoverinfo="text",
                )
            )

        # Add cumulative YTD line
        # fig.add_trace(go.Scatter(
        #     x = df["payment_date_calendar_monthyear"],
        #     y = df["money_moved_usd_cumulative"],
        #     mode = "lines+markers",
        #     name = f"Cumulative FYTD",
        #     line = dict(width = 3, color = self.colors['secondary'], dash = "dot"),
        #     marker = dict(size=6),
        #     yaxis = "y2",
        #     hovertemplate = "<b>Cumulative Overall FYTD: $%{y:,.0f}</b><extra></extra>"
        # ))

            # fig.add_trace(
            #     self.create_line_trace(
            #         x_values = x_vals,
            #         y_values = freq_df["money_moved_usd_cumulative"],
            #         markers_mode = "lines+markers",
            #         marker_size = 6,
            #         marker_color = self.colors['secondary'],
            #         text_values_list = [f"${val:,.2f}" if val is not None else "" for val in freq_df["money_moved_usd_cumulative"]],
            #         text_position = "top left",
            #         name_for_legend = f"{freq_type} Cumulative YTD",
            #         # legend_group = "Cumulative Donations",
            #         line_color = self.colors['secondary'],
            #         line_width = 3,
            #         hover_template = "%{text}",
            #         hover_info = "text",
            #     )
            # )

        fig.update_layout(
            hovermode = "x unified",
            xaxis = dict(showgrid = False, zeroline = False, showline = True, ticks = "outside", tickcolor = self.colors['secondary']),
            yaxis = dict(tickformat = "$,.3s", showgrid = True, zeroline = False, showline = True, ticks = "outside", tickcolor = self.colors['secondary']),
            yaxis2=dict(
                title="Cumulative Total YTD",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            barmode = 'group',
            template = self.plotly_template,
            margin = self.chart_margin,
            legend = dict(title = dict(text = "Select (Double-Click) / De-Select (One-Click)", side = "top center"), yanchor = "top", y = 1.1, x = 0.5, xanchor = "center", orientation = "h"),
        )

        return fig
    
    def create_dumbell_chart_w_logo(self, df, selected_fy, prior_fy):
        df = df.sort_values(by = "pledge_donor_chapter")

        fig = go.Figure()

        # Add traces for the dumbbell chart
        fig.add_trace(go.Scatter(
            x=df["prior_fy"],
            y=df["pledge_donor_chapter"],
            mode="markers",
            name=f"{selected_fy}",
            marker=dict(color=self.colors["primary"], size=10)
        ))

        fig.add_trace(go.Scatter(
            x=df["selected_fy"],
            y=df["pledge_donor_chapter"],
            mode="markers",
            name=f"{prior_fy}",
            marker=dict(color=self.freq_type_colors.get("Unspecified"), size=10)
        ))

        for _, row in df.iterrows():
            fig.add_trace(go.Scatter(
                x=[row["prior_fy"], row["selected_fy"]],
                y=[row["pledge_donor_chapter"], row["pledge_donor_chapter"]],
                mode="lines",
                line=dict(color="gray", width=1),
                showlegend=False
            ))
        
        # Add logos as layout images
        layout_images = []
        y_values = df["pledge_donor_chapter"].tolist()

        logo_mapping = data_preparer.load_logo_mappings()
        
        # Add logos for each donor chapter
        # In the logo addition section:
        for i, donor_chapter in enumerate(y_values):
            # Find the logo for this donor chapter
            logo_file = data_preparer.find_best_logo_match(donor_chapter, logo_mapping)
            
            if logo_file:
                # Convert logo to base64
                logo_b64 = data_preparer.get_logo_as_base64(logo_file)
                
                if logo_b64:
                    # For smaller datasets, adjust sizing
                    row_height = 1.0
                    if len(y_values) <= 5:
                        # Make logos larger for smaller datasets
                        size_multiplier = 0.2
                    else:
                        size_multiplier = 0.15
                    
                    # Add image to layout - use paper coordinates with adjusted position
                    layout_images.append({
                        "source": logo_b64,
                        "xref": "paper",
                        "yref": "y",
                        "x": 0.0,  # Move to the far left edge of the plotting area
                        "y": donor_chapter,
                        "sizex": 0.08,  # Slightly smaller width
                        "sizey": row_height * 0.7,  # Slightly smaller height
                        "xanchor": "right",  # Anchor to right side of image
                        "yanchor": "middle",
                        "layer": "above"
                    })

        # Update layout with adjusted margins and axis placement
        fig.update_layout(
            # title=f"Top Something Donor Chapters - FY", # {selected_fy} vs FY {selected_fy - 1} (YTD Month {selected_fm})",
            xaxis=dict(
                title="Amount (USD)",
                domain=[0.25, 1],  # Increase left margin to 15% for logos
            ),
            yaxis=dict(
                # title="Donor Chapter",
                # categoryorder="array",
                # categoryarray=donor_order,
                side="left",  # Ensure y-axis is on the left
                position=0.25,  # Position y-axis at 15% from left
                automargin=True  # Automatically adjust margin for labels
            ),
            height=max(500, 100 + 50 * len(y_values)),  # Dynamic height
            margin=dict(l=140, r=40, t=50, b=40),  # Increase left margin
            template=self.plotly_template,
            images=layout_images,
            legend = dict(title = dict(side = "top center"), yanchor = "top", y = 1.1, x = 0.5, xanchor = "center", orientation = "h"),
        )

        return fig