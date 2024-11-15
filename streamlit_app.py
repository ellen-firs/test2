import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Расписание занятий", page_icon="📅", layout="wide")

# CSS стили с адаптацией к темному и светлому режиму
st.markdown("""
    <style>
    /* Стилизация заголовка */
    h1 {
        color: inherit; /* Наследуем цвет, чтобы он адаптировался под темный/светлый режим */
        text-align: center;
    }
    
    /* Стилизация рамок селектбоксов и кнопки с нейтральным фоном и адаптивными рамками */
    .stSelectbox, .stButton {
        border-radius: 10px;
        background-color: rgba(240, 240, 240, 0.8); /* светло-серый с прозрачностью */
        padding: 5px;
        box-shadow: 0px 0px 3px rgba(0, 0, 0, 0.1); /* легкий тень */
    }

    /* Стилизация таблицы */
    .stDataFrame table {
        border: 1px solid rgba(200, 200, 200, 0.5); /* светлая рамка для таблицы */
    }
    .stDataFrame table th {
        background-color: rgba(230, 230, 230, 0.8); /* светлый фон заголовка */
        color: inherit; /* Наследуем цвет для адаптации */
    }
    .stDataFrame table td {
        background-color: rgba(250, 250, 250, 0.8); /* почти белый фон ячеек */
        color: inherit;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 Расписание занятий")

# Функции для работы с данными
def get_data(query, params):
    conn = sqlite3.connect('schedule.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query, params)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=columns)

def get_choices(query):
    conn = sqlite3.connect('schedule.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_days_of_week():
    conn = sqlite3.connect('schedule.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT название FROM Дни_недели ORDER BY день_id")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_week_parity(date):
    start_date = datetime(2024, 9, 2)
    delta = date - start_date
    week_number = delta.days // 7
    return 'нечетная' if week_number % 2 == 0 else 'четная'

def get_day_of_week(date):
    days_of_week = get_days_of_week()
    return days_of_week[date.weekday()]

# Загружаем доступные значения
groups = get_choices("SELECT название FROM Группы")
teachers = get_choices("SELECT имя || ' ' || фамилия FROM Преподаватели")
audiences = get_choices("SELECT номер FROM Аудитории")
buildings = get_choices("SELECT DISTINCT корпус FROM Расписание")
types_of_classes = ['лекция', 'практика']

# Селектбоксы для выбора параметров
st.sidebar.header("Фильтры")
selected_date = st.sidebar.date_input("Дата (не обязательно)", value=None)
selected_group = st.sidebar.selectbox("Группа", [""] + groups)
selected_teacher = st.sidebar.selectbox("Преподаватель", [""] + teachers)
selected_audience = st.sidebar.selectbox("Аудитория", [""] + audiences)
selected_building = st.sidebar.selectbox("Корпус", [""] + buildings)
selected_type = st.sidebar.selectbox("Тип занятия", [""] + types_of_classes)

# Определяем день недели и четность, если выбрана дата
day_of_week, week_parity = None, None
if selected_date:
    selected_date = datetime.strptime(str(selected_date), '%Y-%m-%d')
    day_of_week = get_day_of_week(selected_date)
    week_parity = get_week_parity(selected_date)
    st.write(f"Выбранная дата: {selected_date.date()}, {day_of_week}, {week_parity} неделя")

if st.sidebar.button("Показать расписание"):
    query = """
        SELECT 
            Дисциплины.название AS "Дисциплина",
            Преподаватели.имя || ' ' || Преподаватели.фамилия AS "Преподаватель",
            Время.время_начала || '-' || Время.время_окончания AS "Время",
            Дни_недели.название AS "День недели",
            Аудитории.номер AS "Аудитория",
            Расписание.корпус AS "Корпус",
            Группы.название AS "Группа",
            Расписание.тип_занятия AS "Тип занятия"
        FROM Расписание
        JOIN Дисциплины ON Расписание.дисциплина_id = Дисциплины.дисциплина_id
        JOIN Преподаватели ON Расписание.преподаватель_id = Преподаватели.преподаватель_id
        JOIN Время ON Расписание.время_id = Время.время_id
        JOIN Дни_недели ON Расписание.день_id = Дни_недели.день_id
        JOIN Аудитории ON Расписание.аудитория_id = Аудитории.аудитория_id
        JOIN Группы ON Расписание.группа_id = Группы.группа_id
        WHERE 1=1
    """
    params = []
    if selected_group:
        query += " AND Группы.название = ?"
        params.append(selected_group)
    if selected_teacher:
        query += " AND Преподаватели.имя || ' ' || Преподаватели.фамилия = ?"
        params.append(selected_teacher)
    if selected_audience:
        query += " AND Аудитории.номер = ?"
        params.append(selected_audience)
    if selected_building:
        query += " AND Расписание.корпус = ?"
        params.append(selected_building)
    if week_parity:
        query += " AND Расписание.четность = ?"
        params.append(week_parity)
    if day_of_week:
        query += " AND Дни_недели.название = ?"
        params.append(day_of_week)
    if selected_type:
        query += " AND Расписание.тип_занятия = ?"
        params.append(selected_type)
    
    schedule = get_data(query, params)
    if schedule.empty:
        st.warning("По вашим фильтрам расписание не найдено.")
    else:
        st.dataframe(schedule)
