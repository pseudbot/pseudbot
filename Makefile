install:
	python setup.py install

clean:
	python setup.py clean
	rm -rvf build *.egg-info dist

reinstall:
	$(MAKE) clean
	$(MAKE) install

readme-preview:
	pandoc README.md -s -c img/pub.css -o README.html

format:
	black -v -l 80 pseudbot/*
	black -v -l 80 scripts/*
	
	# Uncomment below if we ever include code examples:
	##black -v -l 80 examples/*.py
