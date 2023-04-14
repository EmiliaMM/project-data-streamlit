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

if selected == "Wizualizacja":
    # suwak do sterowania animacją
    min_date = df2["published_at"].min().date()
    max_date = df2["published_at"].max().date()
    date = st.slider("Date", min_date, max_date, min_date)

    # Filtrowane dane, aby pokazać tylko oferty pracy opublikowane do wybranej daty
    filtered_data = df2[df2["published_at"].dt.date <= date]

    # Utwórz mapę pokazującą oferty pracy według lokalizacji i kategorii
    map_data = filtered_data[["latitude", "longitude","title", "marker_icon", "skill_one", "skill_two", "skill_three"]]
    map_data = map_data.dropna(subset=["latitude", "longitude"]) # remove rows with missing lat/lon values
    map_chart = alt.Chart(map_data).mark_circle().encode(
        longitude="longitude:Q",
        latitude="latitude:Q",
        color=alt.Color("marker_icon:N",title="Kategoria", legend=None),
        tooltip=[
            alt.Tooltip("title:N", title="Stanowsiko "),
            alt.Tooltip("skill_one:N", title="1. "),
            alt.Tooltip("skill_two:N", title="2. "),
            alt.Tooltip("skill_three:N", title="3. ")
        ]
    ).properties(
        width=600,
        height=400
    )

    # Poziomy wykres słupkowy pokazujący najważniejsze wymagane umiejętności
    top_skills = filtered_data["skill_one"].append(filtered_data["skill_two"]).append(filtered_data["skill_three"]).value_counts().nlargest(10)
    chart_data = pd.DataFrame({"skill": top_skills.index, "count": top_skills.values})
    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        y=alt.Y("skill:N", sort="-x", title="Kategoria "),
        x= alt.X("count:Q", title="Liczba ofert ")
    ).properties(
        width=800,
        height=400,
        title=f"Top 10 wymaganych umiejętności ({date})"
        
    )

    # Kolor i kodowanie tooltipów do wykresu słupkowego
    tooltip = ["skill:N", "count:Q"]
    color = alt.Color("skill:N")
    bar_chart = bar_chart.encode(
        color=color,
        tooltip=tooltip
    )

    # Pokaż wykresy
    left_column, right_coulmn= st.columns(2)
    with left_column:
        st.altair_chart(map_chart, use_container_width=True)

    with right_coulmn:
        st.altair_chart(bar_chart, use_container_width=True)
 
 st.markdown("---")

#---- Ukryj Streamlit style------
hide_st_style = """
    <style>
    #MainManu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """

st.markdown(hide_st_style, unsafe_allow_html=True)



