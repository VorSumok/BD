import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Функция для подключения к базе данных
def connect_db():
    global conn, cursor
    try:
        conn = sqlite3.connect('База данных для гаражей.db')  # Имя файла базы данных
        cursor = conn.cursor()
        messagebox.showinfo("Успех", "Подключение к базе данных установлено!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")

# Функция для отключения от базы данных
def close_db():
    global conn, cursor
    if conn:
        conn.close()
        messagebox.showinfo("Успех", "Отключение от базы данных выполнено!")

def finish():
    close_db()
    root.destroy()  # ручное закрытие окна и всего приложения

# Функция для отображения данных в таблице
def display_data(table_name):
    global tree
    try:
        tree.delete(*tree.get_children())
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {e}")

# Функция для добавления новой записи
def add_record(table_name):
    def submit_record():
        values = []
        for i in range(len(entry_fields)):
            values.append(entry_fields[i].get())

        # Получение максимального ID из таблицы
        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = cursor.fetchone()[0]
        if max_id is None:
            max_id = 0  # Если таблица пустая, устанавливаем max_id в 0

        # Добавление 1 к максимальному ID
        new_id = max_id + 1

        # Добавление нового ID в начало списка значений
        values.insert(0, new_id)

        # Создание SQL-запроса для вставки данных
        query = f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(values))})"
        try:
            cursor.execute(query, values)
            conn.commit()
            messagebox.showinfo("Успех", "Новая запись добавлена!")
            display_data(table_name)
            add_window.destroy()  # Закрытие окна добавления
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

    add_window = tk.Toplevel(root)
    add_window.title(f"Добавить запись в {table_name}")

    # Определение полей для ввода данных
    entry_fields = []
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for column in columns:
        # Пропускаем столбец "id", так как он будет добавлен автоматически
        if column[1] == "id":
            continue

        label = tk.Label(add_window, text=column[1])
        label.grid(row=columns.index(column), column=0)
        entry = tk.Entry(add_window)
        entry.grid(row=columns.index(column), column=1)
        entry_fields.append(entry)

    submit_button = tk.Button(add_window, text="Добавить", command=submit_record)
    submit_button.grid(row=len(columns) + 1, column=0, columnspan=2)

# Функция для обновления записи
def update_record(table_name):
    def submit_update():
        record_id = id_entry.get()
        values = []
        for i in range(len(entry_fields)):
            values.append(entry_fields[i].get())

        # Создание SQL-запроса для обновления данных
        query = f"UPDATE {table_name} SET {','.join([f'{column[1]} = ?' for column in columns])} WHERE id = ?"
        try:
            cursor.execute(query, values + [record_id])
            conn.commit()
            messagebox.showinfo("Успех", "Запись обновлена!")
            display_data(table_name)
            update_window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

    update_window = tk.Toplevel(root)
    update_window.title(f"Обновить запись в {table_name}")

    # Определение поля для ввода ID записи
    id_label = tk.Label(update_window, text="ID записи:")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(update_window)
    id_entry.grid(row=0, column=1)

    # Определение полей для ввода новых данных
    entry_fields = []
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for i, column in enumerate(columns):

        # Пропускаем столбец "id", так как он не редактируется
        if column[1] == "id":
            entry_fields.append(id_entry)
            continue

        label = tk.Label(update_window, text=column[1])
        label.grid(row=i + 1, column=0)
        entry = tk.Entry(update_window)
        entry.grid(row=i + 1, column=1)
        entry_fields.append(entry)

    submit_button = tk.Button(update_window, text="Обновить", command=submit_update)
    submit_button.grid(row=len(columns) + 1, column=0, columnspan=2)

# Функция для удаления записи
def delete_record(table_name):
    def confirm_delete():
        record_id = id_entry.get()
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить запись с ID {record_id}?"):
            try:
                cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
                conn.commit()
                messagebox.showinfo("Успех", "Запись удалена!")
                display_data(table_name)
                delete_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления: {e}")

    delete_window = tk.Toplevel(root)
    delete_window.title(f"Удалить запись из {table_name}")

    # Определение поля для ввода ID записи
    id_label = tk.Label(delete_window, text="ID записи:")
    id_label.grid(row=0, column=0)
    id_entry = tk.Entry(delete_window)
    id_entry.grid(row=0, column=1)

    delete_button = tk.Button(delete_window, text="Удалить", command=confirm_delete)
    delete_button.grid(row=1, column=0, columnspan=2)

