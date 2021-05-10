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

    df_dict = {}
    my_bar = st.progress(0)
    for year in range(1990, 2021):
        query_final = query + str(year)
        querystring = {
            "search": query_final,
            "format": "json",
        }
        response = requests.request("GET", url, params=querystring)
        text = yaml.safe_load(response.text)
        df_dict[year] = int(text["response"]["numFound"])
        my_bar.progress(len(df_dict) / 31)

    df = pd.DataFrame(list(df_dict.items()), columns = ['Year', 'Articles'])
    return df


st.set_page_config(page_title="Query ERIC", page_icon=":bulb:")

# hiding the hamburger menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("## :bulb: Query ERIC")
st.markdown("---")

st.write("Generate time trends by querying the ERIC database.")

query = st.text_input("Enter query...").lower().strip()
query = query.replace('"', '')

st.markdown("&nbsp;")

if query != "":
    query = " ".join(query.split())
    query = query.replace(" ", " AND ")
    query = query + " AND peerreviewed:T AND publicationdateyear:"
    with st.spinner("Fetching data from ERIC..."):
        df = load_data(query)
    st.altair_chart(
        alt.Chart(df)
        .mark_line()
        .encode(x="Year:Q", y="Articles:Q", tooltip=["Articles"])
        .properties(height=450),
        use_container_width=True,
    )
    df = df.sort_values(by=["Year"]).reset_index(drop=True)
    st.table(df)
