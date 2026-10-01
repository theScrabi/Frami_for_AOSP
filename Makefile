# SPDX-License-Identifier: GPL-3.0-only
# Build the German AOSP/HeliBoard main dictionaries into build/.
# Requires GNU Make >= 4.3 (grouped targets).

LOCALES := de de_DE
OUT     := build

SOURCES      := build_de_dict.py de/de_full_frequency.txt de/de_DE.dic de/de_DE.aff de/allowlist.txt
DICTS        := $(foreach l,$(LOCALES),$(OUT)/main_$(l).dict)
COMBINED     := $(foreach l,$(LOCALES),$(OUT)/main_$(l).combined)
INTERMEDIATE := $(COMBINED) $(OUT)/rejected_by_hunspell.txt

.PHONY: all clean distclean check-tools
# Keep the intermediate files after a build, and don't rebuild them
# just because `make clean` removed them.
.SECONDARY: $(INTERMEDIATE)

all: $(DICTS)

check-tools:
	@for cmd in python3 hunspell java; do \
		command -v $$cmd >/dev/null || { echo "error: $$cmd not found" >&2; exit 1; }; \
	done

$(INTERMEDIATE) &: $(SOURCES) | check-tools
	@mkdir -p $(OUT)
	@echo "==> Generating wordlists, validated with hunspell"
	python3 build_de_dict.py --out $(OUT) --locale $(LOCALES)

$(OUT)/main_%.dict: $(OUT)/main_%.combined dicttool_aosp dicttool_aosp.jar
	@echo "==> Compiling $@"
	./dicttool_aosp makedict -s $< -d $@ -2 >/dev/null

# Remove the intermediate files, keep the dictionaries.
clean:
	rm -f $(INTERMEDIATE)

# Remove all build output.
distclean:
	rm -rf $(OUT)
