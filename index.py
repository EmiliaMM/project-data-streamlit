import pandas as pd
import plotly_express as px
import streamlit as st
from streamlit_option_menu import option_menu
import altair as alt



st.set_page_config(page_title="Analiza ofert pracy dla programistów w Polsce",
                   page_icon=":bar_chart",
                   layout="wide")


@st.cache_data
def get_data_form_csv():
    df = pd.read_csv('data1.csv', parse_dates=["published_at"])
    # df["published_at"] = pd.to_datetime(df["published_at"], format="%Y-%m-%d").dt.date
    return df
df = get_data_form_csv()


# st.dataframe(df)

selected = option_menu(
    menu_title=None,
    options=["Dane ogólne", "Wizualizacja"],
    orientation="horizontal",
)

#---sidebar---

st.sidebar.header("Wybierz filtry:")

# city = st.sidebar.multiselect(
#     "Typ rozmowy kwalifikacyjnej: ",
#     options=df["city"].unique(),
#     default=df["city"].unique()
# )

# options= df["marker_icon"].unique()

marker_icon= st.sidebar.selectbox(
    "Kategoria: ",
    options=df["marker_icon"].unique()
    # default=df["marker_icon"].unique()
)

employment_type= st.sidebar.multiselect(
    "Typ umowy: ",
    options=df["employment_type"].unique(),
    default=df["employment_type"].unique()
)

workplace_type = st.sidebar.multiselect(
    "Tryb pracy:",
    options=df["workplace_type"].unique(),
    default=df["workplace_type"].unique()
)

experience_level = st.sidebar.multiselect(
    "Poziom doświadczenia: ",
    options=df["experience_level"].unique(),
    default=df["experience_level"].unique()
)


# remote_intervieiw = st.sidebar.selectbox(
#     "Typ rozmowy kwalifikacyjnej: ",
#     options=df["remote_intervieiw"].unique(),
#     default=df["remote_intervieiw"].unique(),
#     key=int)
    

df_selection = df.query(
    "marker_icon == @marker_icon & employment_type == @employment_type & workplace_type == @workplace_type & experience_level == @experience_level"
)

# st.dataframe(df_selection)
#--- mainpage


st.title(":bar_chart: Analiza ofert pracy dla programistów w Polsce")
st.markdown("#")

#--- TOP CHART's

total_offers = df["title"].count()
total_offers_select = df_selection["title"].count()

# Definicja funkcji obliczającej średnią wypłatę
def avg_salary(df_selection):
    avg_salary_from = df_selection["salary_from"].mean()
    avg_salary_to = df_selection["salary_to"].mean()
    avg_salary = f"{avg_salary_from:.2f} - {avg_salary_to:.2f} PLN"
    return avg_salary


# def top_3_marker_icons(df_selection):
#     # wybierz kolumnę marker_icon i oblicz liczbę wystąpień każdej wartości
#     counts = df_selection["marker_icon"].value_counts()
#     # wybierz trzy najczęściej występujące wartości
#     top_3 = counts.head(3)
#     return top_3
# top_3 = top_3_marker_icons(df_selection)
# if selected == "Dane ogólne":
#     left_column, middle_column, right_coulmn = st.columns(3)
#     with left_column:
#         st.subheader("Wszytskie oferty: ")
#         st.subheader(f"{total_offers:,} ofert")
#     with middle_column:
#         st.subheader("Wyfiltrowane oferty:")
#         st.subheader(f"{total_offers_select:,} ofert")
#     with right_coulmn:
#         st.subheader("Średnia wypłata:")
#         st.subheader(avg_salary(df_selection))
#     st.markdown("---")




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
                                        "skills_one": True, "skills_two": True, "skills_three": True},
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
    min_date = df["published_at"].min().date()
    max_date = df["published_at"].max().date()
    date = st.slider("Date", min_date, max_date, min_date)

    # Filtrowane dane, aby pokazać tylko oferty pracy opublikowane do wybranej daty
    filtered_data = df[df["published_at"].dt.date <= date]

    # Utwórz mapę pokazującą oferty pracy według lokalizacji i kategorii
    map_data = filtered_data[["latitude", "longitude","title", "marker_icon", "skills_one", "skills_two", "skills_three"]]
    map_data = map_data.dropna(subset=["latitude", "longitude"]) # remove rows with missing lat/lon values
    map_chart = alt.Chart(map_data).mark_circle().encode(
        longitude="longitude:Q",
        latitude="latitude:Q",
        color=alt.Color("marker_icon:N",title="Kategoria", legend=None),
        tooltip=[
            alt.Tooltip("title:N", title="Stanowsiko "),
            alt.Tooltip("skills_one:N", title="1. "),
            alt.Tooltip("skills_two:N", title="2. "),
            alt.Tooltip("skills_three:N", title="3. ")
        ]
    ).properties(
        width=600,
        height=400
    )

    # Poziomy wykres słupkowy pokazujący najważniejsze wymagane umiejętności
    top_skills = filtered_data["skills_one"].append(filtered_data["skills_two"]).append(filtered_data["skills_three"]).value_counts().nlargest(10)
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
