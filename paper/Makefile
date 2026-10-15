# Paper 1 build. Needs latexmk + TeX Live (texlive-latex-extra, texlive-bibtex-extra). PY = the project venv python.
PY ?= python3
#   make           -> main.pdf (review mode, anonymous)
#   make pages     -> page count of the content before Limitations (short paper: 4 pages max)
#   make sync    -> regenerate tables.md and appendix_tables.tex from results/, rebuild, and fail if anything is out of date
#   make clean
.PHONY: all pages clean sync
all: main.pdf
main.pdf: main.tex appendix_tables.tex rule_packet_fy2026.md references.bib acl.sty acl_natbib.bst
	latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
pages: main.pdf
	@pdfinfo main.pdf | grep Pages
	@echo "Limitations starts on page:" $$(pdftotext -layout main.pdf - | awk 'BEGIN{p=1} /\f/{p++} /^ *Limitations *$$/{print p; exit}')
clean:
	latexmk -C main.tex; rm -f main.bbl main.run.xml
sync:
	cd .. && $(PY) src/eval/score_common_scale.py > /dev/null && $(PY) src/eval/make_paper1_tables.py > /dev/null && $(PY) src/eval/make_paper1_appendix.py > /dev/null
	$(MAKE) main.pdf
	cd .. && git diff --quiet -- docs/paper1/tables.md paper/appendix_tables.tex results/common_scale || { echo "tables or common scale were out of date and have been regenerated: review the diff and commit"; exit 1; }
