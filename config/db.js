const mysql = require("mysql");

const pool = mysql.createPool({
  host: "127.0.0.1",
  port: 3306,
  user: "root",
  password: "",
  database: "evp_vre_db",
  connectionLimit: 10,
  connectTimeout: 10000,
  acquireTimeout: 10000,
});

module.exports = pool;
