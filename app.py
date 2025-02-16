from flask import Flask, render_template, jsonify, request, redirect
import mysql.connector
from CreationTables import execute_sql_script                       # Script pour créer les tables de la base de données
from db_connection import get_db_connection                         # Connexion à la base de données
from update_instruments import update_instruments, get_stock_price  # Mise à jour des instruments et récupération des prix
from scheduler import start_scheduler                               # Scheduler pour mettre à jour le prix chaque minute 


# ------------------------------------------------------ INITIALISATION ------------------------------------------------------

app = Flask(__name__)
execute_sql_script()
update_instruments()
start_scheduler(app)

# ------------------------------------------------------ HOME ------------------------------------------------------
@app.route('/')
def index():
    return redirect('/fonds')
# -------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------ FONDS ------------------------------------------------------

# Route pour récupérer et afficher la liste des fonds avec leur valeur totale
@app.route('/fonds')
def fonds():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Récupère les fonds avec leur valeur totale calculée à partir des positions
    cursor.execute("""
        SELECT rf.*, COALESCE(SUM(p.quantite * p.valeur_unitaire), 0) AS valeur_totale
        FROM referentiel_fonds rf
        LEFT JOIN positions p ON rf.id = p.id_fonds
        GROUP BY rf.id
    """)
    fonds = cursor.fetchall()
    
    # Récuperer tous les instruments disponibles pour les afficher dans le menu déroulant de la modale d'ajout d'instrument
    cursor.execute('SELECT * FROM referentiel_instruments')
    instruments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('fonds/fonds.html', fonds=fonds, instruments=instruments)


# Route pour ajouter un nouveau fonds
@app.route('/ajouter_fonds', methods=['POST'])
def ajouter_fonds():
    nom = request.form['nom']
    description = request.form['description']
    date_creation = request.form['date_creation']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO referentiel_fonds (nom, description, date_creation) VALUES (%s, %s, %s)", (nom, description, date_creation))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/fonds')

