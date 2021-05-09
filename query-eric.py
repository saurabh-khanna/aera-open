#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import requests
import yaml
import altair as alt
import streamlit as st

url = "https://api.ies.ed.gov/eric/"


@st.cache(allow_output_mutation=True, show_spinner=False, suppress_st_warning=True)
def load_data(query):

    querystring1 = {"search": query, "format": "json"}
    response1 = requests.request("GET", url, params=querystring1)
    text1 = yaml.safe_load(response1.text)
    results_max = text1["response"]["numFound"]

    my_bar = st.progress(0)
    my_message = st.empty()
    df = []
    results = 0
    start = 0
    while results < results_max:
        if start == 0:
            my_message.warning(
                "Fetched " + str(start) + " out of " + str(results_max) + " papers..."
            )
        querystring = {
            "search": query,
            "format": "json",
            "fields": "publicationdateyear",
            "rows": 2000,
            "start": start,
        }
        response = requests.request("GET", url, params=querystring)
        text = yaml.safe_load(response.text)
        df_mini = pd.DataFrame(text["response"]["docs"])
        df.append(df_mini)
        # keeping at least 30 results
        results += len(df_mini)
        start += 2000
        if start < results_max:
            my_message.warning(
                "Fetched " + str(start) + " out of " + str(results_max) + " papers..."
            )
            my_bar.progress(start / results_max)
        else:
            my_message.success("Fetched all " + str(results_max) + " papers!")
            my_bar.progress(1.0)

    df = pd.concat(df)
    return df


st.set_page_config(page_title="Query ERIC", page_icon=":balloon:")

# hiding the hamburger menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("## Query ERIC")

st.markdown("&nbsp;")

query = st.text_input("Enter query...").strip()

st.markdown("&nbsp;")

if query != "":
    df = load_data(query)
    df = (
        df["publicationdateyear"]
        .value_counts()
        .rename_axis("year")
        .reset_index(name="counts")
    )
    st.altair_chart(
        alt.Chart(df).mark_area().encode(x="year:Q", y="counts:Q", tooltip=["counts"]),
        use_container_width=True,
    )
    df = df.sort_values(by=["year"])
    st.dataframe(df)
