import streamlit as st
import sqlite3
import pandas as pd

# Подключение к базе данных
@st.cache
def get_connection():
    conn = sqlite3.connect("schedule.db")  # Укажите путь к вашей базе данных
    return conn

def get_data(query, params=()):
    conn = get_connection()
    return pd.read_sql_query(query, conn, params)

st.title("Расписание")

# Выбор параметров
with st.sidebar:
    st.header("Выбор параметров")
    selected_group = st.selectbox(
        "Группа",
        options=get_data("SELECT название FROM Группы")["название"].tolist()
    )
    selected_teacher = st.selectbox(
        "Преподаватель",
        options=[f"{row['имя']} {row['фамилия']}" for _, row in get_data("SELECT имя, фамилия FROM Преподаватели").iterrows()]
    )
    selected_audience = st.selectbox(
        "Аудитория",
        options=get_data("SELECT номер FROM Аудитории")["номер"].tolist()
    )
    selected_building = st.number_input("Корпус", min_value=1, step=1)
    selected_date = st.date_input("Дата")

# Определить четность недели
import datetime
week_even = (selected_date.isocalendar()[1] % 2 == 0)
parity = "четная" if week_even else "нечетная"

# Формирование запроса
query = """
    SELECT 
        Дисциплины.название AS "Дисциплина",
        Преподаватели.имя || ' ' || Преподаватели.фамилия AS "Преподаватель",
        Время.время_начала || '-' || Время.время_окончания AS "Время",
        Дни_недели.название AS "День недели",
        Аудитории.номер AS "Аудитория",
        Расписание.корпус AS "Корпус",
        Группы.название AS "Группа"
    FROM Расписание
    JOIN Дисциплины ON Расписание.дисциплина_id = Дисциплины.дисциплина_id
    JOIN Преподаватели ON Расписание.преподаватель_id = Преподаватели.преподаватель_id
    JOIN Время ON Расписание.время_id = Время.время_id
    JOIN Дни_недели ON Расписание.день_id = Дни_недели.день_id
    JOIN Аудитории ON Расписание.аудитория_id = Аудитории.аудитория_id
    JOIN Группы ON Расписание.группа_id = Группы.группа_id
    WHERE Группы.название = ?
      AND Преподаватели.имя || ' ' || Преподаватели.фамилия = ?
      AND Аудитории.номер = ?
      AND Расписание.корпус = ?
      AND Расписание.четность = ?
"""
params = (selected_group, selected_teacher, selected_audience, selected_building, parity)

# Отображение расписания
schedule = get_data(query, params)
if schedule.empty:
    st.warning("Расписание не найдено.")
else:
    st.dataframe(schedule)
