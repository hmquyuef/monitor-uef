const express = require('express');
const router = express.Router();
const sequelize = require('../config/database');

// Lấy tất cả cấu hình
router.get('/', async (req, res) => {
  try {
    const [results] = await sequelize.query('SELECT key, value FROM system_settings');
    const settings = {};
    results.forEach(row => settings[row.key] = row.value);
    res.json(settings);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Lưu cấu hình
router.post('/', async (req, res) => {
  try {
    const settings = req.body; // { collect_interval: '10', telegram_bot_token: '...' }
    for (const [key, value] of Object.entries(settings)) {
      await sequelize.query(
        'INSERT INTO system_settings (key, value, updated_at) VALUES (?, ?, NOW()) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()',
        { replacements: [key, value] }
      );
    }
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
