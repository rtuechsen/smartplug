
cd backend

rm -rf docs

doxygen

cd ..

cd frontend

rm -rf docs

npx typedoc

cd ..