# Route pour supprimer un fonds
@app.route('/supprimer_fonds/<int:id>')
def supprimer_fonds(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM referentiel_fonds WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/fonds')

# Route pour modifier un fonds
@app.route('/modifier_fonds/<int:id>', methods=['GET', 'POST'])
def modifier_fonds(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        date_creation = request.form['date_creation']
        cursor.execute("UPDATE referentiel_fonds SET nom = %s, description = %s, date_creation = %s WHERE id = %s", (nom, description, date_creation, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/fonds')

    cursor.execute("SELECT * FROM referentiel_fonds WHERE id = %s", (id,))
    fonds = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('fonds/modifier_fonds.html', fonds=fonds)

# Route pour ajouter un nouvel instrument à un fonds X
@app.route('/ajouter_instrument_fonds', methods=['POST'])
def ajouter_instrument_fonds():
    fonds_id = request.form['fonds_id']
    instrument_id = request.form['instrument_id']
    quantite = request.form['quantite']

    # Obtenir la valeur de l'instrument
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT valeur_unitaire_actuelle FROM referentiel_instruments WHERE id = %s', (instrument_id,))
    instrument = cursor.fetchone()

    if instrument:
        valeur_unitaire = instrument['valeur_unitaire_actuelle']
        # Ajouter l'instrument dans la table positions
        cursor.execute("""
            INSERT INTO positions (id_fonds, id_instrument, quantite, valeur_unitaire, date_maj)
            VALUES (%s, %s, %s, %s, CURDATE())
        """, (fonds_id, instrument_id, quantite, valeur_unitaire))
        conn.commit()

    cursor.close()
    conn.close()

    return redirect(f'/positions/{fonds_id}')

# -------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------ INSTRUMENTS ------------------------------------------------------

# Route pour afficher tous les instruments
@app.route('/instruments')
def instruments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM referentiel_instruments')
    instruments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('instruments/instruments.html', instruments=instruments)

# Route pour ajouter un nouvel instrument à la BDD s'il n'existe pas déjà
@app.route('/add_instrument', methods=['POST'])
def add_instrument():
    try:
        nom = request.form['nom'].strip()
        type_instrument = request.form['type_instrument']
        code_ISIN = request.form['code_ISIN'].strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifie si l'instrument existe déjà
        cursor.execute("SELECT 1 FROM referentiel_instruments WHERE code_ISIN = %s", 
                      (request.form['code_ISIN'],))
        
        if cursor.fetchone():
            return "Instrument déjà existant", 400
        
        prix = get_stock_price(code_ISIN) or 0.00
         
        # Si n'existe pas, on l'ajoute
        cursor.execute("""
            INSERT INTO referentiel_instruments (nom, type_instrument, code_ISIN, valeur_unitaire_actuelle)
            VALUES (%s, %s, %s, %s)
        """, (nom, type_instrument, code_ISIN, prix))
        
        conn.commit()
        
        return redirect('/instruments')
            
    except Exception as e:
        return str(e), 500
    finally:
        cursor.close()
        conn.close()

# Route pour chercher un instrument en fonction de son Nom ou Type 
@app.route('/search_instruments')
def search_instruments():
    search = request.args.get('search')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search:
        query = """
            SELECT * FROM referentiel_instruments
            WHERE nom LIKE %s OR type_instrument LIKE %s
        """
        search_param = f"%{search}%"
        cursor.execute(query, (search_param, search_param))
    else:
        cursor.execute('SELECT * FROM referentiel_instruments')

    instruments = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(instruments=instruments)

# -----------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------ POSITIONS ------------------------------------------------------

# Route pour afficher la liste des fonds dans le menu déroulant
@app.route('/positions')
def positions_selection():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nom FROM referentiel_fonds')
    fonds = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('positions/positions_selection.html', fonds=fonds)


# Route pour afficher les positions d'un fonds
@app.route('/positions/<int:fonds_id>')
def positions(fonds_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Récupérer le nom du fonds à afficher
    cursor.execute('SELECT nom FROM referentiel_fonds WHERE id = %s', (fonds_id,))
    fonds = cursor.fetchone()

    # Récupérer les positions agrégées par instrument
    cursor.execute('''
    SELECT i.nom AS nom_instrument, 
           i.id AS instrument_id,
           SUM(p.quantite) AS total_quantite, 
           SUM(p.valeur_unitaire * p.quantite) / SUM(p.quantite) AS prix_moyen, 
           SUM(p.quantite * p.valeur_unitaire) AS prix_total_investi,
           i.valeur_unitaire_actuelle, 
           SUM(p.quantite * i.valeur_unitaire_actuelle) AS prix_reel, 
           CASE 
               WHEN SUM(p.quantite * p.valeur_unitaire) = 0 THEN 0
               ELSE (SUM(p.quantite * i.valeur_unitaire_actuelle) - SUM(p.quantite * p.valeur_unitaire)) / SUM(p.quantite * p.valeur_unitaire) * 100
           END AS plus_value_pourcentage
    FROM positions p
    JOIN referentiel_instruments i ON p.id_instrument = i.id
    WHERE p.id_fonds = %s
    GROUP BY i.nom, i.id, i.valeur_unitaire_actuelle  -- Ajoute i.id à la clause GROUP BY
    ''', (fonds_id,))
    positions_aggregated = cursor.fetchall()

    # Récupérer la liste des fonds pour le menu déroulant
    cursor.execute('SELECT id, nom FROM referentiel_fonds')
    fonds_list = cursor.fetchall()

    cursor.close()
    conn.close()

     # Si le fonds existe, afficher les positions
    if fonds:  
        return render_template('positions/positions.html', positions=positions_aggregated, fonds_id=fonds_id, fonds_nom=fonds['nom'], fonds_list=fonds_list)
    else:
        return "Fonds non trouvé", 404

# Route pour récupérer la performance globale d'un fonds
@app.route('/positions/<int:fonds_id>/performance')
def performance_globale(fonds_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Calcul de la performance globale
    cursor.execute('''
        SELECT 
            SUM(p.quantite * i.valeur_unitaire_actuelle) AS valeur_actuelle_globale,
            SUM(p.quantite * p.valeur_unitaire) AS montant_total_investi,
            CASE 
                WHEN SUM(p.quantite * p.valeur_unitaire) = 0 THEN 0
                ELSE (SUM(p.quantite * i.valeur_unitaire_actuelle) - SUM(p.quantite * p.valeur_unitaire)) 
            END AS performance_globale,
            CASE 
                WHEN SUM(p.quantite * p.valeur_unitaire) = 0 THEN 0
                ELSE ((SUM(p.quantite * i.valeur_unitaire_actuelle) - SUM(p.quantite * p.valeur_unitaire)) / SUM(p.quantite * p.valeur_unitaire)) * 100
            END AS performance_globale_pourcentage
        FROM positions p
        JOIN referentiel_instruments i ON p.id_instrument = i.id
        WHERE p.id_fonds = %s;
    ''', (fonds_id,))

    performance_data = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(performance_data)

# Route pour récupérer l'historique des achats d'un fonds
@app.route('/positions/<int:fonds_id>/historique')
def historique_achat(fonds_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Récupérer l'historique des achats pour un fonds donné X
    cursor.execute('''
        SELECT p.id, i.nom AS nom_instrument, p.quantite, p.valeur_unitaire, p.date_maj
        FROM positions p
        JOIN referentiel_instruments i ON p.id_instrument = i.id
        WHERE p.id_fonds = %s
        ORDER BY p.date_maj DESC
    ''', (fonds_id,))
    historique = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(historique)


# Route pour vendre une position d'un fonds X
@app.route('/vendre_position', methods=['POST'])
def vendre_position():
    try:
        id_fonds = request.form.get('fonds_id')
        id_instrument = request.form.get('instrument_id')
        quantite = int(request.form.get('quantite'))

        print(f"id_fonds: {id_fonds}, id_instrument: {id_instrument}, quantite: {quantite}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifier la quantité d'instrument disponible dans le fonds
        cursor.execute("""
            SELECT SUM(quantite)
            FROM positions
            WHERE id_fonds = %s AND id_instrument = %s
        """, (id_fonds, id_instrument))

        quantite_disponible = cursor.fetchone()[0] or 0

        if quantite > quantite_disponible:
            return jsonify({'success': False, 'message': 'Quantité insuffisante'})

        # Récupérer la valeur actuelle de l'instrument
        cursor.execute("""
            SELECT valeur_unitaire_actuelle
            FROM referentiel_instruments
            WHERE id = %s
        """, (id_instrument,))

        valeur_unitaire_actuelle = cursor.fetchone()[0]

        # Calculer le montant de la vente
        montant_vente = quantite * valeur_unitaire_actuelle

        # Ajouter une nouvelle ligne avec quantité négative et le prix actuel
        cursor.execute("""
            INSERT INTO positions (id_fonds, id_instrument, quantite, valeur_unitaire, date_maj)
            VALUES (%s, %s, %s, %s, CURDATE())
        """, (id_fonds, id_instrument, -quantite, valeur_unitaire_actuelle))

        # Mettre à jour la table des espèces
        cursor.execute("""
            INSERT INTO especes (id_fonds, montant, date_maj)
            VALUES (%s, %s, CURDATE())
            ON DUPLICATE KEY UPDATE montant = montant + VALUES(montant), date_maj = CURDATE()
        """, (id_fonds, montant_vente))
        conn.commit()

        return jsonify({'success': True})

    except Exception as e:
        print(f"Erreur: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

# Route pour récupérer le montant des espèces disponibles
@app.route('/montant-especes/<int:fonds_id>', methods=['GET'])
def montant_espèces(fonds_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer le montant des espèces disponibles pour le fonds sélectionné
    cursor.execute("SELECT SUM(montant) FROM especes WHERE id_fonds = %s", (fonds_id,))
    montant_especes = cursor.fetchone()[0] or 0
    
    cursor.close()
    conn.close()

    return jsonify({'montant_especes': montant_especes})


# -----------------------------------------------------------------------------------------------------------------------


# Exécuter l'application Flask
if __name__ == '__main__':
    app.run(debug=False)