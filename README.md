# CarGR Scrapper

This Python script, **car_scrapper**, enables you to download car advertisements from the popular website car.gr. Whether you're a car enthusiast, a data analyst, or just looking to explore web scraping, this script provides a fun and practical way to gather car ad data.

## Requirements

To run **car_scrapper**, ensure you have the following Python libraries installed:

- `concurrent.futures`: For concurrent execution of tasks.
- `subprocess`: For executing subprocesses.
- `json`: For JSON manipulation.
- `time`: For time-related functions.
- `requests`: For making HTTP requests.
- `os`: For interacting with the operating system.
- `websockets`: For working with WebSockets.
- `operator`: For operator functions.
- `argparse`: For parsing command-line arguments.
- `random`: For generating random numbers.
- `user_agent`: For generating user-agent headers.

## Installation

To use **car_scrapper**, follow these steps:

1. Clone this repository to your local machine.
2. Ensure you have Python installed (version 3.6 or higher recommended).
3. Install the required dependencies by running `pip install -r requirements.txt`.
4. You're ready to start scraping car ads from car.gr!

## Usage

The script comes with various command-line options for customizing your scraping experience. Here are the available arguments:

```bash
python car_scrapper.py [-h] [-f DOWNLOAD_FROM] [-t DOWNLOAD_TO] [-tpe] [-w WORKERS] [-s {single,bulk}] [-isp] [-hd] [-p PROXY] [-apf] [-pf PROXY_FILE]
```

- `-f`, `--download-from`: Specify the index of the first ad to be downloaded (default: 0).
- `-t`, `--download-to`: Specify the index of the last ad to be downloaded (default: 99999999).
- `-tpe`, `--futures`: Use threads to download ads (works only with -proxy-file and -isp arguments so far | could work better with fast proxies, haven't tried it yet).
- `-w`, `--workers`: Specify the number of workers (threads) for futures download (default: 4 | DO NOT USE more than 10 workers, could cause denial of service).
- `-s`, `--store-mode`: Choose whether ads should be downloaded as a single file or in bulk (default: single).
- `-isp`, `--isp-network`: Choose Mobile-Network-Operator network for ads download (requires Android device connected in adb mode, do not forget to toggle to mobile data).
- `-hd`, `--headers`: Generate user-agent headers.
- `-p`, `--proxy`: Define a proxy (e.g., `socks5://proxy:port`, default: None).
- `-apf`, `--auto-proxy-file`: Get recent alive HTTP proxies (special thx to TheSpeedX)
- `-pf`, `--proxy-file`: Load HTTP proxies from a specified file.

For more information, use the `-h` or `--help` option.

## Examples

1. To scrape car ads from index 0 to 100 using custom headers:
    ```bash
    python car_scrapper.py -f 0 -t 100 -hd
    ```

2. To scrape car ads from index 32000000 to 33000000 and store them in bulk mode:
    ```bash
    python car_scrapper.py -f 32000000 -t 33000000 -s bulk
    ```
    
3. To scrape car ads from index 32000000 to 33000000 with your file with proxies:
    ```bash
    python car_scrapper.py -f 32000000 -t 33000000 -pf /path/to/file
    ```

4. To scrape car ads from index 32000000 to 33000000 using your MNO network and 10 workers (most efficient so far):
    ```bash
    python car_scrapper.py -f 32000000 -t 33000000 -isp -w 10
    ```

## Acknowledgments

Never use more than 10 workers in concurrent mode!

Thank you for using **car_scrapper**! If you have any questions or suggestions, feel free to open an issue or reach out to me. Happy scraping!
