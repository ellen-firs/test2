import sqlite3
import pandas as pd
import streamlit as st

# Функция для получения данных
def get_data(query, params):
    conn = sqlite3.connect('your_database.db')
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Получение уникальных значений для выбора из базы данных
def get_choices(query):
    conn = sqlite3.connect('your_database.db')
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[:, 0].tolist()

# Динамически загружаем данные для селектбоксов
groups = get_choices("SELECT название FROM Группы")
teachers = get_choices("SELECT имя || ' ' || фамилия FROM Преподаватели")
audiences = get_choices("SELECT номер FROM Аудитории")
buildings = get_choices("SELECT DISTINCT корпус FROM Расписание")

# Отображаем селектбоксы
selected_group = st.selectbox("Выберите группу", groups)
selected_teacher = st.selectbox("Выберите преподавателя", teachers)
selected_audience = st.selectbox("Выберите аудиторию", audiences)
selected_building = st.selectbox("Выберите корпус", buildings)
parity = st.selectbox("Выберите четность недели", ['нечетная', 'четная'])

# Выполнение SQL-запроса с параметрами
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

# Получение данных из базы
schedule = get_data(query, params)

# Отображение результатов
if schedule.empty:
    st.warning("Результат запроса пуст. Проверьте параметры.")
else:
    st.dataframe(schedule)
