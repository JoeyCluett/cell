
docs := *.md
examples := examples/*

all: test

%.md: ${examples}
	./process_md "$@"

compile: ${docs}

test: compile
	./run_all_tests
	./cell incell/cell.cell

