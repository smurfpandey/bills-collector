/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./bills_collector/templates/*.html",
        "./bills_collector/static/src/**/*.js",
        "./node_modules/flowbite/**/*.js"
    ],
    theme: {
        extend: {},
    },
    plugins: [
        require('flowbite/plugin')
    ]
}

