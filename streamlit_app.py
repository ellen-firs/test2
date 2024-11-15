import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# Функция для получения данных из базы данных
def get_data(query, params):
    conn = sqlite3.connect('schedule.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query, params)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=columns)

# Функция для получения доступных опций для селектбоксов
def get_choices(query):
    conn = sqlite3.connect('schedule.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Функция для получения дней недели из базы данных
def get_days_of_week():
    conn = sqlite3.connect('schedule.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT название FROM Дни_недели ORDER BY день_id")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Функция для определения четности недели
def get_week_parity(date):
    # 2 сентября 2024 года - нечетная неделя (это будем считать стартом отсчета)
    start_date = datetime(2024, 9, 2)  # 2 сентября 2024
    delta = date - start_date
    week_number = delta.days // 7
    return 'нечетная' if week_number % 2 != 0 else 'четная'

# Функция для определения дня недели
def get_day_of_week(date):
    days_of_week = get_days_of_week()  # Получаем дни недели из базы
    return days_of_week[date.weekday()]  # Преобразуем день недели в строку (например, 'Понедельник')

# Функция для фильтрации с автодополнением
def filter_choices(choices, query):
    return [choice for choice in choices if query.lower() in choice.lower()]

# Загружаем доступные значения для селектбоксов
groups = get_choices("SELECT название FROM Группы")
teachers = get_choices("SELECT имя || ' ' || фамилия FROM Преподаватели")
audiences = get_choices("SELECT номер FROM Аудитории")
buildings = get_choices("SELECT DISTINCT корпус FROM Расписание")

# Ввод даты
selected_date = st.date_input("Выберите дату", datetime.today())

# Преобразуем строку в объект datetime
selected_date = datetime.strptime(str(selected_date), '%Y-%m-%d')

# Определяем день недели и четность недели на основе выбранной даты
day_of_week = get_day_of_week(selected_date)
week_parity = get_week_parity(selected_date)

# Отображаем выбранные день недели и четность
st.write(f"Выбранная дата: {selected_date.date()}")
st.write(f"Это {day_of_week} и {week_parity} неделя.")

# Ввод группы с автодополнением
group_input = st.text_input("Введите название группы", "")
filtered_groups = filter_choices(groups, group_input)
selected_group = st.selectbox("Выберите группу", [""] + filtered_groups)

# Ввод преподавателя с автодополнением
teacher_input = st.text_input("Введите имя преподавателя", "")
filtered_teachers = filter_choices(teachers, teacher_input)
selected_teacher = st.selectbox("Выберите преподавателя", [""] + filtered_teachers)

# Ввод аудитории с автодополнением
audience_input = st.text_input("Введите номер аудитории", "")
filtered_audiences = filter_choices(audiences, audience_input)
selected_audience = st.selectbox("Выберите аудиторию", [""] + filtered_audiences)

# Ввод корпуса с автодополнением
building_input = st.text_input("Введите номер корпуса", "")
filtered_buildings = filter_choices(buildings, building_input)
selected_building = st.selectbox("Выберите корпус", [""] + filtered_buildings)

# Кнопка "Показать", чтобы выполнить запрос
if st.button("Показать расписание"):
    # Базовый запрос
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
        WHERE 1=1
    """
    
    params = []

    # Добавляем фильтры в запрос в зависимости от выбора пользователя
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
    
    # Добавляем проверку по четности недели
    query += " AND Расписание.четность = ?"
    params.append(week_parity)
    
    # Добавляем фильтрацию по дню недели
    query += " AND Дни_недели.название = ?"
    params.append(day_of_week)

    # Получаем данные из базы
    schedule = get_data(query, params)

    # Отображаем результаты
    if schedule.empty:
        st.warning("По вашим фильтрам расписание не найдено.")
    else:
        st.dataframe(schedule)

    # Показать выбранную четность недели
    st.write(f"Выбрана четность недели: {week_parity}")
