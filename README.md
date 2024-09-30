# Hathi Trust Digital Library - Complete PDF Download
Download an entire book (or publication) in PDF from Hathi Trust Digital Library without "partner login" requirement.

# Motivation
Hathi Trust Digital Library is a good site to find old publications digitized from different university libraries. However, it limits the download of full PDF files to only partner universities, which are mostly american. In this sense, this code attempts to democratize knowledge and permits to download complete public domain works in PDF from Hathi Trust website.

# Features
- Multi-threaded download of PDF pages and merge in a single file.
- Smart download of pages, skipping already downloaded pages.
- Supports the two most common link formats:
  - https://babel.hathitrust.org/cgi/pt?id={bookID}
  - https://hdl.handle.net/XXXX/{bookID}
- Book splicing, allowing to download only a part of the book.
- Bulk download of multiple books.
- Attempts to avoid Error 429 (Too Many Requests) from Hathi Trust.
  - If the error occurs, the thread will sleep for 5 seconds and try again.
  - Works in most cases, but not always.
- Downloads are attempted 3 times before giving up.
  - Users are notified of the failure, and have the option to redownload the missing pages for merge at the end.
  - Retry attempt count is configurable via --retries option.

# Requirements
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) (bs4)
* [Requests](https://realpython.com/python-requests/)
* [PyPDF2](https://pythonhosted.org/PyPDF2/)
* [Progressbar](https://pypi.org/project/progressbar/)

# Usage

```
usage: hathitrustPDF.py [-h] [-l LINK] [-i INPUT_FILE] [-t THREAD_COUNT] [-r RETRIES] [-b BEGIN] [-e END] [-k]
                        [-o OUTPUT_PATH] [-v] [-V]

PDF Downloader and Merger

options:
  -h, --help            show this help message and exit
  -l LINK, --link LINK  HathiTrust book link
  -i INPUT_FILE, --input-file INPUT_FILE
                        File with list of links formatted as link,output_path
  -t THREAD_COUNT, --thread-count THREAD_COUNT
                        Number of download threads
  -r RETRIES, --retries RETRIES
                        Number of retries for failed downloads
  -b BEGIN, --begin BEGIN
                        First page to download
  -e END, --end END     Last page to download
  -k, --keep            Keep downloaded pages
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        Output file path
  -v, --verbose         Enable verbose mode
  -V, --version         show program's version number and exit
```
