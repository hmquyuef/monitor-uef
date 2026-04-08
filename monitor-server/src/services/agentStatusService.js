const { Op } = require('sequelize');
const Agent = require('../models/Agent');
const telegramService = require('./telegramService');

/**
 * Service kiểm tra trạng thái Online/Offline của các Agent
 */
exports.init = () => {
    // Kiểm tra mỗi 30 giây
    setInterval(async () => {
        try {
            // Ngưỡng offline: không thấy gửi dữ liệu trong 1 phút (60 giây)
            const timeoutDate = new Date(Date.now() - 60 * 1000);

            // Tìm các agent đang Online nhưng đã lâu không gửi data
            const agentsToOffline = await Agent.findAll({
                where: {
                    status: 'online',
                    last_seen: {
                        [Op.lt]: timeoutDate
                    }
                }
            });

            for (const agent of agentsToOffline) {
                await agent.update({ status: 'offline' });
                
                // Gửi thông báo Telegram
                telegramService.sendStatus('offline', agent.name);
                
                // Thông báo qua Socket
                if (global.io) {
                    global.io.emit('agent:status', {
                        agent_id: agent.id,
                        status: 'offline'
                    });
                }
                
                console.log(`Agent [${agent.name}] marked as offline`);
            }
        } catch (error) {
            console.error('Agent status check error:', error);
        }
    }, 30000);
};
