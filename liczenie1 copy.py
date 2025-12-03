import psycopg2
import pandas as pd

# --- A. Konfiguracja Połączenia ---
DB_NAME = "logistyka_db"
DB_USER = "postgres"
DB_PASS = "zabawka"  # Wpisz swoje hasło!
DB_HOST = "localhost"

# --- B. Zapytanie SQL (Analiza Opóźnień Przewoźników) ---
# To jest zapytanie, które stworzyliśmy w poprzednim kroku
SQL_QUERY = """
SELECT
    p.Nazwa,
    m.LiczbaJednostek,
    m.DataOstatniejWysyłki,
    AGE(CURRENT_DATE, m.DataOstatniejWysyłki) AS CzasNieaktywności
FROM
    Magazyn m
JOIN
    Produkty p ON m.ProduktID = p.ProduktID
WHERE
    m.DataOstatniejWysyłki IS NOT NULL
ORDER BY
    m.DataOstatniejWysyłki ASC
LIMIT 5;
"""

def pobierz_dane_i_analizuj():
    conn = None  # Inicjujemy połączenie
    try:
        # Nawiązanie połączenia z bazą
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST
        )
        print("Połączenie z bazą PostgreSQL udane.")

        # Użycie Pandas do wykonania zapytania SQL i załadowania wyników do DataFrame
        # DataFrame to Twoja "Tabela Excela" w Pythonie
        df = pd.read_sql_query(SQL_QUERY, conn)

        print("\n--- Wyniki w Pythonie (DataFrame) ---")
        print(df) # Wyświetlenie surowej tabeli w terminalu

        return df

    except psycopg2.Error as e:
        # Obsługa błędów połączenia/zapytania
        print(f"Wystąpił błąd podczas pracy z bazą: {e}")
        return None
    finally:
        # Zawsze zamykamy połączenie, by zwolnić zasoby
        if conn:
            conn.close()
            print("Połączenie z bazą zamknięte.")


if __name__ == "__main__":
    df_wyniki = pobierz_dane_i_analizuj()
    # Przejdziemy do wizualizacji w kolejnym kroku

# ... (Poprzedni kod) ...
import plotly.express as px

# ... (Funkcja pobierz_dane_i_analizuj) ...

if __name__ == "__main__":
    df_wyniki = pobierz_dane_i_analizuj()

    if df_wyniki is not None:
        print("\n--- Tworzenie Wizualizacji Martwego Zapasu ---")

        # 1. Musimy upewnić się, że 'nazwa' i 'liczba jednostek' są w odpowiedniej formie
        # Pandas automatycznie obniża nazwy kolumn na małe litery.
        df_wyniki.rename(columns={'liczbajednostek': 'Liczba_Jednostek'}, inplace=True)
        
        # 2. Tworzenie wykresu kołowego (Pie Chart)
        # Pokazuje, jaki procent zalegającego zapasu stanowi dany produkt
        fig = px.pie(
            df_wyniki,
            values='Liczba_Jednostek',  # Wielkość wycinka: liczba jednostek zalegających
            names='nazwa',  # Nazwa wycinka: nazwa produktu
            title='Udział TOP 5 Produktów w Zalegającym Zapasie',
            hole=.3, # Opcjonalnie: tworzy wykres typu 'donut'
        )
        
        # 3. Dodanie etykiet wewnątrz wykresu
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        # 4. Zapisanie wykresu do pliku HTML
        fig.write_html("raport_martwy_zapas.html")
        print("Wykres martwego zapasu zapisany jako raport_martwy_zapas.html. Otwórz w przeglądarce!")
