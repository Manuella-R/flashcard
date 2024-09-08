import mysql.connector
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style


conn = mysql.connector.connect(
    host="localhost",          # Server (XAMPP runs MySQL on localhost)
    user="root",               # Your MySQL username (default is 'root')
    password="",               # Your MySQL password (leave it empty if there's no password)
    database="flash"         # Name of the database you want to connect to
)

def create_tables(conn):
    cursor = conn.cursor()
    
    # Creating flashcard_sets table
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS flashcard_sets(
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   name VARCHAR(255) NOT NULL)
    ''')
    
    # Creating flashcard table
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS flashcard(
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   set_id INT NOT NULL,
                   word VARCHAR(255) NOT NULL,
                   definition TEXT NOT NULL,
                   FOREIGN KEY (set_id) REFERENCES flashcard_sets(id)
                   )
    ''')
    
    conn.commit()

def add_set(conn, name):
    cursor = conn.cursor()
    
    # Inserting into flashcard_sets table
    cursor.execute('''
      INSERT INTO flashcard_sets (name)
      VALUES (%s)
    ''', (name,))
    
    set_id = cursor.lastrowid  # Get the last inserted ID
    conn.commit()
    
    return set_id

def add_card(conn, set_id, word, definition):
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO flashcard(set_id, word, definition)
        VALUES (%s, %s, %s)
    ''', (set_id, word, definition))

    card_id = cursor.lastrowid
    conn.commit()

    return card_id

def get_sets(conn):
    cursor = conn.cursor()

    cursor.execute('''
       SELECT id, name FROM flashcard_sets
    ''')

    rows = cursor.fetchall()
    sets = {row[1]: row[0] for row in rows}

    return sets

def get_cards(conn, set_id):
    cursor = conn.cursor()

    cursor.execute('''
       SELECT word, definition FROM flashcard
       WHERE set_id = %s
    ''', (set_id,))

    rows = cursor.fetchall()
    cards = [(row[0], row[1]) for row in rows]

    return cards

def delete_set(conn, set_id):
    cursor = conn.cursor()

    cursor.execute('''
       DELETE FROM flashcard_sets
       WHERE id = %s
    ''', (set_id,))

    conn.commit()
    sets_combobox.set('')
    clear_flashcard_display()
    populate_sets_combobox()

    global current_cards, card_index
    current_cards = []
    card_index = 0

def create_set():
    set_name = set_name_var.get()
    if set_name:
        set_id = add_set(conn, set_name)
        populate_sets_combobox()
        set_name_var.set('')

def add_word():
    set_name = sets_combobox.get()
    word = word_var.get()
    definition = definition_var.get()

    if set_name and word and definition:
        sets = get_sets(conn)
        if set_name not in sets:
            set_id = add_set(conn, set_name)
        else:
            set_id = sets[set_name]

        add_card(conn, set_id, word, definition)

        word_var.set('')
        definition_var.set('')

        populate_sets_combobox()

def delete_selected_set():
    set_name = sets_combobox.get()

    if set_name:
        result = messagebox.askyesno(
            'Confirmation', f'Are you sure you want to delete the "{set_name}" set?'
        )
      
        if result:
            set_id = get_sets(conn)[set_name]
            delete_set(conn, set_id)
            populate_sets_combobox()
            clear_flashcard_display()

def select_set():
    set_name = sets_combobox.get()

    if set_name:
        set_id = get_sets(conn)[set_name]
        cards = get_cards(conn, set_id)

        if cards:
            display_flashcards(cards)
        else: 
            word_label.config(text="No cards available")
            definition_label.config(text='')

def display_flashcards(cards):
    global card_index
    global current_cards

    card_index = 0
    current_cards = cards

    if not cards:
        clear_flashcard_display()
    else:
        show_card()

def show_card():
    global card_index
    global current_cards

    if current_cards:
        if 0 <= card_index < len(current_cards):
            word, _ = current_cards[card_index]
            word_label.config(text=word)
            definition_label.config(text='')
        else:
            clear_flashcard_display()
    else:
        clear_flashcard_display()

def flip_card():
    global card_index
    global current_cards

    if current_cards:
        _, definition = current_cards[card_index]
        definition_label.config(text=definition)

def next_card():
    global card_index
    global current_cards

    if current_cards:
        card_index = min(card_index + 1, len(current_cards) - 1)
        show_card()

def prev_card():
    global card_index
    global current_cards

    if current_cards:
        card_index = max(card_index - 1, 0) 
        show_card()

def populate_sets_combobox():
    sets_combobox['values'] = tuple(get_sets(conn).keys())

def clear_flashcard_display():
    word_label.config(text='')
    definition_label.config(text='')

if __name__ == '__main__':
    create_tables(conn)

# Initialize Tkinter root window
root = tk.Tk()
root.title('Flashcards App')
root.geometry('500x400')

# Apply ttkbootstrap styling
style = Style(theme='superhero')
style.configure('TLabel', font=('TkDefaultFont', 18))
style.configure('TButton', font=('TkDefaultFont', 16))

# Variables for holding input data
set_name_var = tk.StringVar()
word_var = tk.StringVar()
definition_var = tk.StringVar()

# Notebook for tabbed interface
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Create Set Frame
create_set_frame = ttk.Frame(notebook)
notebook.add(create_set_frame, text='Create Set')

ttk.Label(create_set_frame, text='Set Name:').pack(padx=5, pady=5)
ttk.Entry(create_set_frame, textvariable=set_name_var, width=30).pack(padx=5, pady=5)

ttk.Label(create_set_frame, text='Word:').pack(padx=5, pady=5)
ttk.Entry(create_set_frame, textvariable=word_var, width=30).pack(padx=5, pady=5)

ttk.Label(create_set_frame, text='Definition:').pack(padx=5, pady=5)
ttk.Entry(create_set_frame, textvariable=definition_var, width=30).pack(padx=5, pady=5)

ttk.Button(create_set_frame, text='Add Word', command=add_word).pack(padx=5, pady=10)
ttk.Button(create_set_frame, text='Create Set', command=create_set).pack(padx=5, pady=10)

# Select Set Frame
select_set_frame = ttk.Frame(notebook)
notebook.add(select_set_frame, text="Select Set")

sets_combobox = ttk.Combobox(select_set_frame, state='readonly')
sets_combobox.pack(padx=5, pady=5)

ttk.Button(select_set_frame, text='Select Set', command=select_set).pack(padx=5, pady=10)
ttk.Button(select_set_frame, text='Delete Set', command=delete_selected_set).pack(padx=5, pady=10)

# Flashcards Frame
flashcards_frame = ttk.Frame(notebook)
notebook.add(flashcards_frame, text='Learn Mode')

word_label = ttk.Label(flashcards_frame, text='', font=('TkDefaultFont', 24))
word_label.pack(padx=5, pady=40)

definition_label = ttk.Label(flashcards_frame, text='')
definition_label.pack(padx=5, pady=5)

ttk.Button(flashcards_frame, text='Flip', command=flip_card).pack(padx=5, pady=5)
ttk.Button(flashcards_frame, text='Next', command=next_card).pack(padx=5, pady=5)
ttk.Button(flashcards_frame, text='Previous', command=prev_card).pack(padx=5, pady=5)

root.mainloop()
