function MakeTable(data_json, div_id){
    let columns = Object.keys(data_json[0]);

    // Créer la table
    let table = $('<table>').addClass('table');
    let thead = $('<thead>');
    let tbody = $('<tbody>');

    // Ajouter les en-têtes de colonnes au thead
    let headerRow = $('<tr>');
    $.each(columns, function(index, column) {
        headerRow.append($('<th>').text(column));
    });
    thead.append(headerRow);

    // Parcourir chaque objet JSON et ajouter une ligne de tableau à tbody pour chaque objet
    $.each(data_json, function(index, item) {
        let row = $('<tr>');
        $.each(columns, function(index, column) {
            row.append($('<td>').text(item[column]));
        });
        tbody.append(row);
    });

    // Ajouter le thead et tbody à la table
    table.append(thead, tbody);

    // Ajouter la table à l'élément div spécifié
    $(`#${div_id}`).append(table);
}
function handleFormSubmit(formId, token = null, f_succses, f_error) {
    // Sélectionner le formulaire
    const form = document.getElementById(formId);

    // Écouter l'événement submit
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Empêcher le comportement par défaut de soumission du formulaire
        
        const form = event.target; // Récupérer le formulaire soumis
        const formData = new FormData(form); // Créer un objet FormData pour les données du formulaire

        // Créer un objet d'en-tête
        const headers = new Headers();
        // Ajouter l'en-tête d'authentification avec la valeur souhaitée
        headers.append('Authorization', `Bearer ${token}`);

        // Créer l'objet de requête avec l'URL, la méthode, les données du formulaire et les en-têtes
        const request = new Request(form.action, {
            method: form.method,
            body: formData,
            headers: headers
        });

        // Envoyer la requête AJAX
        fetch(request)
        .then(response => {
            if (response.ok) {
                // Traiter la réponse si elle est réussie
                f_succses(response);
            } else {
                // Traiter les erreurs si la réponse est un échec
                f_error(response);
            }
        })
        .catch(error => {
            // Traiter les erreurs de réseau ou autres erreurs
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
    });
}

$('body').ready(function(){
    // Définir les trois requêtes AJAX
    let request_streamer = $.ajax({
        url: '../api/streamers',
        method: 'GET'
    });

    let request_role = $.ajax({
        url: '../api/roles',
        method: 'GET'
    });

    let request_user = $.ajax({
        url: '../api/users',
        method: 'GET'
    });

    // Envoyer les trois requêtes simultanément
    Promise.all([request_streamer, request_role, request_user])
        .then(function(responses) {
            // Traitement des réponses
            let response_streamer = responses[0].streamers;
            let response_role = responses[1].roles;
            let response_user = responses[2].users;
            
            MakeTable(response_streamer, 'info_streamer');
            MakeTable(response_role, 'info_role');
            MakeTable(response_user, 'info_user');
            $.each(response_role, function(index, role) {
                $('#role_name').append($('<option>', {
                    value: role.role_id,
                    text: role.name
                }));
            });
            $.each(response_user, function(index, user) {
                $('#pseudo_user_list').append($('<option>', {
                    value: user.user_id,
                    text: user.pseudo
                }));
            });
        })
        .catch(function(error) {
            // Gestion des erreurs
            console.error('Error:', error);
    });
    handleFormSubmit('streamerForm',null,async response=>console.log(await response.json()),async response=>console.log(await response.json()));
    handleFormSubmit('userForm',null,async response=>console.log(await response.json()),async response=>console.log(await response.json()));
    handleFormSubmit('roleForm',null,async response=>console.log(await response.json()),async response=>console.log(await response.json()));

})