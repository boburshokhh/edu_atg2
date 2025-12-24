import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import globals from 'globals'

export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/backend_django/**',
      '**/public/**',
      '**/netlify/**',
    ],
  },

  js.configs.recommended,
  ...vue.configs['flat/recommended'],

  {
    files: ['**/*.{js,mjs,cjs,vue}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      // Keep noise low for legacy code; tighten later.
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
      'no-undef': 'off', // Vite injects import.meta/env; also many globals are browser-side

      // Vue project conventions (relax to avoid failing CI/builds)
      'vue/multi-word-component-names': 'off',
      'vue/no-reserved-component-names': 'off',
      'vue/no-unused-components': 'warn',
      'vue/no-required-prop-with-default': 'warn',
      'vue/no-unused-vars': 'warn',

      // Legacy code: keep as warnings for now
      'no-unreachable': 'warn',
      'no-dupe-keys': 'warn',
      'no-empty': 'warn',
      'no-useless-escape': 'warn',
    },
  },
]


