import { defineConfig, globalIgnores } from "eslint/config";
import globals from "globals";
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";


export default defineConfig([
	{ files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"] },
	{ files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"], languageOptions: { globals: globals.browser } },
	{ files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"], plugins: { js }, extends: ["js/recommended"] },
	tseslint.configs.recommended,
	pluginReact.configs.flat.recommended,
	{
		rules: {
			"react/react-in-jsx-scope": "off",
			"react/jsx-uses-react": "off",
			"semi": ["warn", "always"],
			"@typescript-eslint/explicit-function-return-type": "warn",
			"@typescript-eslint/consistent-type-definitions": "warn",
			"@typescript-eslint/no-unused-vars": "warn",
			"no-unused-labels": "warn",
			"no-unused-expressions": "warn"
		}
	},
	globalIgnores(["dist/", "node_modules/"]),
]);