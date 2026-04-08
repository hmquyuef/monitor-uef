const AlertConfig = require('../models/AlertConfig');
const Alert = require('../models/Alert');
const Agent = require('../models/Agent');
const telegramService = require('./telegramService');

// In-memory cooldown (agentId_metricType: timestamp)
const cooldowns = new Map();
const COOLDOWN_MINUTES = process.env.ALERT_COOLDOWN_MINUTES || 5;

exports.checkMetrics = async (agentId, metrics) => {
  try {
    const configs = await AlertConfig.findAll({ where: { agent_id: agentId, is_active: true } });
    const agent = await Agent.findByPk(agentId);

    for (const config of configs) {
      const type = config.metric_type; // cpu, ram, disk
      const value = metrics[`${type}_percent`];

      if (value === undefined) continue;

      let severity = null;
      let threshold = null;

      if (value >= config.critical_threshold) {
        severity = 'critical';
        threshold = config.critical_threshold;
      } else if (value >= config.warning_threshold) {
        severity = 'warning';
        threshold = config.warning_threshold;
      }

      if (severity) {
        await this.handleAlert(agent, type, severity, threshold, value);
      }
    }
  } catch (error) {
    console.error('Alert check error:', error);
  }
};

exports.handleAlert = async (agent, type, severity, threshold, value) => {
  const cooldownKey = `${agent.id}_${type}_${severity}`;
  const now = Date.now();
  const lastTime = cooldowns.get(cooldownKey) || 0;

  if (now - lastTime < COOLDOWN_MINUTES * 60 * 1000) {
    return; // Đang trong thời gian chờ
  }

  // 1. Lưu alert vào DB
  const message = `[${severity.toUpperCase()}] ${agent.name}: ${type} usage is ${value}% (Threshold: ${threshold}%)`;
  await Alert.create({
    agent_id: agent.id,
    metric_type: type,
    severity,
    threshold,
    value,
    message
  });

  // 2. Cập nhật cooldown
  cooldowns.set(cooldownKey, now);

  // 3. Gửi Telegram
  telegramService.sendAlert(message);

  // 4. Emit socket
  if (global.io) {
    global.io.emit('alert:new', {
      agent_name: agent.name,
      message,
      severity
    });
  }
};
