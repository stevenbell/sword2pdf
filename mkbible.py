# Render a SWORD module as a LaTeX document which can then be compiled into a PDF.
# Pages are richly crosslinked with book/chapter indices to make navigation easy.
# The original output target is the reMarkable paper tablet, but it should work
# on any device that supports PDF links.

from pysword.modules import SwordModules
from pysword.bible import SwordBible
from pysword.canons import canons
import re
from IPython import embed

SWORD_PATH = '/home/steven/.sword/'
MODULE = 'ESV'
RESULT_PATH = 'content.tex'

# Get the modules, returns a dictionary of name:module
modules = SwordModules().parse_modules()

# Print the names of the available modules
print("Available modules:")
for m in modules:
  print("  " + m)

biblePath = SWORD_PATH + modules[MODULE]['datapath']
bible = SwordBible(biblePath)

# The structure of a Bible is stored in a "canon", because we might want to
# display the same text in various arrangements.
# We'll default to NRSV for now
canon = canons['nrsv']

# Transform the "canon" into a dictionary of books, since the default format is a pain
# The canon contains a dict with 'ot' and 'nt'.  Each of these is a list of books.
# Each book is a tuple of 3 abbreviated names plus a list of the number of verses in each chapter.
dictcanon = {}
for book in canon["ot"]:
  dictcanon[book[0]] = book[3]
for book in canon["nt"]:
  dictcanon[book[0]] = book[3]

#START_REF = 
BOOK = "Romans"
START_CH = 1
START_VERSE = 1
END_CH = 16
END_VERSE = 27


# TODO: generate an OT/NT page?
outfile = open(RESULT_PATH, 'w')

chNum = START_CH
verseNum = START_VERSE
while (chNum < END_CH) or (chNum == END_CH and verseNum <= END_VERSE):
  if verseNum == 1:
    outfile.write('\hangsection%\n')
    print(f"CHAPTER {chNum}")

  verses_in_chapter = dictcanon[BOOK][chNum-1] # chapters are 1-indexed!
  while (chNum < END_CH and verseNum <= verses_in_chapter) or (chNum == END_CH and verseNum <= END_VERSE):

    # set "clean=False" to keep the markup (formatting, xref, headings, etc)
    try:
      verse = bible.get(books=BOOK, chapters=chNum, verses=verseNum, clean=False)
    except ValueError as e:
      # This should never happen if we're keeping track of verses correctly; if it does
      # be noisy so it can be fixed, but continue to get as much output as possible.
      print(e)

    text = verse

    # Use a series of regular expressions to conver the OSIS to LaTeX
    #note
    # q (quote): extract the particular quote mark

    # For these tags, insert particular LaTeX markup
    text = re.sub(r'<title.*?>(.+?)</title>', r'\\sectiontitle{\1}', text)

    # For these tags, just strip the tag and leave the text
    text = re.sub(r'<divineName>(.+?)</divineName>', r'\1', text)
    #text = re.sub(r'(<[^\>]+type="x-br"[^\>]+\>)', r'\1 ', text)

    # Discard these tags along with their content
    text = re.sub('<note.+?/note>', '', text)
    #text = re.sub('<>', '', text)
    text = re.sub('<lb type="x-end-paragraph"/>', '\n\n', text)
    text = re.sub('<lb type="x-begin-paragraph"/>', '', text)


    text = re.sub('<l.*?/>', '', text)
    text = re.sub('<q.*?/>', '', text)

    print(f"v{verseNum}")
    print("{} #######".format(verse))
    print(verse)
    print("------")
    print(text)

    #if num > 1:
    outfile.write(r'\versenum{' + str(verseNum) + '}')
    outfile.write(text)
    outfile.write("\n")

    verseNum = verseNum + 1

  chNum = chNum+1
  verseNum = 1


outfile.close()

