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


#--- TOP CHART's

total_offers = df2["title"].count()
total_offers_select = df_selection["title"].count()

# Definicja funkcji obliczającej średnią wypłatę
def avg_salary(df_selection):
    avg_salary_from = df_selection["salary_from"].mean()
    avg_salary_to = df_selection["salary_to"].mean()
    avg_salary = f"{avg_salary_from:.2f} - {avg_salary_to:.2f} PLN"
    return avg_salary


# i

#[BAR CHART]


top_cities = df_selection.groupby("city")["title"].count().reset_index()
top_cities = top_cities.sort_values("title", ascending=False).head(10)

fig1 = px.bar(top_cities, x="city", y="title", title="Top 10 miast z największą ilością ofert pracy")
# st.plotly_chart(fig1)


def draw_map(df_selection):
    # Ustawienie mapy zgodnie z granicami Polski
    # mapbox_access_token = "pk.eyJ1IjoibXNhbGFyaXMiLCJhIjoiY2tjN3lqanZtMDlzbTJycWtkaXk1czc1eCJ9.8rt_mjGZfuJwEziXTgHaow"
    # px.set_mapbox_access_token(mapbox_access_token)
    fig = px.density_mapbox(df_selection, lat="latitude", lon="longitude", radius=5,
                            hover_data={"title": True, 
                                        "city": True, 
                                        "marker_icon": True, 
                                        "salary_from": True, "salary_to": True,
                                        "skill_one": True, "skill_two": True, "skill_three": True},
                            mapbox_style="carto-darkmatter", center={"lat": 52.237049, "lon": 21.017532}, zoom=5, opacity=0.8)
    fig.update_traces(hovertemplate="<b>Stanowisko:</b> %{customdata[0]}<br>"
                                     "<b>Miasto:</b> %{customdata[1]}<br>"
                                     "<b>Kategoria:</b> %{customdata[2]}<br>"
                                     "<b>Wypłata:</b> %{customdata[3]}-%{customdata[4]} PLN<br>"
                                     "<b>Skills:</b> %{customdata[5]}, %{customdata[6]}, %{customdata[7]}<extra></extra><br>"
                                     )
    fig.update_layout(hoverlabel=dict(bgcolor="#23272b", font=dict(color="white")))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_layout(mapbox=dict(center=dict(lat=52.237049, lon=21.017532), zoom=5, style="carto-darkmatter"))
    fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(title=f"Liczba ofert: {len(df_selection)}")

    return fig


# Rysowanie mapy
# st.plotly_chart(draw_map(df_selection))
if selected == "Dane ogólne":
    left_column, middle_column, right_coulmn = st.columns(3)
    with left_column:
        st.subheader("Wszytskie oferty: ")
        st.subheader(f"{total_offers:,} ofert")
    with middle_column:
        st.subheader("Wyfiltrowane oferty:")
        st.subheader(f"{total_offers_select:,} ofert")
    with right_coulmn:
        st.subheader("Średnia wypłata:")
        st.subheader(avg_salary(df_selection))
    st.markdown("---")

    left_column, right_coulmn = st.columns(2)
    left_column.plotly_chart(fig1, use_container_width=True)
    with right_coulmn:
        st.subheader("Rozłożenie ofert na mapie Polski")
        right_coulmn.plotly_chart(draw_map(df_selection),use_container_width=True)

st.markdown("---")



