const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const AlertConfig = sequelize.define('AlertConfig', {
  id: {
    type: DataTypes.BIGINT,
    autoIncrement: true,
    primaryKey: true
  },
  agent_id: {
    type: DataTypes.UUID,
    allowNull: false
  },
  metric_type: {
    type: DataTypes.STRING, // cpu, ram, disk
    allowNull: false
  },
  warning_threshold: DataTypes.NUMERIC(5, 2),
  critical_threshold: DataTypes.NUMERIC(5, 2),
  is_active: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  }
}, {
  tableName: 'alert_configs',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: 'updated_at'
});

module.exports = AlertConfig;
