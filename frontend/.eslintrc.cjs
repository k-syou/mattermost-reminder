/* eslint-env node */
require('@typescript-eslint/eslint-plugin')
require('@typescript-eslint/parser')
require('eslint-plugin-vue')

module.exports = {
  root: true,
  'extends': [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@typescript-eslint/recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    parser: '@typescript-eslint/parser'
  },
  rules: {
    'vue/multi-word-component-names': 'off'
  }
}
