var="$(date +%F_%H-%M-%S)"
if [ "$1" == "-v" ]; then
	pytest -s --html=reports/report_$var.html --self-contained-html
else
	pytest --html=reports/report_$var.html --self-contained-html
fi
