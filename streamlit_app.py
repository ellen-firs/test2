import streamlit as st
import sqlite3
import pandas as pd
import datetime

# Подключение к базе данных
@st.cache_resource
def get_connection():
    return sqlite3.connect("schedule.db")  # Укажите путь к вашей базе данных

def get_data(query, params=()):
    try:
        conn = get_connection()
        df = pd.read_sql_query(query, conn, params)
        if df.empty:
            st.warning(f"Запрос не вернул данных: {query}")
        return df
    except Exception as e:
        st.error(f"Ошибка выполнения запроса: {e}")
        return pd.DataFrame()

st.title("Расписание")

# Выбор параметров
with st.sidebar:
    st.header("Выбор параметров")

    # Проверка таблицы Группы
    try:
        groups = get_data("SELECT * FROM Группы")  # Диагностика
        st.write("Данные из таблицы 'Группы':", groups)

        selected_group = st.selectbox(
            "Группа", 
            options=groups["название"].tolist() if "название" in groups.columns else []
        )
    except Exception as e:
        st.error(f"Ошибка загрузки данных для групп: {e}")

    # Проверка таблицы Преподаватели
    try:
        teachers = get_data("SELECT * FROM Преподаватели")  # Диагностика
        st.write("Данные из таблицы 'Преподаватели':", teachers)

        selected_teacher = st.selectbox(
            "Преподаватель", 
            options=[f"{row['имя']} {row['фамилия']}" for _, row in teachers.iterrows()] if "имя" in teachers.columns and "фамилия" in teachers.columns else []
        )
    except Exception as e:
        st.error(f"Ошибка загрузки данных для преподавателей: {e}")

    # Проверка таблицы Аудитории
    try:
        audiences = get_data("SELECT * FROM Аудитории")  # Диагностика
        st.write("Данные из таблицы 'Аудитории':", audiences)

        selected_audience = st.selectbox(
            "Аудитория", 
            options=audiences["номер"].tolist() if "номер" in audiences.columns else []
        )
    except Exception as e:
        st.error(f"Ошибка загрузки данных для аудиторий: {e}")

    selected_building = st.number_input("Корпус", min_value=1, step=1)
    selected_date = st.date_input("Дата")

# Определение четности недели
def get_week_parity(date):
    base_date = datetime.date(2024, 9, 2)  # 2 сентября 2024
    delta_weeks = (date - base_date).days // 7
    return "нечетная" if delta_weeks % 2 == 0 else "четная"

parity = get_week_parity(selected_date)

# Формирование и выполнение запроса для расписания
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

try:
    schedule = get_data(query, params)
    if schedule.empty:
        st.warning("Расписание не найдено.")
    else:
        st.dataframe(schedule)
except Exception as e:
    st.error(f"Ошибка загрузки расписания: {e}")
