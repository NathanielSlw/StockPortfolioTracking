// Script de gestion de la page des positions : 
// - Affichage des performances
// - Historique d'achats
// - Graphique, 
// - Export CSV du tableau
// - Vente de parts


document.addEventListener("DOMContentLoaded", function() {
    // Formater les prix dans le tableau
    formatTablePrices();

    // Initialiser la performance lors de la sélection du fonds dans le dropdown
    const fondsSelect = document.getElementById("fondsSelect");
    if (fondsSelect) {
        chargerPerformance(fondsSelect.value);
        chargerHistoriqueAchat(fondsSelect.value)
        getMontantEspeces(fondsSelect.value);

        // Gérer du changement de fonds
        fondsSelect.addEventListener("change", function() {
            if (this.value) {
                window.location.href = "/positions/" + this.value;
            }
        });
        
    }

    // Initialiser le graphique
    if (typeof positionsData !== 'undefined') {
        createChart(positionsData);
    } else {
        console.error("Positions data not found");
    }

    // Initialiser la modale de vente
    var vendreModal = document.getElementById('vendreModal');
    vendreModal.addEventListener('show.bs.modal', function(event) {
        var button = event.relatedTarget;
        var instrumentId = button.getAttribute('data-instrument-id');
        var quantiteMax = button.getAttribute('data-quantite-max');

        var modal = vendreModal;
        modal.querySelector('#instrumentId').value = instrumentId;
        modal.querySelector('#quantiteVente').max = quantiteMax;
    });

});

// Fonction de formatage des prix
function formatPrice(price) {
    if (price === undefined || price === null) {
        console.error("Price is undefined or null");
        return "0,00 €";
    }
    return price.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " €";
}

// Formater tous les prix dans le tableau
function formatTablePrices() {
    document.querySelectorAll('.price-value').forEach(element => {
        const value = parseFloat(element.dataset.value);
        element.textContent = formatPrice(value);
    });
}

// Fonction pour charger la performance du fonds
function chargerPerformance(fondsId) {
    fetch(`/positions/${fondsId}/performance`)
        .then(response => response.json())
        .then(data => {
            let valeurActuelle = parseFloat(data.valeur_actuelle_globale || 0);
            let performanceGlobale = parseFloat(data.performance_globale || 0);
            let performanceGlobalePourcentage = parseFloat(data.performance_globale_pourcentage || 0);
            let montantTotalInvesti = parseFloat(data.montant_total_investi || 0);

            // Mise à jour des valeurs affichées
            document.getElementById("valeur-actuelle").textContent = formatPrice(valeurActuelle);
            document.getElementById("montant-total-investi").textContent = formatPrice(montantTotalInvesti);
            document.getElementById("performance-globale").textContent = formatPrice(performanceGlobale);
            document.getElementById("performance-globale-pourcentage").textContent = performanceGlobalePourcentage.toFixed(2) + " %";

            // Appliquer couleur rouge/vert en fonction de la performance
            document.getElementById("performance-globale").className = performanceGlobale >= 0 ? "text-success" : "text-danger";
            document.getElementById("performance-globale-pourcentage").className = performanceGlobalePourcentage >= 0 ? "text-success" : "text-danger";
        })
        .catch(error => console.error("Erreur lors du chargement de la performance :", error));
}

// Fonction pour créer le graphique de répartition des positions
function createChart(positions) {
    const ctx = document.getElementById('repartitionGraph');
    if (!ctx) {
        return;
    }

    const labels = positions.map(position => position.nom_instrument);
    const data = positions.map(position => position.prix_reel);

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Répartition des Positions',
                data: data,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                    '#FF9F40', '#FF5733', '#33FF57'
                ],
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                    display: true
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            return `${context.label}: ${formatPrice(value)}`;
                        }
                    }
                }
            }
        }
    });
}

// Fonction pour charger l'historique des achats du fonds
function chargerHistoriqueAchat(fondsId) {
    fetch(`/positions/${fondsId}/historique`)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#historique-table tbody');
            tableBody.innerHTML = '';
            data.forEach(achat => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${achat.nom_instrument}</td>
                    <td>${achat.quantite}</td>
                    <td>${parseFloat(achat.valeur_unitaire).toFixed(2)} €</td>
                    <td>${new Date(achat.date_maj).toLocaleDateString()}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error("Erreur lors du chargement de l'historique d'achat :", error));
}


// Fonction pour récupérer le montant des espèces disponibles
function getMontantEspeces(fondsId) {
    fetch(`/montant-especes/${fondsId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('montant-especes').textContent = data.montant_especes + " €";
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
}



// Fonction pour vendre des parts
function vendreParts() {
    const formData = new FormData(document.getElementById('venteForm'));

    // Log des données envoyées
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }

    fetch('/vendre_position', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert('Erreur lors de la vente: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Une erreur est survenue lors de la vente');
    });
}

// Exportation des positions en CSV
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('exportCSV').addEventListener('click', function () {
        // Cibler uniquement le tableau des positions (table.table-bordered)
        const table = document.querySelector('table.table-bordered');
        if (!table) return; 

        // Récupérer les données du tableau
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const csvData = [];
        
        // Ajouter les en-têtes (exclure la colonne "Actions")
        const headers = Array.from(table.querySelectorAll('thead th'))
            .filter((th, index) => index !== 7)  // Exclure la colonne "Actions" (index 7)
            .map(th => th.textContent.trim());
        csvData.push(headers);

        // Ajouter les lignes du tableau
        rows.forEach(row => {
            const rowData = Array.from(row.querySelectorAll('td'))
                .filter((td, index) => index !== 7)  // Exclure la colonne "Actions" (index 7)
                .map(td => td.textContent.trim());
            csvData.push(rowData);
        });

        // Convertir les données en CSV
        const csvContent = csvData.map(row => row.join(',')).join('\n');

        // Créer un fichier CSV à télécharger
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'positions.csv');
        link.click();
    });
});
