CC      := clang
CCFLAGS := -Wall -std=c11

all: clean bin lib

bin:
	$(CC) $(CCFLAGS) -o ass-a4 ass-a4.c
	chmod +x ass-a4

lib:
	$(CC) $(CCFLAGS) -shared -fPIC -o ass-a4.so ass-a4.c

test: all
	cd ./testscripts && \
	python3.7 tc_runner.py && \
	python3.7 tc_report.py && \
	xdg-open $(readlink -f ./results/report.html)

clean:
	rm -f ass-a4
	rm -f ass-a4.so
	rm -rf testscripts/tmp/*
	rm -rf testscripts/results/*

