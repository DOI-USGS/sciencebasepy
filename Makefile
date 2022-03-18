dist:
	python3 setup.py sdist bdist_wheel

publish: dist
	/Users/jllong/Library/Python/3.6/bin/twine upload --cert /Users/jllong/certificates/DOIRootCA2.crt dist/*

clean:
	rm -rf dist
