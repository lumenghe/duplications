# Duplication finder

## Summary

The purpose of this project is to identify the duplications by given a list of movies where each movie is described by two different providers.

It contains the following files and folders:
* duplications: duplication finder code folder
* requirements.txt: all python library need
* CHANGELOG.md
* Dockerfile
* docker-compose.yml
* Makefile
* pylintrc
* README.md
* app_pandas.py version with pandas library


## How to build and run code

* `python duplications/app.py --read <pathToMovieFile> --save <pathToOutputFile>`: to run the project.

* `make format`: to run black lib on all the code (code formatter)

* `make down: docker-compose down --volumes`: to remove declared named volumes

## Potential improvements

* Add unit tests, integration tests, functional tests

* scale docker per year

* Save duplications year per year as it could loss results if it stops in the middle.

* Configuration should not be hardcode, bettre to use consul or config file

* Could use Redis to store dict. especially when scale dockers

* It's better to use pandas

* group movies by duplications per line in output

* If no pandas used, sorted movie length and loop in line 110 should be break if the first movie length is greater than the second one's

