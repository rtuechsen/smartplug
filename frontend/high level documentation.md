
# High level documentation frontend

This is the high level documentation for the frontend.

## Architecture

The frontend uses React in compination with Typescript and Material UI.  
For the build system the typescript compiler and vite (bundler) are used.  
Dependencies are installed using npm.  
Each source file contains one (or a few) components, which in turn use other components.  

## Files and places

The folder `src` contains the source code. The entry point is `main.tsx`. All other components are (indirectly) included here.  
The file `AdminSettings.tsx` is intended for settings an admin might want to tweak without touching the overall implementation.  
The file `vite-env.d.ts` is required by the build system.  
The `frontend` folder also contains a number of additional files:
- `index.html`: a bare bones html file that includes the scripts for the components.
- `eslint.config.js`: configuration file for the linter, used only for development.
- `package.json` / `package-lock.json`: lists the dependencies for the project that are installed via npm.
- `tsconfig.json` / `tsconfig.app.json` / `tsconfig.node.json`: compiler options for the typescript compiler.
- `typedocjson`: configuration for typedoc, the generator of the documentation
- `vite.config.ts`: the configuration of the bundler vite.

## Additional notes

- The components are defined as functions instead of classes following modern conventions.
- The `StrictMode` component in `main.tsx` is only used for development to identify side effects.
