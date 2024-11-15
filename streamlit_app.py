import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Функция для подключения к базе данных
def get_connection():
    conn = sqlite3.connect("schedule.db")
    return conn

# Функция для загрузки расписания с фильтрами
def load_schedule(group_id=None, teacher_id=None, classroom_id=None, day=None, date=None):
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

    # Применяем фильтры
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
    if date:
        day_of_week = date.strftime('%A')  # Преобразуем дату в день недели
        query += " AND Дни_недели.название = ?"
        params.append(day_of_week)

    # Получаем данные
    schedule_df = pd.read_sql(query, conn, params=params)
    conn.close()
    return schedule_df

# Функция для получения всех уникальных значений для фильтров из БД
def get_unique_values():
    conn = get_connection()

    # Получаем уникальные значения для группы, преподавателя и аудитории
    groups = pd.read_sql("SELECT DISTINCT группа_id FROM Расписание", conn)
    teachers = pd.read_sql("SELECT DISTINCT преподаватель_id FROM Расписание", conn)
    classrooms = pd.read_sql("SELECT DISTINCT аудитория_id FROM Расписание", conn)
    
    conn.close()

    return groups['группа_id'].tolist(), teachers['преподаватель_id'].tolist(), classrooms['аудитория_id'].tolist()

# Основная функция Streamlit
def main():
    st.title("Расписание занятий")

    # Получаем уникальные значения для фильтров
    groups, teachers, classrooms = get_unique_values()

    # Фильтры для группы, преподавателя, аудитории
    group_id = st.selectbox('Выберите группу', groups)
    teacher_id = st.selectbox('Выберите преподавателя', teachers)
    classroom_id = st.selectbox('Выберите аудиторию', classrooms)

    date = st.date_input('Выберите дату', datetime.now())

    # Выбор отображения: Список или Сетка
    display_mode = st.radio("Выберите отображение:", ('Список', 'Сетка'))

    # Кнопки для отображения
    if st.button("Показать расписание"):
        schedule = load_schedule(group_id=group_id, teacher_id=teacher_id, classroom_id=classroom_id)
        if schedule.empty:
            st.write("Ура, выходной!")
        else:
            if display_mode == 'Список':
                st.write(schedule)
            else:
                st.table(schedule)

    if st.button("Показать расписание на сегодня"):
        schedule = load_schedule(group_id=group_id, date=date)
        if schedule.empty:
            st.write("Ура, выходной!")
        else:
            if display_mode == 'Список':
                st.write(schedule)
            else:
                st.table(schedule)

    # Выбор дня недели для отображения
    day_of_week = st.selectbox('Выберите день недели', ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'])
    
    if st.button(f"Показать расписание на {day_of_week}"):
        schedule = load_schedule(group_id=group_id, day=day_of_week)
        if schedule.empty:
            st.write("Ура, выходной!")
        else:
            if display_mode == 'Список':
                st.write(schedule)
            else:
                st.table(schedule)

if __name__ == "__main__":
    main()
