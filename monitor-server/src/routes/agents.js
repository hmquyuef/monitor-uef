const express = require('express');
const router = express.Router();
const Agent = require('../models/Agent');

router.get('/', async (req, res) => {
  try {
    const agents = await Agent.findAll();
    res.json(agents);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    await Agent.destroy({ where: { id: req.params.id } });
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
