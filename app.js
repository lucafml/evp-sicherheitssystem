const path = require("path");
const express = require("express");
const routes = require("./routes/routes.js");

const app = express();

// Setze die View-Engine auf EJS und den Views-Pfad
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Verwende die definierten Routen
app.use(routes);

// Definiere einen einfachen Endpunkt
app.get("/", (req, res) => {
  res.send("Hallo Welt!");
});

// Setze den Port, auf dem der Server lauschen soll
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server läuft auf http://localhost:${PORT}`);
});
