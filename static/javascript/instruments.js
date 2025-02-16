// Script gérant la recherche et la réinitialisation des instruments affichés dans le tableau.

document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resetButton = document.getElementById('reset-button');
    const tableBody = document.querySelector('#instruments-table tbody');

    // Permet de lancer la recherche en appuyant sur Entrée dans le champ de recherche
    searchInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            searchButton.click();
        }
    });

    // Effectue une recherche d'instruments et met à jour le tableau
    searchButton.addEventListener('click', function() {
        const searchTerm = searchInput.value;
        fetch(`/search_instruments?search=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                tableBody.innerHTML = '';
                data.instruments.forEach(instrument => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${instrument.id}</td>
                        <td>${instrument.nom}</td>
                        <td>${instrument.valeur_unitaire_actuelle}</td>
                        <td>${instrument.type_instrument}</td>
                        <td>${instrument.code_ISIN}</td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => console.error("Erreur lors de la recherche des instruments :", error));
    });

    // Réinitialise la recherche et recharge la liste complète des instruments
    resetButton.addEventListener('click', function() {
        searchInput.value = '';
        fetch('/instruments')
            .then(response => response.text())
            .then(data => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(data, 'text/html');
                tableBody.innerHTML = doc.querySelector('#instruments-table tbody').innerHTML;
            })
            .catch(error => console.error("Erreur lors du rechargement des instruments :", error));
    });
});