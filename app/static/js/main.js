console.log("TEST: js/main.js is linked.");

/* ---- Alert Fade Out ---- */
document.addEventListener("DOMContentLoaded", () => {
    // Find all success and info alert messages on the page
    const flashMessages = document.querySelectorAll(
        ".alert-success, .alert-info" // Danger/error are excluded so they stay visible
    );

    flashMessages.forEach((message) => {
        setTimeout(() => {
            message.classList.add("fade-out"); // Transition to the 0 opacity version

            message.addEventListener("transitionend", () => {
                message.remove();
            });
        }, 4000); // Wait 4 seconds before fading out
    });
});

