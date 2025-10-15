// ocr.js - Processes OCR (Optical Character Recognition) and extracts data from images

// Load the Tesseract.js library
const Tesseract = require('../libs/tesseract.min.js');

// Function to perform OCR on a given image
function performOCR(image) {
    return new Promise((resolve, reject) => {
        Tesseract.recognize(
            image,
            'eng', // Language
            {
                logger: info => console.log(info) // Log progress
            }
        ).then(({ data: { text } }) => {
            resolve(text); // Resolve with the recognized text
        }).catch(err => {
            reject(err); // Reject on error
        });
    });
}

// Export the performOCR function for use in other modules
export { performOCR };