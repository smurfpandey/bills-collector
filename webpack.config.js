const webpack = require('webpack');
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyPlugin = require("copy-webpack-plugin");

const config = {
    // context: path.resolve(__dirname, 'bills_collector/static/src'),
    entry: path.resolve(__dirname, 'bills_collector/static/src/app.js'),
    output: {
        path: path.resolve(__dirname, 'bills_collector/static/dist'),
        filename: 'bundle.js',
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css']
    },
    plugins: [
        new webpack.ProgressPlugin(),
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin(),
        new CopyPlugin({
            patterns: [
              { from: path.resolve(__dirname, 'bills_collector/static/src/images'), to: path.resolve(__dirname, 'bills_collector/static/dist/images') },
            ],
          }),
    ],
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader'],
            }
        ],
    },
};

module.exports = config;
