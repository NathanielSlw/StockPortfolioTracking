import mysql.connector

# A MODIFIER : Configuration de la connexion à MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      
        user="root",            # A MODIFIER
        password="P@ssword123", # A MODIFIER
        database="FinanceDB"
    )