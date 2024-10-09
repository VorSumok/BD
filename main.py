import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

global conn, cursor
# Функция для подключения к базе данных
def connect_db():
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


# Функция для отображения данных в таблице
def display_data(table_name):
    global tree
    tree.delete(*tree.get_children())
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)


# Функция для добавления новой записи
def add_record(table_name):
    def submit_record():
        values = []
        for i in range(len(entry_fields)):
            values.append(entry_fields[i].get())

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


# Создание основного окна
root = tk.Tk()
root.title("База данных гаражей")

# Создание меню
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Подключиться", command=connect_db)
filemenu.add_command(label="Отключиться", command=close_db)
filemenu.add_separator()
filemenu.add_command(label="Выход", command=root.quit)
menubar.add_cascade(label="Файл", menu=filemenu)
root.config(menu=menubar)

# Создание фрейма для таблицы
table_frame = tk.Frame(root)
table_frame.pack(pady=20)

# Создание таблицы
tree = ttk.Treeview(table_frame, columns=("id", "дата_покупки", "дата_продажи", "владелец_id", "цена"), show="headings")
tree.heading("id", text="ID")
tree.heading("дата_покупки", text="Дата покупки")
tree.heading("дата_продажи", text="Дата продажи")
tree.heading("владелец_id", text="ID владельца")
tree.heading("цена", text="Цена")
tree.pack()

# Создание кнопок для управления данными
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Кнопка добавления записи
add_button = tk.Button(button_frame, text="Добавить", command=lambda: add_record("Garages"))
add_button.pack(side=tk.LEFT, padx=10)

# Кнопка обновления записи
update_button = tk.Button(button_frame, text="Обновить", command=lambda: update_record("Garages"))
update_button.pack(side=tk.LEFT, padx=10)

# Кнопка удаления записи
delete_button = tk.Button(button_frame, text="Удалить", command=lambda: delete_record("Garages"))
delete_button.pack(side=tk.LEFT, padx=10)

# Отображение данных по умолчанию

# Запуск графического интерфейса
root.mainloop()