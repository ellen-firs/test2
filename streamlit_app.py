import sqlite3
import pandas as pd
import streamlit as st

# Функция для получения данных из базы данных
def get_data(query, params):
    conn = sqlite3.connect('schedule.db', check_same_thread=False)  # Отключаем проверку на поток
    cursor = conn.cursor()
    cursor.execute(query, params)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    
    # Преобразуем результат в DataFrame
    return pd.DataFrame(rows, columns=columns)

# Функция для получения доступных опций из базы данных
def get_choices(query):
    conn = sqlite3.connect('schedule.db', check_same_thread=False)  # Отключаем проверку на поток
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    return [row[0] for row in rows]

# Загружаем доступные значения для селектбоксов
groups = get_choices("SELECT название FROM Группы")
teachers = get_choices("SELECT имя || ' ' || фамилия FROM Преподаватели")
audiences = get_choices("SELECT номер FROM Аудитории")
buildings = get_choices("SELECT DISTINCT корпус FROM Расписание")

# Селектбоксы
selected_group = st.selectbox("Выберите группу", groups)
selected_teacher = st.selectbox("Выберите преподавателя", teachers)
selected_audience = st.selectbox("Выберите аудиторию", audiences)
selected_building = st.selectbox("Выберите корпус", buildings)
parity = st.selectbox("Выберите четность недели", ['нечетная', 'четная'])

# Запрос для получения расписания
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

# Получение данных из базы данных
schedule = get_data(query, params)

# Отображение результатов
if schedule.empty:
    st.warning("Результат запроса пуст. Проверьте параметры.")
else:
    st.dataframe(schedule)
