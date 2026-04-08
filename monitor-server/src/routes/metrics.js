const express = require('express');
const router = express.Router();
const metricController = require('../controllers/metricController');

// Endpoint nhận metrics từ Agent
router.post('/', metricController.receiveMetrics);

// Endpoint lấy lịch sử metrics cho Dashboard
router.get('/:agentId', metricController.getHistory);

module.exports = router;
