document.addEventListener("DOMContentLoaded", () => {
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // General fade/slide in
        entry.target.classList.add("in-view");

        // Divider: trigger stroke animation
        if (entry.target.classList.contains("divider")) {
          entry.target.classList.add("animate");
        }

        obs.unobserve(entry.target); // animate once
      }
    });
  }, { threshold: 0.3 });

  // Observe contact section elements
  document.querySelectorAll(".contact-icons a, .divider, .contact-form-card")
    .forEach(el => observer.observe(el));

  // Form submit handler - AJAX submission
  const form = document.querySelector(".contact-form-card form");
  const formCard = document.querySelector(".contact-form-card");

  if (!form) {
    console.warn("Contact form not found");
    return;
  }

  console.log("Contact form found, adding event listener");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("Form submission intercepted");

    // Get form data
    const formData = new FormData(form);

    // Disable submit button and add loading state
    const submitButton = form.querySelector("button[type='submit'], input[type='submit']");
    const originalText = submitButton.textContent || submitButton.value;
    submitButton.disabled = true;
    submitButton.textContent = "Sending...";

    // Add fade-out class to form
    formCard.classList.add("form-submitting");

    try {
      console.log("Sending AJAX request to:", form.action);

      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest" // Identify as AJAX request
        }
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log("Response data:", result);

      if (result.success) {
        // Wait a moment for the fade-out effect, then replace content
        setTimeout(() => {
          // Replace the entire form card content with success message
          formCard.innerHTML = `
            <div class="success-message">
              <div>
                <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0; animation: fadeIn 0.8s ease forwards 0.3s;">✅</div>
                <h3 style="opacity: 0; animation: fadeInUp 0.8s ease forwards 0.6s;">Thank you!</h3>
                <p style="opacity: 0; animation: fadeInUp 0.8s ease forwards 0.9s;">
                  ${result.message || "Your message has been sent successfully. I'll get back to you soon!"}
                </p>
              </div>
            </div>
          `;

          // Remove the submitting class and ensure full opacity
          formCard.classList.remove("form-submitting");
          formCard.style.opacity = "1";
          formCard.style.transform = "scale(1)";
        }, 600); // Match the CSS transition duration
      } else {
        // Remove fade-out and show error
        formCard.classList.remove("form-submitting");
        showFormMessage(result.message || "Something went wrong. Please try again.", "error");
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = originalText;
      }
    } catch (error) {
      console.error("Form submission error:", error);
      // Remove fade-out and show error
      formCard.classList.remove("form-submitting");
      showFormMessage("Network error. Please check your connection and try again.", "error");
      // Re-enable submit button
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  });

  // Helper function to show messages within the form
  function showFormMessage(message, type) {
    // Remove any existing messages
    const existingMessage = form.querySelector(".form-message");
    if (existingMessage) {
      existingMessage.remove();
    }

    // Create and insert new message
    const messageDiv = document.createElement("div");
    messageDiv.className = `form-message ${type}-message`;
    messageDiv.textContent = message;
    messageDiv.style.opacity = "0";
    messageDiv.style.transform = "translateY(-10px)";

    // Insert before the submit button
    const submitButton = form.querySelector("button[type='submit'], input[type='submit']");
    form.insertBefore(messageDiv, submitButton);

    // Animate in
    requestAnimationFrame(() => {
      messageDiv.classList.add("in-view");
    });

    // Remove message after 5 seconds for errors
    if (type === "error") {
      setTimeout(() => {
        if (messageDiv.parentNode) {
          messageDiv.style.opacity = "0";
          messageDiv.style.transform = "translateY(-10px)";
          setTimeout(() => messageDiv.remove(), 300);
        }
      }, 5000);
    }
  }
});

// Add additional CSS animations via JavaScript
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.8); }
    to { opacity: 1; transform: scale(1); }
  }

  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;
document.head.appendChild(style);