from concurrent.futures.thread import ThreadPoolExecutor
import concurrent.futures
import requests
import sys
from tqdm import tqdm
from datetime import datetime, timedelta


def make_request(url):
    try:
        response = requests.get(url, timeout=5, stream=True)
    except:
        return (408, url)
    return (response.status_code, url)


# Define the URL of the Wayback Machine API
url = 'http://web.archive.org/cdx/search/cdx'

# Define the URL of the site you want to retrieve file listings for
execution_parameter = ''
output_file = 'output.log'
if len(sys.argv) > 1:
    execution_parameter = sys.argv[1]
else:
    print("No url provided")
    exit(-1)
if len(sys.argv) > 2:
    output_file = sys.argv[2]

site_url = execution_parameter.rstrip('/')

mime_types = [
    "text/plain",
    "text/html",
    "application/json",
    "text/javascript",
    "application/x-sh",
    "application/java-archive",
    "application/x-python-code",
    "text/x-python",
    "application/x-httpd-php",
    "application/octet-stream",
    "application/pdf",
    "application/rtf",
    "application/x-tar",
    "application/zip",
    "application/x-7z-compressed",
    "application/gzip",
    "application/x-bzip",
    "application/x-bzip2",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.visio",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/csv"
]

# Define the start and end years for the time range you want to retrieve file listings for
start_year = 2000
end_year = datetime.today().year
found_files = []

# Loop through the snapshot dates and retrieve the file listings for each one
print("Scanning way-back machine for interesting locations (sites / files / subdomains) related to the specified URL...")
for mime_type in mime_types:
    snapshot_url = f'{url}?url={site_url}/*&output=json&fl=original&filter=mimetype:{mime_type}&matchType=domain&collapse=urlkey&from={start_year}&to={end_year}'
    response = requests.get(snapshot_url)
    if response.status_code == 200:
        if response.content.decode() != '[]':
            file_list = [line.strip() for line in response.content.decode().split(',\n')]
            for found_file in file_list:
                reformatted_found_file = found_file.replace('[', '').replace(']', '').replace('"','')
                if reformatted_found_file != '' and reformatted_found_file != 'original' and reformatted_found_file not in found_files:
                    found_files.append(reformatted_found_file)

found_files.sort()

live_locations = []
past_locations = []
print("Found {} locations".format(len(found_files)))
print("Checking which of the found locations are still live...")
iteration = 0
count = len(found_files)

with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(make_request, found_file) for found_file in found_files]

    with tqdm(total=len(found_files)) as pbar:
        for future in concurrent.futures.as_completed(futures):
            rsp = future.result()
            if rsp[0] == 200:
                live_locations.append(rsp[1])
            else:
                past_locations.append(rsp[1])
            pbar.update(1)

with open(output_file, 'w') as f:
    f.write("%s\n" % "# Live locations:")
    for live_location in live_locations:
        f.write("%s\n" % live_location)
    f.write("\n")

with open(output_file, 'a') as f:
    f.write("%s\n" % "# Past locations (to view any of these, open your browser to https://web.archive.org/ and put the address of the 'past location' in the search field):")
    for past_location in past_locations:
        f.write("%s\n" % past_location)

print("Done!")
