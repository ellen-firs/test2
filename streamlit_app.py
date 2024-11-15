import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Подключение к базе данных
def get_connection():
    conn = sqlite3.connect("schedule.db")
    return conn

# Загрузка расписания на основе фильтров
def load_schedule(group_id=None, teacher_id=None, classroom_id=None, day=None, week_type=None, date=None):
    conn = get_connection()
    query = """
    SELECT
        Дисциплины.название AS Дисциплина,
        Преподаватели.имя || ' ' || Преподаватели.фамилия AS Преподаватель,
        Время.время_начала || ' - ' || Время.время_окончания AS Время,
        Аудитории.номер AS Аудитория,
        Расписание.корпус AS Корпус,
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

# Основная функция
def main():
    st.title("Расписание занятий")
    
    # Выбор группы
    group_id = st.selectbox('Выберите группу', ['A-01-21', 'A-02-21', 'B-01-21'])  # Пример
    # Фильтры
    teacher_id = st.selectbox('Выберите преподавателя', ['Преподаватель 1', 'Преподаватель 2'])  # Пример
    classroom_id = st.selectbox('Выберите аудиторию', ['C-409', 'B-308', 'M-307'])  # Пример
    date = st.date_input('Выберите дату', datetime.now())

    # Кнопки для отображения
    if st.button("Показать расписание"):
        schedule = load_schedule(group_id=group_id, teacher_id=teacher_id, classroom_id=classroom_id)
        st.write(schedule)

    if st.button("Показать расписание на сегодня"):
        schedule = load_schedule(group_id=group_id, date=date)
        if schedule.empty:
            st.write("Ура, выходной!")
        else:
            st.write(schedule)

    # Выбор дня недели
    day_of_week = st.selectbox('Выберите день недели', ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'])
    
    if st.button(f"Показать расписание на {day_of_week}"):
        schedule = load_schedule(group_id=group_id, day=day_of_week)
        if schedule.empty:
            st.write("Ура, выходной!")
        else:
            st.write(schedule)

if __name__ == "__main__":
    main()
