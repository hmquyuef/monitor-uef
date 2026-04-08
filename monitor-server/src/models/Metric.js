const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Metric = sequelize.define('Metric', {
  id: {
    type: DataTypes.BIGINT,
    autoIncrement: true,
    primaryKey: true
  },
  agent_id: {
    type: DataTypes.UUID,
    allowNull: false
  },
  collected_at: {
    type: DataTypes.DATE,
    allowNull: false
  },
  cpu_percent: DataTypes.NUMERIC(5, 2),
  ram_percent: DataTypes.NUMERIC(5, 2),
  disk_percent: DataTypes.NUMERIC(5, 2),
  extra_data: {
    type: DataTypes.JSONB
  }
}, {
  tableName: 'metrics',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: false
});

module.exports = Metric;
