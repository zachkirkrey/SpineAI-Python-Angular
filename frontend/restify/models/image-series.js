const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('ImageSeries', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    study: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'Study',
        key: 'id'
      }
    },
    type: {
      type: DataTypes.STRING,
      allowNull: false
    },
    image_pickled: {
      type: DataTypes.BLOB
    },
    metadata_pickled: {
      type: DataTypes.BLOB
    }
  });
};
