const express = require("express");
const router = express.Router();
const pool = require("../config/db.js");
const util = require('util');
const axios = require('axios');
const bcrypt = require('bcrypt');
const queryAsync = util.promisify(pool.query).bind(pool);

function checkLogin(req, res, next) {
  if (!req.session.isLoggedIn) {
    return res.redirect("/login");
  }
  next();
}

async function getSystemState() {
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/system-state');
    return response.data.state === 'aktiviert';
  } catch (error) {
    return false;
  }
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

    if (result.length > 0 && bcrypt.compareSync(password, result[0].password)) {
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

router.get("/create-user", checkLogin, async (req, res) => {
  try {
    const sys_state = await getSystemState();
    res.render("create-user", { 
      page: "create-user",
      sys_state 
    });
  } catch(err) {
    console.error(err);
    res.status(500).send("Ein Fehler ist aufgetreten");
  }
});

router.post("/create-user", checkLogin, async (req, res) => {
  const { username, password } = req.body;
  const query = "INSERT INTO users (username, password) VALUES (?, ?)";
  const hashedPassword = await bcrypt.hash(password, 10);
  pool.query(query, [username, hashedPassword], function (err, result) {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Interner Serverfehler." });
    }
    return res.json({ success: true, message: "Benutzer erfolgreich erstellt." });
  });
});

router.get("/dashboard", checkLogin, async (req, res) => {
  try {
    const sys_state = await getSystemState();
    
    const queries = [
      'SELECT username, event_type, timestamp FROM security_state_changes ORDER BY timestamp DESC LIMIT 5',
      'SELECT status, timestamp FROM bewegungen ORDER BY timestamp DESC LIMIT 5',
      'SELECT status, timestamp FROM lichtschranke ORDER BY timestamp DESC LIMIT 5'
    ];

    const [stateChanges, bewegungen, lichtschranke] = await Promise.all(
      queries.map(query => queryAsync(query))
    );

    res.render("dashboard", {
      page: "dashboard",
      stateChanges,
      bewegungen,
      lichtschranke,
      sys_state
    });
  } catch(error) {
    console.error('Fehler beim Abrufen der Daten:', error);
    res.status(500).send('Interner Serverfehler');
  }
});

router.get("/dashboard/state-changes", checkLogin, async (req, res) => {
  try {
    const sys_state = await getSystemState();
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 30;
    const offset = (page - 1) * limit;
    
    let query = "SELECT * FROM security_state_changes WHERE 1=1";
    let countQuery = "SELECT COUNT(*) as total FROM security_state_changes WHERE 1=1";
    const params = [];
    
    if (req.query.username) {
      query += " AND username LIKE ?";
      countQuery += " AND username LIKE ?";
      params.push(`%${req.query.username}%`);
    }
    
    if (req.query.eventType && req.query.eventType !== 'all') {
      query += " AND event_type = ?";
      countQuery += " AND event_type = ?";
      params.push(req.query.eventType);
    }
    
    if (req.query.date) {
      query += " AND DATE(timestamp) = ?";
      countQuery += " AND DATE(timestamp) = ?";
      params.push(req.query.date);
    }
    
    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?";
    const queryParams = [...params, limit, offset];
    
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
      page: "state-changes",
      sys_state
    });
  } catch(err) {
    console.error(err);
    res.status(500).send("Ein Fehler ist aufgetreten. Bitte versuche es später erneut oder wende dich an einen Systemadministrator");
  }
});

router.get("/dashboard/lichtschranke", checkLogin, async (req, res) => {
  try {
    const sys_state = await getSystemState();
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 30;
    const offset = (page - 1) * limit;
    
    // Basis-Query erstellen
    let query = "SELECT * FROM lichtschranke WHERE 1=1";
    let countQuery = "SELECT COUNT(*) as total FROM lichtschranke WHERE 1=1";
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
    
    res.render("lichtschranke", {
      entries: entries,
      currentPage: page,
      totalPages: totalPages,
      limit: limit,
      query: req.query,
      sys_state
    });
  } catch(err) {
    console.error(err);
    res.status(500).send("Ein Fehler ist aufgetreten. Bitte versuche es später erneut oder wende dich an einen Systemadministrator");
  }
});

router.get("/dashboard/bewegungssensor", checkLogin, async (req, res) => {
  try {
    const sys_state = await getSystemState();
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 30;
    const offset = (page - 1) * limit;
    
    // Basis-Query erstellen
    let query = "SELECT * FROM bewegungen WHERE 1=1";
    let countQuery = "SELECT COUNT(*) as total FROM bewegungen WHERE 1=1";
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
    
    res.render("bewegungssensor", {
      entries: entries,
      currentPage: page,
      totalPages: totalPages,
      limit: limit,
      query: req.query,
      sys_state
    });
  } catch(err) {
    console.error(err);
    res.status(500).send("Ein Fehler ist aufgetreten. Bitte versuche es später erneut oder wende dich an einen Systemadministrator");
  }
});


module.exports = router;
