docformatter -i ./backend/smartplug_app/*.py && black ./backend/smartplug_app/

cd frontend
npx prettier ./src/ --write --use-tabs --tab-width 4
cd ..
