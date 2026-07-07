exename = dhop
sourcefiles = src/dhop.cpp

all: dhop

dhop: $(sourcefiles)
	g++ $(sourcefiles) -o $(exename)

clean:
	@echo "Cleaning $(exename)"
	@rm $(exename)

