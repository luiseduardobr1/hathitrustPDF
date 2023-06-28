#!/usr/bin/env python3
import argparse
import os
import re
import threading
import time
from pathlib import Path

import progressbar
import requests
from PyPDF2 import PdfMerger
from bs4 import BeautifulSoup


class Downloader:
    def __init__(self, max_threads, to_download, bar_, path, verbose):
        self.max_threads = max_threads
        self.download_threads = []
        self.finished_threads = []
        self.to_download = to_download
        self.bar = bar_
        self.lock = threading.Lock()
        self.path = path
        self.verbose = verbose

    def download(self):
        def download_finished(thread_: DownloadThread):  # callback function
            self.finished_threads.append(thread_)
            self.bar.update(1)
            with self.lock:
                if len(self.to_download) > 0:
                    # create new thread with new ID, link, and callback
                    new_thread = DownloadThread(link_=self.to_download.pop(0), downloader_=self,
                                                callback=download_finished)
                    self.download_threads.append(new_thread)
                    new_thread.start()

                else:
                    if len(self.download_threads) == len(self.finished_threads):
                        if self.verbose:
                            print("All downloads finished\n")

        # Start initial set of threads
        for _ in range(min(self.max_threads, len(self.to_download))):
            thread = DownloadThread(link_=self.to_download.pop(0), downloader_=self,
                                    callback=download_finished)
            self.download_threads.append(thread)
            thread.start()

        # Wait for all download threads to finish
        for thread in self.download_threads:
            thread.join()

    def download_file(self, link_):
        retry_count = 0
        page_number = re.search(r"seq=(\d+)", link_)
        if page_number is not None:
            page_number = page_number.group(1)
        else:
            page_number = ""
        if self.verbose:
            print(f"Downloading page {page_number}")
        # check if file exists
        if os.path.exists(os.path.join(self.path, 'page' + page_number + '.pdf')):
            if self.verbose:
                print(f"File page{page_number}.pdf already exists. Skipping...")
            return
        pdf_download = requests.get(link_, stream=True, timeout=300)
        if pdf_download.status_code != 200:

            while retry_count < 3:
                if pdf_download.status_code == 200:
                    break
                retry_count += 1
                if self.verbose:
                    print(f"Error downloading {link_}: Status code {pdf_download.status_code}. "
                          f"Retrying...{retry_count}/3")
                if pdf_download.status_code == 429:
                    if self.verbose:
                        print("Too many requests. Waiting 5 seconds...")
                    time.sleep(5)
                pdf_download = requests.get(link_, stream=True, timeout=300)
            if pdf_download.status_code != 200:
                if self.verbose:
                    print(f"Error downloading {link_} with status code {pdf_download.status_code}. Skipping...")
                return

        path = os.path.join(self.path, 'page' + page_number + '.pdf')
        try:
            with open(path, 'wb') as f:
                f.write(pdf_download.content)
        except Exception as e_:
            if self.verbose:
                print("Error writing file " + path)
                print(e_)
            return
        if self.verbose:
            print(f"Finished downloading page {page_number}")


class DownloadThread(threading.Thread):
    def __init__(self, link_, downloader_, callback):
        threading.Thread.__init__(self)
        self.link = link_  # link to download
        self.downloader = downloader_  # Downloader object
        self.callback = callback  # callback function to call when download is finished

    def run(self):
        self.downloader.download_file(self.link)
        self.callback(self)


def check_files_missing(begin, end, path_folder, pdf_list):
    missing_pages = []
    for page in range(begin, end):
        if os.path.join(path_folder, f"page{page}.pdf") not in pdf_list:
            missing_pages.append(page)
    for file in os.listdir(path_folder):
        if os.path.getsize(os.path.join(path_folder, file)) == 0:
            missing_pages.append(int(file[4:-4]))

    return missing_pages


def main():
    parser = argparse.ArgumentParser(description='PDF Downloader and Merger')
    parser.add_argument('-l', '--link', help='HathiTrust book link')
    parser.add_argument('-i', '--input-file', default="", help='File with list of links formatted as link,output_path')
    parser.add_argument('-t', '--thread-count', type=int, default=5, help='Number of download threads')
    parser.add_argument('-b', '--begin', type=int, default=1, help='First page to download')
    parser.add_argument('-e', '--end', type=int, default=0, help='Last page to download')
    parser.add_argument('-k', '--keep', action='store_true', help='Keep downloaded pages')
    parser.add_argument('-o', '--output-path', default=None, help='Output file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')
    #  todo: add -i option to take a file with a list of link:output
    args = parser.parse_args()

    if not (args.link or args.input_file):
        parser.print_help()
        exit(1)

    if args.input_file != "":
        with open(args.input_file, 'r') as f:
            links = dict(map(lambda x: x.split(','), f.readlines()))
    else:
        links = {args.link: args.output_path}
    for link, output in links.items():
        download_link(args, link, output.rstrip('\n'))


