from bs4 import BeautifulSoup
import requests
import re
import os, glob
from pathlib import Path
from PyPDF2 import PdfFileMerger
import re
import time

def PDFDownload(output_line):
    PDF_download = requests.get(output_line, stream=True, timeout=120)
    with open(path_folder+'page'+str(actual_page)+'.pdf', 'wb') as f:
        f.write(PDF_download.content)
    
# Get hathitrust book link
link = "https://babel.hathitrust.org/cgi/pt?id=mdp.39015023320164"
r  = requests.get(link)
data = r.text
pattern = re.compile(r'\.val\("([^@]+@[^@]+\.[^@]+)"\);', re.MULTILINE | re.DOTALL)
soup = BeautifulSoup(data, "html.parser")

# Number of the book pages and name
number_pages=int(soup.find("span", {"data-slot": "total-seq"}).text)
name_book=soup.find('p').text

# Create a new folder
local=os.getcwd() # Actual Folder
directory_name=name_book.split()[0]+name_book.split()[1]
Path(local+"/"+directory_name).mkdir(parents=True, exist_ok=True)
path_folder=local+"/"+directory_name+"/"

# Download pdf file
begin_page=1
last_page=number_pages+1

for actual_page in range(begin_page, last_page):
    index1 = link.find('/cgi/')
    output_line = link[:index1] + '/cgi/imgsrv/download/pdf?' + link[index1+8:]+';orient=0;size=100;seq='+str(actual_page)+';attachment=0'
    PDFDownload(output_line)
    while os.path.getsize(path_folder+'page'+str(actual_page)+'.pdf') < 2000:
        PDFDownload(output_line)
    
# Merge all pdf files  
ordered_files = sorted(os.listdir(path_folder), key=lambda x: (int(re.sub('\D','',x)),x))
x = [path_folder+a for a in ordered_files if a.endswith(".pdf")]
merger = PdfFileMerger()

for pdf in x:
    merger.append(open(pdf, 'rb'))
    
with open(path_folder+"MERGED_OUTPUT.pdf", "wb") as fout:
    merger.write(fout)
    merger.close()