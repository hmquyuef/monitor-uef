const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Agent = sequelize.define('Agent', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true,
    field: 'id'
  },
  name: {
    type: DataTypes.STRING,
    unique: true,
    allowNull: false
  },
  hostname: DataTypes.STRING,
  ip_address: DataTypes.STRING,
  api_key: {
    type: DataTypes.STRING,
    unique: true,
    allowNull: false
  },
  status: {
    type: DataTypes.STRING,
    defaultValue: 'offline'
  },
  last_seen: DataTypes.DATE
}, {
  tableName: 'agents',
  timestamps: true,
  createdAt: 'created_at',
  updatedAt: false
});

module.exports = Agent;
