if [ "$1" == "-v" ]; then
	pytest -s --html=report.html
else
	pytest --html=report.html
fi
