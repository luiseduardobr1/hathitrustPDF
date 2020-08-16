# Hathi Trust Digital Library - Complete PDF Download
Download an entire book (or publication) in PDF from Hathi Trust Digital Library without "partner login" requirement.

# Motivation
Hathi Trust Digital Library is a good site to find old publications digitized from different university libraries. However, it limits the download of full PDF files to only partner universities, which are mostly american. In this sense, this code attempts to democratize knowledge and permits to download complete public domain works in PDF from Hathi Trust website.

# Requirements
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) (bs4)
* [Requests](https://realpython.com/python-requests/)
* [PyPDF2](https://pythonhosted.org/PyPDF2/)

# How to use it
Copy Hathi Trust book URL and paste into "link" variable on code line:
```python
...
link = "https://babel.hathitrust.org/cgi/pt?id=mdp.39015023320164"
r  = requests.get(link)
...
```
Keep the same pattern presented (**numbers at the end**)! 

After that, all pages will be downloaded as PDF files and merged in a single file named **MERGED_OUTPUT.pdf** in the corresponding folder. The individual pages are not *automatically* deleted after the end of the process! 

# Slice pages
The code also allows you to remove only a range of pages. For that purpose, just edit the start and end page on code line:
```python
...
# Download pdf file
begin_page=1
last_page=number_pages+1

for actual_page in range(begin_page, last_page):
...
```

# Screenshot
![captura-hait](https://user-images.githubusercontent.com/56649205/72007547-abc73680-3230-11ea-9e74-4e6e495c90d2.PNG)
