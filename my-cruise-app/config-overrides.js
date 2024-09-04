const { override, addBabelPreset, addBabelPlugin } = require('customize-cra');

module.exports = override(
  addBabelPreset('@babel/preset-env'),
  addBabelPreset('@babel/preset-react'),
  addBabelPlugin('@babel/plugin-transform-runtime'),
  addBabelPlugin('@babel/plugin-proposal-class-properties') // Add this line
);
