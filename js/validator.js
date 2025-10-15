function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

function validateRequired(value) {
    return value.trim() !== '';
}

function validateAge(age) {
    return Number.isInteger(age) && age >= 0 && age <= 120;
}

function validateForm(formData) {
    const errors = {};

    if (!validateRequired(formData.name)) {
        errors.name = 'Name is required';
    }

    if (!validateEmail(formData.email)) {
        errors.email = 'Email is invalid';
    }

    if (!validateAge(formData.age)) {
        errors.age = 'Age must be a valid number between 0 and 120';
    }

    return errors;
}

// Export the validation functions for use in other modules
export { validateEmail, validateRequired, validateAge, validateForm };