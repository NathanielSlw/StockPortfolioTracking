// Script gérant l'affichage de la valeur unitaire d'un instrument
// lors de la sélection dans le formulaire d'achat d'un instrument pour un fonds.


// Met à jour le champ de la valeur unitaire en fonction de l'instrument sélectionné
function afficherValeurUnitaire() {
    const select = document.getElementById('instrument_id');
    const valeurUnitaireField = document.getElementById('valeur_unitaire_actuelle');

    // Récupère la valeur unitaire de l'option sélectionnée et l'affiche
    const valeurUnitaire = select.options[select.selectedIndex].getAttribute('data-valeur');
    valeurUnitaireField.value = valeurUnitaire ? `${valeurUnitaire} €` : '';
}


document.addEventListener("DOMContentLoaded", function () {
    // Met à jour la valeur unitaire lors de l'ouverture du modal d'ajout d'instrument
    const ajouterInstrumentModal = document.getElementById('ajouterInstrumentModal');
    if (ajouterInstrumentModal) {
        ajouterInstrumentModal.addEventListener('shown.bs.modal', afficherValeurUnitaire);
    }

    // Sélectionne automatiquement le fonds correspondant lorsqu'on clique sur "Acheter un Instrument"
    const acheterInstrumentBtns = document.querySelectorAll("[data-bs-target='#ajouterInstrumentModal']");
    const fondsSelect = document.getElementById("fonds_id");

    acheterInstrumentBtns.forEach(button => {
        button.addEventListener("click", function () {
            const fondsId = this.getAttribute("data-fonds-id");
            if (fondsSelect) {
                fondsSelect.value = fondsId;
            }
        });
    });
});