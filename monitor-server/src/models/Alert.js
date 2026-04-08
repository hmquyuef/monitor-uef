const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Alert = sequelize.define('Alert', {
  id: {
    type: DataTypes.BIGINT,
    autoIncrement: true,
    primaryKey: true
  },
  agent_id: {
    type: DataTypes.UUID,
    allowNull: false
  },
  metric_type: DataTypes.STRING,
  severity: DataTypes.STRING, // warning, critical
  threshold: DataTypes.NUMERIC(5, 2),
  value: DataTypes.NUMERIC(5, 2),
  message: DataTypes.TEXT,
  is_resolved: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  }
}, {
  tableName: 'alerts',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: false
});

module.exports = Alert;
