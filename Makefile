dist:
	python3 setup.py sdist bdist_wheel

publish: dist
	twine upload --cert /Users/jllong/certificates/DOIRootCA2.crt dist/*

clean:
	rm -rf dist
