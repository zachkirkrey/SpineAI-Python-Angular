const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('ReferralReason', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    reason: {
      type: DataTypes.STRING,
      allowNull: false
    },
  });
};
