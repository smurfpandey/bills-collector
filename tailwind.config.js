/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./bills_collector/templates/*.{html,j2}",
        "./node_modules/flowbite/**/*.js"
    ],
    theme: {
        extend: {},
    },
    plugins: [
        require('flowbite/plugin')
    ]
}

