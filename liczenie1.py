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
    Przewoznik,
    COUNT(DostawaID) AS LiczbaDostaw,
    SUM(CASE WHEN DataRzeczywista > DataPlanowana THEN 1 ELSE 0 END) AS LiczbaOpoznien,
    ROUND(
        (SUM(CASE WHEN DataRzeczywista > DataPlanowana THEN 1 ELSE 0 END) * 100.0) / COUNT(DostawaID), 2
    ) AS ProcentOpoznien
FROM
    Dostawy
GROUP BY
    Przewoznik
ORDER BY
    ProcentOpoznien DESC;
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
        print("\n--- Tworzenie Wizualizacji Plotly ---")

        # 1. Tworzenie wykresu słupkowego (Plotly Express)
        fig = px.bar(
            df_wyniki,
            x='przewoznik',  # Oś X: Nazwa przewoźnika
            y='procentopoznien',  # Oś Y: Procent Opóźnień
            title='Procent Opóźnień Dostaw wg Przewoźnika',
            labels={
                'przewoznik': 'Przewoźnik',
                'procentopoznien': 'Procent Opóźnień [%]'
            },
            color='procentopoznien', # Kolor słupków w zależności od wartości
            color_continuous_scale=px.colors.sequential.Reds # Używamy czerwonej skali, aby podkreślić ryzyko
        )
        
        # 2. Dodatkowe ustawienia (np. opis procentowy na słupkach)
        fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        
        # 3. Zapisanie wykresu do pliku HTML
        # Plik 'raport_opoznienia.html' zostanie otwarty w Twojej przeglądarce
        fig.write_html("raport_opoznienia.html")
        print("Wykres zapisany jako raport_opoznienia.html. Otwórz w przeglądarce!")