#For maintainers to publish to PyPi
dist:
	python3 setup.py sdist bdist_wheel

publish: dist
	twine upload --cert (PATH_TO_CERT)/DOIRootCA2.crt dist/*

clean:
	rm -rf dist
