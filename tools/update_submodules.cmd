@echo off
cd ..
echo "Inicializando subm¢dulos (si existen no se hace nada)"
git submodule init
echo "Actualizando subm¢dulos"
git submodule update --remote
pause