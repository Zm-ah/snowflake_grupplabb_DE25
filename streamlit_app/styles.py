# Shared styling helpers for the Streamlit pages (pure Python, no HTML/CSS)
import streamlit as st

# Colors used by the charts (same palette as the theme in .streamlit/config.toml)
# Colors are read from .streamlit/config.toml, so they are defined in one place only
BAR_COLOR = st.get_option("theme.primaryColor")
LABEL_COLOR = st.get_option("theme.textColor")
GRID_COLOR = st.get_option("theme.dataframeBorderColor")



def style_chart(chart):
    # Make an Altair chart readable on the dark theme
    return (
        chart.configure(background="transparent")
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=LABEL_COLOR,
            titleColor=LABEL_COLOR,
            gridColor=GRID_COLOR,
            domainColor=GRID_COLOR,
            tickColor=GRID_COLOR,
            labelFontSize=13,
            titleFontSize=13,
        )
    )


def glass_table(df, columns, bar_column=None):
    # Show a DataFrame with nice column names and number formats.
    # columns: list of (column_name, label, kind) where kind is "text", "int" or "float"
    config = {}
    for name, label, kind in columns:
        if name == bar_column:
            # Draw this column as a progress bar so rows are easy to compare
            config[name] = st.column_config.ProgressColumn(
                label,
                format="%.1f",
                min_value=0,
                max_value=float(df[name].max()) or 1,
            )
        elif kind == "text":
            config[name] = st.column_config.TextColumn(label)
        elif kind == "int":
            config[name] = st.column_config.NumberColumn(label, format="%d")
        else:
            config[name] = st.column_config.NumberColumn(label, format="%.1f")

    # Only show the columns we described, in the same order
    column_names = [name for name, _, _ in columns]
    st.dataframe(
        df[column_names],
        column_config=config,
        hide_index=True,
        use_container_width=True,
    )