def download_link(args, link, output):
    if "babel.hathitrust.org" in link:
        id_book = re.findall(r'id=(\w*\.\d*)|$', link)[0]
    elif "hdl.handle.net" in link:
        link.rstrip('/')
        id_book = re.findall(r'.+/(.+)', link)[0]
    else:
        print(f"{link}: Unknown link format. Please use a link from babel.hathitrust.org or hdl.handle.net")
        return
    r = requests.get(link)
    soup = BeautifulSoup(r.text, "html.parser")

    # Number of the book pages and name
    pages_book = int(soup.find("section", {'class': 'd--reader--viewer'})['data-total-seq'])
    name_book = soup.find('meta', {'property': 'og:title'})['content']

    # Limit book title
    if len(name_book) > 55:
        name_book = name_book[:40]

    # Remove invalid characters
    remove_character = "[],/\\:.;\"'?!*"
    name_book = name_book.translate(str.maketrans(remove_character, len(remove_character)*" ")).strip()
    if args.output_path is None:
        args.output_path = name_book + ".pdf"
    # Create a new folder
    local = os.getcwd()
    path_folder = os.path.join(local, "tmp")
    Path(path_folder).mkdir(parents=True, exist_ok=True)

    # Download pdf file
    begin_page = args.begin
    last_page = pages_book + 1 if (args.end == 0 or args.end > pages_book + 1) else args.end + 1

    # ProgressBar
    bar = progressbar.ProgressBar(maxval=last_page,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ',
                                           progressbar.Percentage()])
    bar.start()
    base_link = 'https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id={};orient=0;size=100;seq={};attachment=0'
    links = [base_link.format(id_book, actual_page) for actual_page in range(begin_page, last_page)]

    downloader = Downloader(max_threads=args.thread_count, to_download=links, bar_=bar,
                            path=path_folder, verbose=args.verbose)
    downloader.download()

    # Sort by page number, trims "page" and ".pdf"
    ordered_files = sorted(os.listdir(path_folder), key=lambda x: int(x[4:-4]))

    # Merge PDF files
    pdf_list = [os.path.join(path_folder, a) for a in ordered_files if a.endswith(".pdf")]
    # print(pdf_list)
    missing_pages = check_files_missing(begin_page, last_page, path_folder, pdf_list)

    # Check if there are missing pages
    while len(missing_pages) > 0:
        for page in missing_pages:
            print(f"Missing/corrupted page {page}. Download it manually at {base_link.format(id_book, page)}, and "
                  f"save it to {os.path.join(path_folder, f'page{page}.pdf')}.\n")
        print("You have missing pages. Press enter to continue, R to recheck, D to redownload, or CTRL+C to exit.")
        try:
            # Wait for user input
            while True:
                key = input()
                if key.lower() == "r":
                    # Recheck missing pages
                    ordered_files = sorted(os.listdir(path_folder), key=lambda x: int(x[4:-4]))
                    pdf_list = [os.path.join(path_folder, a) for a in ordered_files if a.endswith(".pdf")]
                    missing_pages = check_files_missing(begin_page, last_page, path_folder, pdf_list)
                    break
                elif key.lower() == "d":
                    # Try to download missing pages
                    for i in missing_pages:
                        downloader.download_file(base_link.format(id_book, i))

                    ordered_files = sorted(os.listdir(path_folder), key=lambda x: int(x[4:-4]))
                    pdf_list = [os.path.join(path_folder, a) for a in ordered_files if a.endswith(".pdf")]
                    missing_pages = check_files_missing(begin_page, last_page, path_folder, pdf_list)
                    break

                elif key == "":
                    # force continue, even with missing pages
                    missing_pages = []
                    break
        except KeyboardInterrupt:
            return

    merger = PdfMerger()

    for pdf in pdf_list:
        with open(pdf, 'rb') as file:
            merger.append(file)

    try:
        with open(output, "wb") as fout:
            merger.write(fout)
    except Exception as e:
        print("Error writing merged file " + args.output_path)
        print(e)

    # Cleanup
    if not args.keep:
        for i in pdf_list:
            try:
                os.remove(os.path.join(path_folder, i))
            except Exception as e:
                print("Error removing file " + i)
                print(e)
        try:
            os.rmdir(path_folder)
        except Exception as e:
            print("Error removing folder " + path_folder)
            print(e)

    bar.finish()
    merger.close()


if __name__ == '__main__':
    main()
