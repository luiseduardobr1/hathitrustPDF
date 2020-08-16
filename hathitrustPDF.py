from bs4 import BeautifulSoup
import requests
import re
import os
from pathlib import Path
from PyPDF2 import PdfFileMerger
import progressbar


def PDFDownload(output_line):
    PDF_download = requests.get(output_line, stream=True, timeout=300)
    with open(path_folder + 'page' + str(actual_page) + '.pdf', 'wb') as f:
        f.write(PDF_download.content)


# Get hathitrust book link
link = "https://babel.hathitrust.org/cgi/pt?id=uiug.30112106748004"
id_book = re.findall('id=(\w*\.\d*)|$', link)[0]
r = requests.get(link)
soup = BeautifulSoup(r.text, "html.parser")

# Number of the book pages and name
pages_book = int(soup.find("span", {"data-slot": "total-seq"}).text)
name_book = soup.find('meta', {'property': 'og:title'})['content']

if len(name_book) > 55:
    name_book = name_book[:40]

# Remove invalid characters
remove_character = "[],/\\:.;\"'?!*"
name_book = name_book.translate(
            str.maketrans(remove_character, len(remove_character)*" ")).strip()

# Create a new folder
local = os.getcwd()
Path(local + "/" + name_book).mkdir(parents=True, exist_ok=True)
path_folder = local + "/" + name_book + "/"

# Download pdf file
begin_page = 1
last_page = pages_book + 1

# ProgressBar
bar = progressbar.ProgressBar(maxval=last_page,
                              widgets=[progressbar.Bar('=', '[', ']'), ' ',
                                       progressbar.Percentage()])
bar.start()

for actual_page in range(begin_page, last_page):
    output_line = f'https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id={id_book};orient=0;size=100;seq={actual_page};attachment=0'
    PDFDownload(output_line)

    while os.path.getsize(path_folder + 'page' + str(actual_page) + '.pdf') < 6000:
        PDFDownload(output_line)

    bar.update(actual_page + 1)


# Merge all pdf files
ordered_files = sorted(os.listdir(path_folder),
                       key=lambda x: (int(re.sub('\D', '', x)), x))

pdf_list = [path_folder + a for a in ordered_files if a.endswith(".pdf")]
merger = PdfFileMerger()

for pdf in pdf_list:
    merger.append(open(pdf, 'rb'))

with open(path_folder + name_book + "_output.pdf", "wb") as fout:
    merger.write(fout)
    merger.close()

bar.finish()
