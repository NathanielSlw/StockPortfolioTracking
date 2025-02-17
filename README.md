# StockPortfolioTracking

Ce projet consiste en une application web permettant de suivre les portefeuilles d'investissement. L'utilisateur peut visualiser les fonds disponibles, gérer les instruments financiers (actions, ETF, matières premières, etc.), et suivre la performance de ses investissements à travers des graphiques et des tableaux. L'application intègre l'API Yahoo Finance pour récupérer les valeurs actuelles des instruments et permettre une gestion dynamique des portefeuilles. 

Lien de la vidéo qui explique le fonctionnement : 

### Installation

1. Installer le projet
```sh
git clone https://github.com/NathanielSlw/StockPortfolioTracking.git
cd StockPortfolioTracking
```

2. Installer les dépendances :
```sh
pip install -r requirements.txt
```

3. Configurer la base de données MySQL en modifiant le fichier `db_connection.py`
```python
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      
        user="USERNAME",            # A MODIFIER
        password="PASSWORD",        # A MODIFIER
        database="FinanceDB"
    )
```

4. Lancez l'application :
```sh
python app.py
```

### Fonctionnalités

#### Page **`fonds`**
- Voir tous les fonds
- Créer un fonds
- Modifier un fonds
- Supprimer un fonds
- Acheter un instrument pour un fond en sélectionnant parmi la liste des instruments, avec une récupération automatique de sa valeur unitaire grâce à l'API Yahoo Finance

#### Page **`instruments`**
- Voir tous les instruments avec :
    - Nom
    - Valeur unitaire actuelle (récupérée automatiquement via l'API Yahoo Finance)
    - Type (Action, ETF, Matières premières, Obligation, Crypto)
    - Ticker (ex : AAPL)
- Ajouter un instrument grâce à son ticker, en récupérant son prix actuel via l'API Yahoo Finance
- Rechercher un instrument par nom ou type
- Mise à jour automatique des prix de chaque instrument chaque minute

#### Page **`positions`**
- Voir la performance globale d'un fond
- Tableau récapitulatif des positions avec des statistiques :
    - Instrument
    - Quantité totale
    - Prix d'achat moyen
    - Montant investi
    - Cours actuel de l'action
    - Valeur totale actuelle
    - Performance (%)
- Vendre une position
- Exporter le tableau en CSV
- Un graphique de répartition des instruments pour le fond
- Historique des achats

### Screenshots 

![[fonds.png]]

![[instruments.png]]

![[positions.png]]

### Technologies Utilisées 
* Python avec Flask
* HTML + CSS + Bootstrap 
* JavaScript + jQuery 
* MySQL

### Fonctionnalités intéressantes à ajouter

- **Alertes de Prix** : Implémenter des notifications pour alerter l'utilisateur lorsque le prix d'un instrument atteint un certain seuil.
- **Rapports de Performance** : Générer des rapports détaillés sur la performance des fonds et des instruments sur différentes périodes (mensuelle, trimestrielle, annuelle).
- **Analyse de Risque** : Intégrer des indicateurs de risque pour chaque fonds, comme la volatilité ou le Sharp Ratio
- **Simulation d'Investissement** : Permettre aux utilisateurs de simuler des investissements hypothétiques pour voir l'impact potentiel sur leur portefeuille.
- **Intégrer d'autres API financières** : Pour obtenir + de données et des analyses supplémentaires.
- **Mode sombre**
- ....

