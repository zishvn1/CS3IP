// wait until the entire page is fully loaded
document.addEventListener('DOMContentLoaded', function() {

    // get references to the dropdown elements
    const makeSelect = document.getElementById('id_make');     // dropdown for car make
    const modelSelect = document.getElementById('id_model');   // dropdown for car model
    const variantSelect = document.getElementById('id_variant'); // dropdown for car variant

    // when user selects a different make
    makeSelect.addEventListener('change', function() {
        const make = makeSelect.value;  // get the selected make

        // fetch the models related to that make
        fetch(`/get_models/?make=${make}`)
            .then(response => response.json())  // convert server response to JSON
            .then(data => {
                // reset the model dropdown to only show default option
                modelSelect.innerHTML = '<option value="">---------</option>';

                // for each model received, add it as a new dropdown option
                data.models.forEach(model => {
                    modelSelect.innerHTML += `<option value="${model}">${model}</option>`;
                });

                // also reset the variant dropdown because the model has changed
                variantSelect.innerHTML = '<option value="">---------</option>';
            });
    });

    // when user selects a different model
    modelSelect.addEventListener('change', function() {
        const make = makeSelect.value;    // get selected make again
        const model = modelSelect.value;  // get selected model

        // fetch the variants related to the selected make and model
        fetch(`/get_variants/?make=${make}&model=${model}`)
            .then(response => response.json())  // convert server response to JSON
            .then(data => {
                // reset the variant dropdown to only show default option
                variantSelect.innerHTML = '<option value="">---------</option>';

                // for each variant received, add it as a new dropdown option
                data.variants.forEach(variant => {
                    variantSelect.innerHTML += `<option value="${variant}">${variant}</option>`;
                });
            });
    });
});
