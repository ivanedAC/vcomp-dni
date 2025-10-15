// This file contains the logic for the form, including features like autocompletion and form submission handling.

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('myForm');
    const inputField = document.getElementById('inputField');
    const suggestionsList = document.getElementById('suggestionsList');

    // Sample data for autocompletion
    const sampleData = ['Option 1', 'Option 2', 'Option 3'];

    // Autocomplete functionality
    inputField.addEventListener('input', function() {
        const inputValue = this.value.toLowerCase();
        suggestionsList.innerHTML = '';

        if (inputValue) {
            const filteredData = sampleData.filter(item => item.toLowerCase().includes(inputValue));
            filteredData.forEach(item => {
                const suggestionItem = document.createElement('li');
                suggestionItem.textContent = item;
                suggestionItem.addEventListener('click', function() {
                    inputField.value = item;
                    suggestionsList.innerHTML = '';
                });
                suggestionsList.appendChild(suggestionItem);
            });
        }
    });

    // Form submission handling
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        // Process form data here (e.g., send to server)
        console.log('Form submitted:', Object.fromEntries(formData.entries()));
        alert('Form submitted successfully!');
        form.reset();
        suggestionsList.innerHTML = '';
    });
});