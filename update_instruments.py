import yfinance as yf
import mysql.connector
from db_connection import get_db_connection

# Fonction qui récupère le prix actuel d'une action via l'API Yahoo Finance
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        return float(stock.fast_info['last_price'])
    except Exception as e:
        print(f"Erreur lors de la récupération du prix pour {ticker}: {e}")
        return None

# Fonction principale pour mettre à jour les prix des instruments dans la base de données
def update_instruments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, code_ISIN FROM referentiel_instruments")
    instruments = cursor.fetchall()
    
    for instrument in instruments:
        prix = get_stock_price(instrument["code_ISIN"])
        if prix:
            cursor.execute(
                    "UPDATE referentiel_instruments SET valeur_unitaire_actuelle = %s WHERE id = %s",
                    (prix, instrument["id"])
                )
            conn.commit()
            print(f"Mise à jour de {instrument['code_ISIN']} : {prix} €")
        
    cursor.close()
    conn.close()