# Функция для открытия окна работы с таблицей
def open_table_window(table_name):
    global tree, add_button, update_button, delete_button
    try:
        # Очистка таблицы и обновление столбцов
        tree.delete(*tree.get_children())
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        tree.configure(columns=[column[1] for column in columns])
        for column in columns:
            tree.heading(column[1], text=column[1])

        # Отображение данных
        display_data(table_name)

        # Удаление старых кнопок, если они есть
        if add_button:
            add_button.destroy()
        if update_button:
            update_button.destroy()
        if delete_button:
            delete_button.destroy()

        # Создание новых кнопок
        add_button = tk.Button(button_frame, text="Добавить", command=lambda: add_record(table_name))
        add_button.pack(side=tk.LEFT, padx=10)
        update_button = tk.Button(button_frame, text="Обновить", command=lambda: update_record(table_name))
        update_button.pack(side=tk.LEFT, padx=10)
        delete_button = tk.Button(button_frame, text="Удалить", command=lambda: delete_record(table_name))
        delete_button.pack(side=tk.LEFT, padx=10)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка: {e}")

def search_data(table_name, search_criteria, search_value):
    global tree
    tree.delete(*tree.get_children())

    if table_name == "Renters" and search_criteria == "Поиск арендатора по номеру автомобиля":
        # Поиск арендатора по номеру автомобиля
        cursor.execute(f"""
            SELECT Renters.*
            FROM Renters
            JOIN Rent ON Renters.id = Rent.арендатор_id
            JOIN Garages ON Rent.гараж_id = Garages.id
            JOIN Cars ON Garages.id = Cars.гараж_id
            WHERE Cars.номер = ?
        """, (search_value,))
    elif table_name == "Rent" and search_criteria == "Поиск контрактов по дате начала":
        # Поиск контрактов по дате начала
        cursor.execute(f"SELECT * FROM {table_name} WHERE дата_начала = ?", (search_value,))
    elif table_name == "Rent" and search_criteria == "Поиск контрактов по дате конца":
        # Поиск контрактов по дате конца
        cursor.execute(f"SELECT * FROM {table_name} WHERE дата_окончания = ?", (search_value,))
    elif table_name == "Garages" and search_criteria == "Поиск гаражей по ID владельца":
        # Поиск гаражей по ID владельца
        cursor.execute(f"SELECT * FROM {table_name} WHERE владелец_id = ?", (search_value,))
    else:
        # Некорректный критерий поиска
        messagebox.showerror("Ошибка", "Некорректный критерий поиска.")
        return

    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)

# Функция для выполнения SQL-запроса
# Функция для открытия окна SQL-запросов
def open_sql_window():

    def execute_sql():
        query = sql_entry.get()
        try:
            cursor.execute(query)
            conn.commit()
            results = cursor.fetchall()

            # Очистка предыдущих данных в таблице
            tree.delete(*tree.get_children())

            # Отображение результатов в таблице
            for row in results:
                tree.insert("", tk.END, values=row)

            messagebox.showinfo("Успех", "Запрос выполнен успешно!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения запроса: {e}")
        sql_entry.delete(0, tk.END)

    sql_window = tk.Toplevel(root)
    sql_window.title("Выполнить SQL-запрос")

    # Поле для ввода SQL-запроса
    sql_label = tk.Label(sql_window, text="SQL-запрос:")
    sql_label.grid(row=0, column=0)
    sql_entry = tk.Entry(sql_window)
    sql_entry.grid(row=0, column=1)

    # Кнопка выполнения SQL-запроса
    sql_button = tk.Button(sql_window, text="Выполнить", command=execute_sql)
    sql_button.grid(row=1, column=0, columnspan=2)

