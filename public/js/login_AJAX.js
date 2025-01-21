const loginForm = document.getElementById("loginForm");
const loginFeedback = document.getElementById("loginFeedback");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(loginForm);
  const data = Object.fromEntries(formData);

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      loginFeedback.textContent =
        errorData.error || "Ein Fehler ist aufgetreten";
      loginFeedback.style.display = "block";
      return;
    }

    const result = await response.json();
    console.log(result);
    if (result.success && result.redirectUrl) {
      window.location.href = result.redirectUrl;
    }
  } catch (err) {
    loginFeedback.textContent = "Problem mit der Verbindung";
    loginFeedback.style.display = "block";
  }
});
