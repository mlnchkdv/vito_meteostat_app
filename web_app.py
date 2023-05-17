import streamlit as st

from datetime import datetime
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from meteostat import Point, Daily


def import_meteostat_saratov(start_date, end_date):
    # Set time period
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Create Point for Saratov 
    # https://time-in.ru/coordinates/saratov
    location = Point(51.5406, 46.0086, 71)

    # Get daily data
    data = Daily(location, start, end)
    data = data.fetch()

    return data['tavg']

def get_transition_point(df_col, threshold):
    df_col = df_col.resample('5D').mean()
    df_col = threshold - df_col
    df_col = df_col.rolling(5).mean()
    return df_col

def get_transition_point_median(df_col, threshold):
    df_col = df_col.resample('5D').median()
    df_col = threshold - df_col
    df_col = df_col.rolling(5).median()
    return df_col

def get_index_by_n_from_series(series, n):
    return str(series.index[n])[:-9]

def date_transition_point(df_date):
    for i in range(len(df_date)-1):
        if df_date[i] / df_date[i+1] >= 1.7:
            return (get_index_by_n_from_series(df_date, i+1), df_date[i+1])


st.set_page_config(page_title="Метео данные для города Саратов", page_icon=":thermometer:", layout="wide")
st.title("Метео данные для города Саратов")

col1, col2 = st.columns(2)

with col1:
    start = st.date_input("Введеите дату начала периода:")
with col2:
    end = st.date_input("Введеите дату конца периода:")

st.write('Ваши даты:', start, " - ", end)

selected = st.selectbox(
        "Что необходимо вычислить?",
        ("Вычислить точку перехода для периода", 
        "Вычислить среднее за весь период по дням", 
        "Вычислить медианное за весь период по дням"),
    )

# st.button("Получить отчет", on_click=start_app(start, end))
# if st.button('Получить отчет за период', on_click=None):
#     st.success('Данные загружены!', icon="✅")
if selected == "Вычислить точку перехода для периода":
    t_avg = import_meteostat_saratov(str(start), str(end))
    st.line_chart(t_avg)

    df_date = get_transition_point(t_avg, threshold = 10)
    st.write('Точка перехода:', date_transition_point(df_date))

# if st.button('Вычислить среднее за весь период по дням', on_click=None):
if selected == "Вычислить среднее за весь период по дням":

    t_avg = import_meteostat_saratov(str(start), str(end))

    # DataFrame
    df = t_avg.to_frame(name="temp").reset_index()
    df["time"] = pd.to_datetime(df["time"])
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["day"] = df["time"].dt.day
    df = df.groupby(["month", "day"]).mean()

    # Series
    t_avg_by_days = df["temp"].squeeze()
    # drop 29 February
    t_avg_by_days.drop((2, 29), axis=0, inplace=True)
    # # t_avg_by_days = pd.to_datetime(t_avg_by_days.index.get_level_values('day'))
    t_avg_by_days.index = pd.to_datetime(
        "2025-"
        + t_avg_by_days.index.get_level_values("month").astype(str)
        + "-"
        + t_avg_by_days.index.get_level_values("day").astype(str),
        format="%Y-%m-%d"
    )

    st.line_chart(t_avg_by_days)

    df_date = get_transition_point(t_avg_by_days, threshold = 10)
    st.write('Точка перехода:', date_transition_point(df_date))
    
# if st.button('Вычислить медианное за весь период по дням', on_click=None):
if selected == "Вычислить медианное за весь период по дням":
    t_avg = import_meteostat_saratov(str(start), str(end))

    # DataFrame
    df = t_avg.to_frame(name="temp").reset_index()
    df["time"] = pd.to_datetime(df["time"])
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["day"] = df["time"].dt.day
    df = df.groupby(["month", "day"]).median()

    # Series
    t_avg_by_days = df["temp"].squeeze()
    # drop 29 February
    t_avg_by_days.drop((2, 29), axis=0, inplace=True)
    t_avg_by_days.index = pd.to_datetime(
        "2025-"
        + t_avg_by_days.index.get_level_values("month").astype(str)
        + "-"
        + t_avg_by_days.index.get_level_values("day").astype(str),
        format="%Y-%m-%d"
    )

    st.line_chart(t_avg_by_days)

    df_date = get_transition_point_median(t_avg_by_days, threshold = 10)
    st.write('Точка перехода:', date_transition_point(df_date))