# Функция для сортировки таблицы
def sort_table(column, reverse):
    global tree

    # Получение данных из таблицы
    data = []
    for i in range(tree.get_children().__len__()):
        data.append(tree.item(tree.get_children()[i])['values'])

    tree.delete(*tree.get_children())

    # Сортировка данных по выбранному столбцу
    data.sort(key=lambda row: row[column], reverse=reverse)

    # Вставка отсортированных данных в таблицу
    for row in data:
        tree.insert("", tk.END, values=row)


# Создание основного окна
root = tk.Tk()
root.geometry("1000x500")
root.title("База данных гаражей")

connect_db()

# Создание меню
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Подключиться", command=connect_db)
filemenu.add_command(label="Отключиться", command=close_db)
filemenu.add_separator()
filemenu.add_command(label="Сортировать по возрастанию", command=lambda: sort_table(column_index, False))
filemenu.add_command(label="Сортировать по убыванию", command=lambda: sort_table(column_index, True))
filemenu.add_separator()
filemenu.add_command(label="Выход", command=root.quit)
menubar.add_cascade(label="Меню", menu=filemenu)
root.config(menu=menubar)

# Создание фрейма для таблицы
table_frame = tk.Frame(root)
table_frame.pack(pady=20)

# Создание таблицы
tree = ttk.Treeview(table_frame, show="headings")
tree.pack()

# Создание фрейма для кнопок
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Инициализация кнопок (первоначально они невидимы)
global add_button, update_button, delete_button, column, column_index
add_button = None
update_button = None
delete_button = None
column = 0
column_index = 0

# Создание меню выбора таблицы
table_menu = tk.Menu(root, tearoff=0)
table_menu.add_command(label="Renters", command=lambda: open_table_window("Renters"))
table_menu.add_command(label="Rent", command=lambda: open_table_window("Rent"))
table_menu.add_command(label="Owners", command=lambda: open_table_window("Owners"))
table_menu.add_command(label="Cars", command=lambda: open_table_window("Cars"))
table_menu.add_command(label="Garages", command=lambda: open_table_window("Garages"))
table_menu.add_separator()
table_menu.add_command(label="Выполнить SQL-запрос", command=open_sql_window)

# Кнопка для вызова меню выбора таблицы
table_button = tk.Button(root, text="Выбрать таблицу", command=lambda: table_menu.post(root.winfo_rootx(), root.winfo_rooty()))
table_button.pack(pady=10)

# Создание фрейма для поиска данных
search_frame = tk.Frame(root)
search_frame.pack(pady=10)

# Поля для ввода критерия и значения поиска
search_criteria_label = tk.Label(search_frame, text="Критерий поиска:")
search_criteria_label.grid(row=0, column=0)
search_criteria_var = tk.StringVar(search_frame)
search_criteria_var.set("Поиск арендатора по номеру автомобиля")  # По умолчанию - поиск арендатора по номеру авто
search_criteria_menu = tk.OptionMenu(search_frame, search_criteria_var,
                                     "Поиск арендатора по номеру автомобиля", "Поиск контрактов по дате начала", "Поиск контрактов по дате конца", "Поиск гаражей по ID владельца")
search_criteria_menu.grid(row=0, column=1)

search_value_label = tk.Label(search_frame, text="Значение поиска:")
search_value_label.grid(row=1, column=0)
search_value_entry = tk.Entry(search_frame)
search_value_entry.grid(row=1, column=1)

# Кнопка поиска
search_button = tk.Button(search_frame, text="Поиск",
                        command=lambda: search_data(table_menu.entrycget(0, "label"),
                                                  search_criteria_var.get(),
                                                  search_value_entry.get()))
search_button.grid(row=2, column=0, columnspan=2)

def on_header_click(event):
    global column_index
    column = tree.identify_column(event.x)  # Получение номера столбца
    column_index = int(column[1:]) - 1  # Преобразование номера столбца в индекс

# Привязка обработчика к событию клика по заголовкам столбцов
tree.bind("<Button-1>", on_header_click)

root.protocol("WM_DELETE_WINDOW", finish)

# Запуск графического интерфейса
root.mainloop()