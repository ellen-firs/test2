import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Подключение к базе данных SQLite
def get_connection():
    return sqlite3.connect("schedule.db")

# Загрузка групп из базы данных
def load_groups():
    conn = get_connection()
    groups_df = pd.read_sql("SELECT группа_id, название FROM Группы", conn)
    conn.close()
    return groups_df

# Загрузка преподавателей из базы данных
def load_teachers():
    conn = get_connection()
    teachers_df = pd.read_sql("SELECT преподаватель_id, имя || ' ' || фамилия AS имя_фамилия FROM Преподаватели", conn)
    conn.close()
    return teachers_df

# Загрузка аудиторий из базы данных
def load_classrooms():
    conn = get_connection()
    classrooms_df = pd.read_sql("SELECT аудитория_id, номер FROM Аудитории", conn)
    conn.close()
    return classrooms_df

# Загрузка дней недели из базы данных
def load_days_of_week():
    conn = get_connection()
    days_df = pd.read_sql("SELECT день_id, название FROM Дни_недели ORDER BY день_id", conn)
    conn.close()
    return days_df

# Загрузка расписания на основе фильтров
def load_schedule(group_id=None, teacher_id=None, classroom_id=None, day=None, week_type=None, date=None):
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
    WHERE 1=1
    """
    params = []

    if group_id:
        query += " AND Расписание.группа_id = ?"
        params.append(group_id)
    if teacher_id:
        query += " AND Расписание.преподаватель_id = ?"
        params.append(teacher_id)
    if classroom_id:
        query += " AND Расписание.аудитория_id = ?"
        params.append(classroom_id)
    if day:
        query += " AND Дни_недели.название = ?"
        params.append(day)
    if week_type:
        query += " AND Расписание.четность_недели = ?"
        params.append(week_type)
    if date:
        day_of_week = date.strftime('%A')
        query += " AND Дни_недели.название = ?"
        params.append(day_of_week)

    schedule_df = pd.read_sql(query, conn, params=params)
    conn.close()
    return schedule_df

# Определение типа недели (четная/нечетная)
def get_week_type():
    current_week = datetime.now().isocalendar()[1]
    return 'четная' if current_week % 2 == 0 else 'нечетная'

# Интерфейс Streamlit
st.title("Расписание занятий")

# Загрузка данных
groups = load_groups()
teachers = load_teachers()
classrooms = load_classrooms()
days_of_week = load_days_of_week()

# Фильтры
selected_group = st.selectbox("Выберите группу:", ["Все"] + list(groups['название']))
selected_teacher = st.selectbox("Выберите преподавателя:", ["Все"] + list(teachers['имя_фамилия']))
selected_classroom = st.selectbox("Выберите аудиторию:", ["Все"] + list(classrooms['номер']))
week_type = st.selectbox("Выберите тип недели:", ["четная", "нечетная"])
selected_day = st.selectbox("Выберите день недели:", ["Все"] + list(days_of_week['название']))
selected_date = st.date_input("Выберите дату")

# Выбор отображения
display_option = st.radio("Выберите формат отображения:", ["Список", "Сетка"])

# Кнопка для отображения расписания
if st.button("Показать расписание"):
    group_id = groups.loc[groups['название'] == selected_group, 'группа_id'].iloc[0] if selected_group != "Все" else None
    teacher_id = teachers.loc[teachers['имя_фамилия'] == selected_teacher, 'преподаватель_id'].iloc[0] if selected_teacher != "Все" else None
    classroom_id = classrooms.loc[classrooms['номер'] == selected_classroom, 'аудитория_id'].iloc[0] if selected_classroom != "Все" else None
    day = selected_day if selected_day != "Все" else None

    schedule = load_schedule(group_id, teacher_id, classroom_id, day, week_type, selected_date)
    
    if schedule.empty:
        st.write("Ура, выходной!")
    else:
        if display_option == "Список":
            st.write(schedule)
        elif display_option == "Сетка":
            st.write(schedule.style.set_properties(**{'text-align': 'center'}))
