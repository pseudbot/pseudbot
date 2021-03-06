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
	pandoc media/README.md -s -c $(PWD)/img/pub.css -o media/README.html

format:
	black -v -l 80 pseudbot/*
	black -v -l 80 scripts/*
	black -v -l 80 examples/*.py
