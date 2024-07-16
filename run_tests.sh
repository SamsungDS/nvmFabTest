if [ "$1" == "-v" ]; then
	pytest -s --html=reports/report.html --self-contained-html
else
	pytest --html=reports/report.html --self-contained-html
fi
