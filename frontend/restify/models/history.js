const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('History', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    history: {
      type: DataTypes.STRING,
      allowNull: false
    },
  });
};
