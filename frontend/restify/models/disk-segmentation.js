const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('DiskSegmentation', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    creation_datetime: {
      type: DataTypes.DATE,
      allowNull: false
    },
    segmentation: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: sequelize.models.Segmentation,
        key: 'id'
      }
    },
    study: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: sequelize.models.Study,
        key: 'id'
      }
    },
  });
};
