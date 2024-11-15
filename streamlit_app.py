import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.html('<head><script src="https://telegram.org/js/telegram-web-app.js"></script></head>')

# Функция для подключения к базе данных SQLite
def get_connection():
    return sqlite3.connect("schedule.db")

# Загрузка групп из базы данных
def load_groups():
    conn = get_connection()
    query = "SELECT группа_id, название FROM Группы"
    groups_df = pd.read_sql(query, conn)
    conn.close()
    return groups_df

# Загрузка дней недели из базы данных
def load_days_of_week():
    conn = get_connection()
    query = "SELECT день_id, название FROM Дни_недели ORDER BY день_id"
    days_df = pd.read_sql(query, conn)
    conn.close()
    return days_df

# Загрузка расписания для конкретной группы, дня и четности недели
def load_schedule(group_id, day, week_type):
    conn = get_connection()
    query = """
    SELECT
        Дисциплины.название AS Дисциплина,
        Преподаватели.имя || ' ' || Преподаватели.фамилия AS Преподаватель,
        Время.время_начала || ' - ' || Время.время_окончания AS Время,
        Аудитории.номер AS Аудитория,
        Расписание.ккорпус AS Корпус,
        Дни_недели.название AS День
    FROM Расписание
    JOIN Дисциплины ON Расписание.дисциплина_id = Дисциплины.дисциплина_id
    JOIN Преподаватели ON Расписание.преподаватель_id = Преподаватели.преподаватель_id
    JOIN Время ON Расписание.время_id = Время.время_id
    JOIN Дни_недели ON Расписание.день_id = Дни_недели.день_id
    JOIN Аудитории ON Расписание.аудитория_id = Аудитории.аудитория_id
    WHERE Расписание.группа_id = ? AND Дни_недели.название = ? AND Расписание.четность_недели = ?
    ORDER BY Время.время_начала;
    """
    schedule_df = pd.read_sql(query, conn, params=(group_id, day, week_type))
    conn.close()
    return schedule_df

# Определение текущего типа недели (четная/нечетная)
def get_week_type():
    current_week = datetime.now().isocalendar()[1]
    return 'четная' if current_week % 2 == 0 else 'нечетная'

# Интерфейс Streamlit
st.title("Расписание занятий")

# Загрузка данных из базы данных
groups = load_groups()
days_of_week = load_days_of_week()

# Выбор группы
group_names = dict(zip(groups['название'], groups['группа_id']))
selected_group = st.selectbox("Выберите группу:", list(group_names.keys()))

# Выбор типа недели (четная или нечетная)
week_type = get_week_type()
week_type = st.selectbox("Выберите тип недели:", ['четная', 'нечетная'], index=(0 if week_type == 'четная' else 1))

# Выбор дня недели
selected_day = st.selectbox("Выберите день недели:", list(days_of_week['название']))

# Кнопка для отображения расписания
if st.button("Показать расписание"):
    if selected_group and selected_day:
        group_id = group_names[selected_group]
        schedule = load_schedule(group_id, selected_day, week_type)
        
        if schedule.empty:
            st.write("Ура, выходной!")
        else:
            # Выводим расписание в виде таблицы
            st.write(f"Расписание для группы {selected_group} на {selected_day} ({week_type} неделя):")
            st.write(schedule.reset_index(drop=True))
    else:
        st.write("Пожалуйста, выберите группу и день недели.")
