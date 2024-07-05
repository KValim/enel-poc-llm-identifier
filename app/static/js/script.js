// Code for home.html

/**
 * Opens a PDF in a new tab based on the selected project.
 */
function openPDF() {
    var selectedProject = document.getElementById('project').value;
    var url = '/open_pdf?file=' + encodeURIComponent(selectedProject + '.pdf');
    window.open(url, '_blank');
}

/**
 * Shows the summary of the selected project by making an AJAX request.
 * @param {string} project - The selected project name.
 */
function showSummary(project) {
    $.post('/project_summary', { project: project }, function(data) {
        var summary = JSON.parse(data);
        document.getElementById('project-summary').innerHTML = `
            <h2>Resumo do Projeto</h2>
            <p><strong>Estruturas Avaliadas: ${summary.total_avaliadas}/${summary.total_estruturas}</strong></p>
            <p>Total de Estruturas Válidadas: ${summary.total_validas}</p>
            <p>Total de Estruturas Com Divergênca: ${summary.total_invalidas}</p>
            <!-- <p>Total de Estruturas Não Avalidadas: ${summary.total_nao_validadas}</p>
            <p>Total de Estruturas Extras Encontradas: ${summary.total_extras}</p> -->
            <form id="validate-project-form" method="post" action="/validate_project">
                <input type="hidden" name="project" id="selected-project" value="">
                <button type="button" class="btn btn-success mt-3" onclick="validateProject()">Validar Projeto</button>
            </form>
        `;
    });
}

/**
 * Validates the selected project after checking for unvalidated structures.
 */
function validateProject() {
    var selectedProject = document.getElementById('project').value;
    if (!selectedProject) {
        alert("Por favor, selecione um projeto primeiro.");
        return;
    }

    $.post('/check_validation_status', { project: selectedProject }, function(data) {
        var result = JSON.parse(data);
        if (result.has_unvalidated_structures) {
            var confirmValidation = confirm("Existem estruturas não validadas.\nTem certeza que deseja validar o projeto?");
            if (confirmValidation) {
                $('#validate-project-form').submit();
            }
        } else {
            $('#validate-project-form').submit();
        }
    });
}

$(document).ready(function() {
    $('#project').change(function() {
        var selectedProject = $(this).val();
        if (selectedProject) {
            $('#select-structure-btn').prop('disabled', false);
            $('#open-pdf-btn').prop('disabled', false);
            showSummary(selectedProject);
        } else {
            $('#select-structure-btn').prop('disabled', true);
            $('#open-pdf-btn').prop('disabled', true);
            document.getElementById('project-summary').innerHTML = '';
        }
    });
    $('#project').trigger('change');
});

// Code for results.html

/**
 * Toggles the display of details for a specific item.
 * @param {string} id - The ID of the item.
 */
function toggleDetails(id) {
    var details = document.getElementById("details-" + id);
    var arrow = document.getElementById("arrow-" + id);
    if (details.style.display === "none") {
        details.style.display = "block";
        if (arrow) {
            arrow.classList.add("arrow-down");
        }
    } else {
        details.style.display = "none";
        if (arrow) {
            arrow.classList.remove("arrow-down");
        }
    }
}

// Code for select_structure.html

/**
 * Gets the user's current location using the Geolocation API.
 */
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocalização não é suportada por este navegador.");
    }
}

/**
 * Shows the user's position by setting the latitude and longitude inputs and submitting the form.
 * @param {Position} position - The position object returned by the Geolocation API.
 */
function showPosition(position) {
    document.getElementById("latitude").value = position.coords.latitude;
    document.getElementById("longitude").value = position.coords.longitude;
    document.getElementById("get-location-form").submit();
}

/**
 * Shows an error message based on the Geolocation API error code.
 * @param {PositionError} error - The error object returned by the Geolocation API.
 */
function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("Usuário negou o pedido para Geolocalização.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Informação de localização não disponível.");
            break;
        case error.TIMEOUT:
            alert("O pedido para obter a localização do usuário expirou.");
            break;
        case error.UNKNOWN_ERROR:
            alert("Ocorreu um erro desconhecido.");
            break;
    }
}

// Code for upload_photo.html

/**
 * Previews the selected image file.
 */
function previewImage() {
    const fileInput = document.getElementById('file-input');
    const preview = document.getElementById('image-preview');
    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.addEventListener('load', function() {
        preview.src = reader.result;
    }, false);

    if (file) {
        reader.readAsDataURL(file);
    }
}

/**
 * Shows the loading spinner overlay.
 */
function showLoadingSpinner() {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'flex';
}
