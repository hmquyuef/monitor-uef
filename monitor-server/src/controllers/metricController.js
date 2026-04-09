const Metric = require('../models/Metric');
const Agent = require('../models/Agent');
const alertService = require('../services/alertService');
const telegramService = require('../services/telegramService');
const sequelize = require('../config/database');

exports.receiveMetrics = async (req, res) => {
  try {
    const { agent_name, collected_at, ...metricsData } = req.body;

    // 1. Tìm hoặc tự động đăng ký Agent
    let [agent, created] = await Agent.findOrCreate({
      where: { name: agent_name },
      defaults: { 
        api_key: req.headers.authorization?.split(' ')[1] || 'generated-key',
        status: 'online' 
      }
    });

    // 2. Cập nhật trạng thái agent
    const previousStatus = agent.status;
    await agent.update({
      status: 'online',
      last_seen: new Date()
    });

    // Thông báo nếu agent mới tạo hoặc quay trở lại online
    if (created || previousStatus === 'offline') {
      try {
        await telegramService.sendStatus('online', agent.name);
      } catch (err) {
        console.error('Failed to send Telegram notification:', err.message);
      }
    }

    // 3. Lưu metric vào DB
    const metric = await Metric.create({
      agent_id: agent.id,
      collected_at: collected_at || new Date(),
      ...metricsData
    });

    // 4. Real-time broadcast qua Socket.io
    if (global.io) {
      global.io.emit('metric:update', {
        agent_id: agent.id,
        agent_name: agent.name,
        metrics: metricsData
      });
    }

    // 5. Kiểm tra cảnh báo (Alert)
    alertService.checkMetrics(agent.id, metricsData);

    // 6. Trả về cấu hình mới cho Agent
    const [setting] = await sequelize.query('SELECT value FROM system_settings WHERE key = ?', {
        replacements: ['collect_interval']
    });
    
    const interval = setting.length > 0 ? parseInt(setting[0].value) : 10;

    res.status(201).json({ 
      success: true,
      config: {
        collect_interval: interval
      }
    });
  } catch (error) {
    console.error('Error receiving metrics:', error);
    res.status(500).json({ error: 'Failed to process metrics' });
  }
};

exports.getHistory = async (req, res) => {
  try {
    const { agentId } = req.params;
    const { range = '1d' } = req.query;

    const rangeMap = { '1d': 1, '7d': 7, '30d': 30 };
    const days = rangeMap[range] || 1;
    const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000);

    const history = await Metric.findAll({
      where: {
        agent_id: agentId,
        collected_at: { [require('sequelize').Op.gte]: since }
      },
      limit: 2000,
      order: [['collected_at', 'ASC']]
    });
    res.json(history);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch history' });
  }
};
