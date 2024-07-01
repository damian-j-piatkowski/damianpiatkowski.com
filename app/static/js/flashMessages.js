/* Handles the display and removal of flash messages on the website. */

document.addEventListener('DOMContentLoaded', function () {
    var flashMessage = document.querySelector('.flash-message');
    if (flashMessage) {
        // Show the flash message immediately
        flashMessage.classList.add('show');

        // Schedule the removal of the flash message after a delay
        setTimeout(function() {
            // Start fading out the flash message
            flashMessage.classList.remove('show');

            // Remove the flash message from the DOM after the fade-out transition
            setTimeout(function() {
                flashMessage.remove();
            }, 2000); // Wait for the fade-out transition (2 seconds)
        }, 2000); // Flash message fade-out starts after 2 seconds of fade-in
    }
});