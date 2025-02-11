const express = require("express");
const router = express.Router();
const pool = require("../config/db.js");
const util = require('util');

const queryAsync = util.promisify(pool.query).bind(pool);

function checkLogin(req, res, next) {
  if (!req.session.isLoggedIn) {
    return res.redirect("/login");
  }
  next();
}

router.get("/", checkLogin, (req, res) => {
  res.redirect("/dashboard");
});

router.get("/login", (req, res) => {
  if (req.session.isLoggedIn) {
    return res.redirect("/dashboard");
  }
  res.render("login");
});

router.post("/login", (req, res) => {
  const { username, password } = req.body;
  const query = "Select * from users where username = ?";

  pool.query(query, [username], async function (err, result) {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Interner Serverfehler." });
    }

    if (result.length > 0 && result[0].password == password) {
      req.session.isLoggedIn = true;
      return res.json({ success: true, redirectUrl: "/dashboard" });
    } else {
      return res.status(401).json({ error: "Ungültige Anmeldedaten." });
    }
  });
});

router.post("/logout", (req, res) => {
  req.session.isLoggedIn = false;
  res.redirect("/login");
})

router.get("/create-user", checkLogin, (req, res) => {
  res.render("create-user", { page: "create-user" });
});

router.post("/create-user", checkLogin, (req, res) => {
  const { username, password } = req.body;
  const query = "INSERT INTO users (username, password) VALUES (?, ?)";
  pool.query(query, [username, password], function (err, result) {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Interner Serverfehler." });
    }
    return res.json({ success: true, message: "Benutzer erfolgreich erstellt." });
  });
});

router.get("/dashboard/state-changes", checkLogin, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 30;
    const offset = (page - 1) * limit;
    
    // Basis-Query erstellen
    let query = "SELECT * FROM security_state_changes WHERE 1=1";
    let countQuery = "SELECT COUNT(*) as total FROM security_state_changes WHERE 1=1";
    const params = [];
    
    // Filter hinzufügen
    if (req.query.username) {
      query += " AND username LIKE ?";
      countQuery += " AND username LIKE ?";
      params.push(`%${req.query.username}%`);
    }
    
    if (req.query.eventType) {
      query += " AND event_type = ?";
      countQuery += " AND event_type = ?";
      params.push(req.query.eventType);
    }
    
    if (req.query.date) {
      query += " AND DATE(timestamp) = ?";
      countQuery += " AND DATE(timestamp) = ?";
      params.push(req.query.date);
    }
    
    // Sortierung und Limit hinzufügen
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?";
    const queryParams = [...params, limit, offset];
    
    // Queries ausführen
    const [entries, countResult] = await Promise.all([
      queryAsync(query, queryParams),
      queryAsync(countQuery, params)
    ]);
    
    const total = countResult[0].total;
    let totalPages = Math.ceil(total / limit);
    if(totalPages == 0) {
      totalPages = 1;
    }
    
    res.render("state_changes", {
      entries: entries,
      currentPage: page,
      totalPages: totalPages,
      limit: limit,
      query: req.query,
      page: "state-changes"
    });
  } catch(err) {
    console.error(err);
    res.status(500).send("Ein Fehler ist aufgetreten. Bitte versuche es später erneut oder wende dich an einen Systemadministrator");
  }
});

router.get("/dashboard", checkLogin, (req, res) => {
  res.render("dashboard", { page: "dashboard" });
});

module.exports = router;
