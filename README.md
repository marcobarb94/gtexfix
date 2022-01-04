# gtexfix

Fix for Google Translate to process LaTeX documents.
Updated to simplify some steps. 

**Description**

Code ``step1.py`` replaces the LaTeX constructs by tokens. After passing translation the tokens are then restored by ``step2.py``. Simple tokens 
of the type ``[number.number]`` are used, which are more friendly to Google Translate (or DeepL). If the token type conflicts with the original text the user is notified. At times, Google Translate will corrupt the tokens and may even change their numbers unpreditably (the side effect of machine learning!). Corrupted tokens are identified and reported to the user for manual treatment.

**Usage**

1. Run ``$./step1.py path/source.tex`` to produce ``path/source_XX.txt``, where ``XX`` is ``00,01,...``. Several files are produced if the output exceeds the Google Translate character limit (actual: 5000). If you need only one file, pass ``-i`` as optional parameter (e.g. ``$./step1.py -i path/source.tex``). 

2. Feed files ``<source_*.txt>`` to Google Translate or DeepL. I suggest to use DeepL desktop app to speed up the work. 

3. Run ``$./step2.py <source>`` to produce ``<sourceT9N.tex>``. It looks in your folder to find all files that start like ``source_``. This code removes the italian advertisement message of DeepL too (for now). 

4. Check for the corrupted tokens. You should be able to substitute them manually by looking at ``gtexfix_commands.json``. 

**Example**

Sample LaTeX input is give in the ``examples`` folder. 

Step 1. Run ``python step1.py examples/example``:
 
	$ python step1.py examples/example
    LaTeX file: examples\example.tex
    No token conflicts detected. Proceeding.
    Output file: examples\example_00.txt
    Output file: examples\example_01.txt
    Output file: examples\example_02.txt
    Supply the output file(s) to Google Translate

Step 2. Google Translate or DeepL.

Step 3. Run ``python step2.py examples/example``:

	$ python step2.py examples/example
    Input file (original): examples/example
    I found these files:
    ['examples\\example_00.txt', 'examples\\example_01.txt', 'examples\\example_02.txt']
    Backup file not found
    Output file: examples/exampleT9N.tex
    No corrupted tokens. The translation is ready.

Step 4. 


