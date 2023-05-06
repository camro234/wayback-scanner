# wayback scanner
Python script written for security researchers to scan for locations (files, sites, subdomains) in the way-back machine (web.archive.org) for a specified URL.

## summary
The script will scan for locations and find interesting file types based on a hardcoded list of mime types. It will output results in to a file.
The scanner will inform the researcher of everything found that is currently live on that site, and seperately everything that is no longer live.

The idea is not only as a web scanner (that can be done through other means such as ffuf), but as a way to find what _used_ to exist and may be sensitive or 
provide otherwise useful information to further research.

## pre-requisites:
python3 -m pip install -r requirements.txt --user

## usage example:
python3 wayback_scanner.py www.somerandomsite.com output.log

