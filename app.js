const path = require("path");
const express = require("express");
const routes = require("./routes/routes.js");
const session = require("express-session");
const auth = require("./config/auth.js");

const app = express();

// Session-Konfiguration
const sessionConfig = {
  secret: "secret-key", // Dein geheimer Schlüssel
  resave: false, // Verhindert unnötige Session-Aktualisierungen
  saveUninitialized: false, // Speichert nicht initialisierte Sitzungen
  cookie: { secure: false }, // `secure: true` nur verwenden, wenn du HTTPS verwendest
};

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(
  "/assets",
  express.static(path.join(__dirname, "public"), {
    maxAge: "1d",
  })
);

// Setze die View-Engine auf EJS und den Views-Pfad
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Verwende die Session-Middleware
app.use(session(sessionConfig));

// Verwende die Authentifizierungs-Middleware
app.use(auth);

// Verwende die definierten Routen
app.use(routes);

// Setze den Port, auf dem der Server lauschen soll
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server läuft auf http://localhost:${PORT}`);
});
