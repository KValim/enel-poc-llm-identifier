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
            <h2>Project Summary</h2>
            <p><strong>Evaluated Structures: ${summary.total_avaliadas}/${summary.total_estruturas}</strong></p>
            <p>Total Valid Structures: ${summary.total_validas}</p>
            <p>Total Invalid Structures: ${summary.total_invalidas}</p>
            <p>Total Unvalidated Structures: ${summary.total_nao_validadas}</p>
            <form id="validate-project-form" method="post" action="/validate_project">
                <input type="hidden" name="project" id="selected-project" value="">
                <button type="button" class="btn btn-success mt-3" onclick="validateProject()">Validate Project</button>
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
        alert("Please select a project first.");
        return;
    }

    $.post('/check_validation_status', { project: selectedProject }, function(data) {
        var result = JSON.parse(data);
        if (result.has_unvalidated_structures) {
            var confirmValidation = confirm("There are unvalidated structures. Are you sure you want to validate the project?");
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
        alert("Geolocation is not supported by this browser.");
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
            alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
}

// Code for upload_photo.html

/**
 * Previews the selected image file.
 */
function previewImage() {
    var file = document.getElementById("file-input").files;
    if (file.length > 0) {
        var fileReader = new FileReader();

        fileReader.onload = function(event) {
            document.getElementById("image-preview").setAttribute("src", event.target.result);
            document.getElementById("image-preview").style.display = "block";
        };

        fileReader.readAsDataURL(file[0]);
    }
}

/**
 * Shows the loading spinner overlay.
 */
function showLoadingSpinner() {
    document.getElementById('loading-overlay').style.display = 'flex';
}
