const loginForm = document.getElementById("createUserForm");
const loginFeedback = document.getElementById("createUserFeedback");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(loginForm);
  const data = Object.fromEntries(formData);

  try {
    const response = await fetch("/create-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      loginFeedback.textContent = "Ein Fehler ist aufgetreten";
      loginFeedback.style.display = "block";
      loginFeedback.style.color = "red";
      return;
    }

    const result = await response.json();
    loginFeedback.textContent = "Benutzer erfolgreich erstellt!";
    loginFeedback.style.display = "block";
    loginFeedback.style.color = "#28a745";
    loginForm.reset();
    console.log(result);
  } catch (err) {
    loginFeedback.textContent = "Problem mit der Verbindung";
    loginFeedback.style.display = "block";
    loginFeedback.style.color = "red";
  }
});
