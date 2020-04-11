module.exports = {
    entry: {
        homepage: './frontend/src/homepage.js'
    },
    output:{
        filename: '[name].js',
        path: __dirname +'/frontend/static/frontend/'
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader"
                }
            }
        ]
    }
};