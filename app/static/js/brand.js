document.addEventListener("DOMContentLoaded", () => {
  const brand = document.getElementById("brand");
  if (!brand) return;

  const text = brand.textContent;
  brand.textContent = ""; // clear original

  [...text].forEach((char, i) => {
    const span = document.createElement("span");
    span.textContent = char;
    span.style.animationDelay = `${i * 0.1}s`; // assign delay per letter
    brand.appendChild(span);
  });
});
