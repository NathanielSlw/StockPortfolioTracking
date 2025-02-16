import mysql.connector
from db_connection import get_db_connection

def execute_sql_script():
    # Établir la connexion
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL script pour créer les tables et insérer des données fictives
    sql_script = """
DROP DATABASE IF EXISTS FinanceDB;
CREATE DATABASE IF NOT EXISTS FinanceDB;
USE FinanceDB;

CREATE TABLE referentiel_fonds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    date_creation DATE NOT NULL
);

CREATE TABLE referentiel_instruments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    type_instrument ENUM('Action', 'Obligation', 'ETF', 'Matière première', 'Crypto-monnaie') NOT NULL,
    code_ISIN VARCHAR(12) UNIQUE NOT NULL,
    valeur_unitaire_actuelle DECIMAL(10, 2)
);

CREATE TABLE positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_fonds INT NOT NULL,
    id_instrument INT NOT NULL,
    quantite INT NOT NULL,
    valeur_unitaire DECIMAL(10,2) NOT NULL CHECK (valeur_unitaire >= 0),
    date_maj DATE NOT NULL,
    FOREIGN KEY (id_fonds) REFERENCES referentiel_fonds(id) ON DELETE CASCADE,
    FOREIGN KEY (id_instrument) REFERENCES referentiel_instruments(id) ON DELETE CASCADE
);

CREATE TABLE especes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_fonds INT NOT NULL,
    montant DECIMAL(10, 2) NOT NULL CHECK (montant >= 0),
    date_maj DATE NOT NULL,
    FOREIGN KEY (id_fonds) REFERENCES referentiel_fonds(id) ON DELETE CASCADE,
    UNIQUE KEY (id_fonds)
);

INSERT INTO referentiel_fonds (nom, description, date_creation) VALUES
('Fonds A', 'Fonds d''investissement diversifié visant une croissance à long terme', '2020-01-01'),
('Fonds B', 'Fonds axé sur les investissements responsables et durables', '2021-07-10'),
('Fonds C', 'Fonds spécialisé dans les entreprises technologiques innovantes', '2019-03-20');

INSERT INTO referentiel_instruments (nom, type_instrument, code_ISIN, valeur_unitaire_actuelle) VALUES
('Apple Inc', 'Action', 'AAPL', '0.00'),
('Tesla Inc', 'Action', 'TSLA', '0.00'),
('Google', 'Action', 'GOOGL', '0.00'),
('Microsoft Corp', 'Action', 'MSFT', '0.00'),
('Amazon.com Inc', 'Action', 'AMZN', '0.00'),
('Vanguard FTSE Developed Markets ETF', 'ETF', 'VEA', '0.00'),
('iShares MSCI Emerging Markets ETF', 'ETF', 'EEM', '0.00'),
('SPDR Gold Shares', 'ETF', 'GLD', 0.00),
('iShares Silver Trust', 'ETF', 'SLV', 0.00),
('Silver', 'Matière première', 'SI=F', '0.00');

INSERT INTO positions (id_fonds, id_instrument, quantite, valeur_unitaire, date_maj) VALUES
(1, 1, 100, 200.00, '2025-01-01'),
(1, 2, 50, 300.00, '2025-01-01'),
(1, 4, 30, 370.00, '2025-01-01'),
(3, 5, 200, 230.00, '2025-01-01'),
(3, 6, 1000, 43.00, '2025-01-01'),
(2, 7, 500, 50.00, '2025-01-01'),
(2, 8, 400, 150.00, '2025-01-01');
"""


    # Diviser le script en instructions individuelles
    statements = sql_script.split(';')

    # Exécuter chaque instruction séparément
    for statement in statements:
        if statement.strip():
            try:
                cursor.execute(statement)
            except mysql.connector.Error as err:
                print(f"Error executing: {statement[:50]}...")
                print(f"Error message: {err}")

    conn.commit()
    cursor.close()
    conn.close()

