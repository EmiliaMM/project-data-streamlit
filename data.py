import pandas as pd
import plotly_express as px
import streamlit as st
from streamlit_option_menu import option_menu
import altair as alt
import requests


st.set_page_config(
    page_title="Analiza ofert pracy dla programistów w Polsce",
    page_icon=":bar_chart",
    layout="wide"
)


@st.cache_data
def load_data():
    API_URL = "https://justjoin.it/api/offers"

    response = requests.get(API_URL)
    if response.status_code == 200:
        job_offers = response.json()
    else:
        job_offers = []

    data = []
    for offer in job_offers:
        skills = offer['skills']
        skill_one = ''
        skill_two = ''
        skill_three = ''
        if len(skills) > 0:
            skill_one = skills[0]['name']
        if len(skills) > 1:
            skill_two = skills[1]['name']
        if len(skills) > 2:
            skill_three = skills[2]['name']
        if 'salary' in 'employment_types':
            salary_from = offer['employment_types'][0]['from']
            salary_to = offer['employment_types'][1]['to']
        else:
            salary_from = None
            salary_to = None
        data.append({
            'title': offer['title'],
            'city': offer['city'],
            'marker_icon': offer['marker_icon'],
            'workplace_type': offer['workplace_type'],
            'experience_level': offer['experience_level'],
            'latitude': offer['latitude'],
            'longitude': offer['longitude'],
            'published_at': offer['published_at'],
            'remote_interview': offer['remote_interview'],
            'display_offer': offer['display_offer'],
            'employment_type': offer['employment_types'][0]['type'],
            'salary_from': salary_from,
            'salary_to': salary_to,
            'skill_one': skill_one,
            'skill_two': skill_two,
            'skill_three': skill_three
        })
    

    df = pd.DataFrame(data, columns=['title', 'city', 'marker_icon', 'workplace_type', 'experience_level',
                                'latitude', 'longitude', 'published_at', 'remote_interview', 'display_offer',
                                'employment_type','salary_from','salary_to','skill_one', 'skill_two', 'skill_three'])
    df["published_at"] = pd.to_datetime(df["published_at"])
    return df

df2 = load_data()
# st.dataframe(df2)

#Panel filtrujący

st.sidebar.header("Wybierz filtry:")

city = st.sidebar.selectbox(
    "Lokalizacja: ",
    options=df2["city"].unique(),
)


marker_icon= st.sidebar.selectbox(
    "Kategoria: ",
    options=df2["marker_icon"].unique()
    
)

employment_type= st.sidebar.multiselect(
    "Typ umowy: ",
    options=df2["employment_type"].unique(),
    default=df2["employment_type"].unique()
)

workplace_type = st.sidebar.multiselect(
    "Tryb pracy:",
    options=df2["workplace_type"].unique(),
    default=df2["workplace_type"].unique()
)

experience_level = st.sidebar.multiselect(
    "Poziom doświadczenia: ",
    options=df2["experience_level"].unique(),
    default=df2["experience_level"].unique()
)
    

df_selection = df2.query(
    "marker_icon == @marker_icon & city== @city & employment_type == @employment_type & workplace_type == @workplace_type & experience_level == @experience_level"
)


# konfiguracja strony 
st.title(":bar_chart: Analiza ofert pracy dla programistów w Polsce")
st.markdown("#")

selected = option_menu(
    menu_title=None,
    options=["Dane ogólne", "Wizualizacja"],
    orientation="horizontal",
)


