// Fonction pour définir le jeton dans le stockage local avec une expiration de 7 jours
function setToken(token, expirationDays) {
    let date = new Date();
    date.setTime(date.getTime() + (expirationDays * 24 * 60 * 60 * 1000));
    let expires = "expires=" + date.toUTCString();
    document.cookie = "token=" + token + ";" + expires + ";path=/";
}


// Fonction pour récupérer le jeton depuis le stockage local et vérifier s'il est toujours valide
function getToken() {
    let name = "token=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let cookies = decodedCookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i];
        while (cookie.charAt(0) == ' ') {
            cookie = cookie.substring(1);
        }
        if (cookie.indexOf(name) == 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    return "";
}


function handleFormSubmit(formId, token = null, f_succses, f_error) {
    const form = document.getElementById(formId);

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const headers = new Headers();
        headers.append('Authorization', `Bearer ${token}`);
        const request = new Request(form.action, {
            method: form.method,
            body: formData,
            headers: headers
        });

        fetch(request)
        .then(response => {
            if (response.ok) {
                f_succses(response);
            } else {
                f_error(response);
            }
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
    });
}

function logout() {
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    window.location.href = "/login.html";
}

function fillHeader(pseudo, roles) {
    let link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/css/index.css';
    document.head.appendChild(link);

    let header = $('header');
    let navList = $('<ul>');

    let indexItem = $('<li>').append($('<a>').attr('href', '/user/index.html').text('Accueil'));
    navList.append(indexItem);

    if (roles.includes('admin')) {
        let adminItem = $('<li>').append($('<a>').attr('href', '/admin/index.html').text('Administration'));
        navList.append(adminItem);
    }

    if (pseudo) {
        let pseudoItem = $('<li>').append($('<a>').text(pseudo).on('click', function() {
            window.location.href = '/user/profile.html';
        }));
        navList.append(pseudoItem);
        let logoutItem = $('<li>').append($('<a>').text('Déconnexion').on('click', logout));
        navList.append(logoutItem);
    } else {
        let loginItem = $('<li>').append($('<a>').attr('href', '/login.html').text('Connexion'));
        navList.append(loginItem);
    }

    header.append(navList);
}

function buildProfilPage(pseudo){
    let token = getToken()
    const headers = new Headers();
    headers.append('Authorization', `Bearer ${token}`);
        const request = new Request(`/api/users/?pseudo===${pseudo}`, {
            method: 'GET',
            headers: headers
        });
        fetch(request)
        .then(response => {
            if (response.ok) {
                console.log(response);
            }
        })
        .then()
        .catch(error => {
            console.error('Erreur lors de l\'envoi de la requête AJAX', error);
        });
}


