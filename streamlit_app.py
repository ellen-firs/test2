import streamlit as st
import sqlite3
import pandas as pd
import datetime

# Подключение к базе данных
@st.cache_resource
def get_connection():
    # Разрешаем использование соединения в разных потоках
    return sqlite3.connect("schedule.db", check_same_thread=False)

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

# Проверка данных из таблиц
with st.sidebar:
    st.header("Выбор параметров")

    try:
        groups = get_data("SELECT * FROM Группы")
        if groups.empty:
            st.error("Таблица 'Группы' пуста. Добавьте данные.")
        else:
            st.write("Данные из таблицы 'Группы':", groups)
            selected_group = st.selectbox(
                "Группа", 
                options=groups["название"].tolist() if "название" in groups.columns else []
            )
    except Exception as e:
        st.error(f"Ошибка загрузки данных для групп: {e}")

    try:
        teachers = get_data("SELECT * FROM Преподаватели")
        if teachers.empty:
            st.error("Таблица 'Преподаватели' пуста. Добавьте данные.")
        else:
            st.write("Данные из таблицы 'Преподаватели':", teachers)
            selected_teacher = st.selectbox(
                "Преподаватель", 
                options=[f"{row['имя']} {row['фамилия']}" for _, row in teachers.iterrows()] if "имя" in teachers.columns and "фамилия" in teachers.columns else []
            )
    except Exception as e:
        st.error(f"Ошибка загрузки данных для преподавателей: {e}")

    try:
        audiences = get_data("SELECT * FROM Аудитории")
        if audiences.empty:
            st.error("Таблица 'Аудитории' пуста. Добавьте данные.")
        else:
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
    base_date = datetime.date(2024, 9, 2)
    delta_weeks = (date - base_date).days // 7
    return "нечетная" if delta_weeks % 2 == 0 else "четная"

parity = get_week_parity(selected_date)

# Формирование запроса для расписания
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
try:
    schedule = get_data(query, params)
    if schedule.empty:
        st.warning("Расписание не найдено.")
    else:
        st.dataframe(schedule)
except Exception as e:
    st.error(f"Ошибка загрузки расписания: {e}")
