 import sqlite3
import os
import time
from pathlib import Path

def init_db():
    # Zajistíme existenci adresáře
    Path("data").mkdir(exist_ok=True)
    
    db_path = 'data/databaze.db'
    
    # Pokud soubor existuje a je poškozený
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            print("Čekám na uvolnění souboru...")
            time.sleep(2)  # Počkáme 2 sekundy
            os.remove(db_path)
    
    # Vytvoříme novou databázi
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE jidla
                    (id INTEGER PRIMARY KEY, 
                     nazev TEXT NOT NULL, 
                     popis TEXT, 
                     cena REAL NOT NULL)''')
        
        c.execute('''CREATE TABLE objednavky
                    (id INTEGER PRIMARY KEY,
                     jidlo_id INTEGER NOT NULL,
                     jmeno TEXT NOT NULL,
                     datum TEXT NOT NULL,
                     stav TEXT DEFAULT 'nova',
                     FOREIGN KEY (jidlo_id) REFERENCES jidla(id))''')
        
        c.execute('''CREATE TABLE admini
                    (id INTEGER PRIMARY KEY,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL)''')
        
        # Přidání výchozího admina
        from werkzeug.security import generate_password_hash
        c.execute("INSERT INTO admini (username, password) VALUES (?, ?)",
                 ('admin', generate_password_hash('admin')))
        
        conn.commit()
        print("Databáze úspěšně vytvořena!")
        
    except sqlite3.Error as e:
        print(f"Chyba databáze: {e}")
        if conn:
            conn.close()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()
