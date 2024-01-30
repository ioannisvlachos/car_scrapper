from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import json
from time import perf_counter
import time
import requests
import os
import websockets
import operator
import argparse
import random
from user_agent import generate_user_agent
from datetime import datetime

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def get_adb_dev():
	is_connected = subprocess.getoutput('adb devices | grep -w device')
	if len(is_connected) > 0:
		print('[+] Device connected successfully!')
		print('[+] Enabling usb tethering..')
		subprocess.getoutput('adb shell svc usb setFunctions rndis')
		time.sleep(1)
		subprocess.getoutput('nmcli networking off')
		time.sleep(1)
		subprocess.getoutput('nmcli networking on')
		time.sleep(1)
		return True	
	return False

def curl_req(ad_num):	
	try:
		output = subprocess.getoutput("curl -L -s car.gr/api/" + str(ad_num))
		print("curl -L -s car.gr/api/" + str(ad_num))
		print(output)
	except websockets.exceptions.ConnectionClosedError as e:
		if e.code == 1006:
			rotate_ip()
			curl_req(ad_num)
	return {ad_num:json.loads(output)}

def curl_req_headers(ad_num, header):
	try:
		output = subprocess.getoutput('curl -L -s car.gr/api/' + str(ad_num) + ' -H User-Agent: ' + header)
		print('curl -L -s car.gr/api/' + str(ad_num) + ' -H User-Agent: ' + header)	
		print(output)
		return {ad_num:json.loads(output)}
	except Exception as e:
		with open('error_log.txt', 'a') as error:
			error.write(f'Error in ad {key}\t{e}\n')

def curl_req_proxy(ad_num, proxy):
	try:
		output = subprocess.getoutput('curl -L -s car.gr/api/' + str(ad_num) + ' -p ' + proxy)
		print('curl -L -s car.gr/api/' + str(ad_num) + ' -p ' + proxy)	
		print(output)
		return {ad_num:json.loads(output)}
	except Exception as e:
		with open('error_log.txt', 'a') as error:
			error.write(f'Error in ad {ad_num}\t{e}\n')

def smp_download(ad_num, header='None', proxy='None'):
	try:
		if header=='None' and proxy!='None':
			output = subprocess.getoutput('curl -L -s car.gr/api/' + str(ad_num) + ' -p ' + proxy)
			print('curl -L -s car.gr/api/' + str(ad_num) + ' -p ' + proxy)	
			output = json.loads(output)
			if output['status'] == 200:
				item = {}
				item.update({'ad_num':ad_num, 'content':output})
				store_single(item)
				print(f'[+] Ad {ad_num} downloaded successfully')
			else:
				print('[-] Ad {} skipped\tstatus_code: {}'.format(ad_num, output['status']))	
		if header!='None' and proxy=='None':
			output = subprocess.getoutput('curl -L -s car.gr/api/' + str(ad_num) + ' -H \'User-Agent: ' + header + '\'')
			print('curl -L -s car.gr/api/' + str(ad_num) + ' -H \'User-Agent: ' + header + '\'')	
			output = json.loads(output)
			if output['status'] == 200:
				item = {}
				item.update({'ad_num':ad_num, 'content':output})
				store_single(item)
				print(f'[+] Ad {ad_num} downloaded successfully')
			else:
				print('[-] Ad {} skipped\tstatus_code: {}'.format(ad_num, output['status']))		
		if header!='None' and proxy!='None':
			output = subprocess.getoutput('curl -L -s car.gr/api/' + str(ad_num) + ' -H \'User-Agent: ' + header + '\' -p ' + proxy)
			print('curl -L -s car.gr/api/' + str(ad_num) + ' -H \'User-Agent: ' + header + '\' -p ' + proxy)
			output = json.loads(output)	
			if output['status'] == 200:
				item = {}
				item.update({'ad_num':ad_num, 'content':output})
				store_single(item)
				print(f'[+] Ad {ad_num} downloaded successfully')
			else:
				print('[-] Ad {} skipped\tstatus_code: {}'.format(ad_num, output['status']))	
		if header=='None' and proxy=='None':	
			output = subprocess.getoutput("curl -L -s car.gr/api/" + str(ad_num))
			print("curl -L -s car.gr/api/" + str(ad_num))	
			output = json.loads(output)
			if output['status'] == 200:
				item = {}
				item.update({'ad_num':ad_num, 'content':output})
				store_single(item)
				print(f'[+] Ad {ad_num} downloaded successfully')
			else:
				print('[-] Ad {} skipped\tstatus_code: {}'.format(ad_num, output['status']))		
	except Exception as e:
		with open('error_log.txt', 'a') as error:
			error.write(f'Error in ad {ad_num}\t{e}\n')

def rotate_ip():
	r = requests.get('http://ifconfig.me')
	print('[*] IP blacklstd -----> ' + r.text)
	print('[<>] Rotating IP...')
	reset = subprocess.getoutput('adb shell cmd connectivity airplane-mode enable')
	time.sleep(1)
	reset = subprocess.getoutput('adb shell cmd connectivity airplane-mode disable')

def store_single(item):
	with open(os.getcwd() + '/car_db/cardb_' + str(item['ad_num']), 'w') as cardb:
		data = json.dumps(item, ensure_ascii = False, indent = 4)
		cardb.write(data)

def create_db_part(start_point):
	db = open('cagrdb_part.json', 'w', encoding = 'utf8')
	db.write('[')
	return db	

def create_db_folder():
	if not os.path.isdir(os.getcwd() + '/car_db'):
		os.mkdir(os.getcwd() + '/car_db')

def get_proxy_file():
	proxy_file = subprocess.getoutput('curl https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt -o http.txt')
	print('[*] Proxy file downloaded successfully!')

def tpe_download(start_point, end_point, workers, store_mode, proxy_list = None, nat = False):
	pool = []
	rot_digit = 0
	ad = start_point
	js_file = []
	item = {}
	dpart = 1
	
	if nat:
		while get_adb_dev() is False:
			print('Connect device in adb mode..')
			print(LINE_UP, end=LINE_CLEAR)

	# filling the pool with first 100 ads
	for i in range(start_point, start_point + 101):
		pool.append(i)
		ad += 1

	# enteering while loop
	while ad < end_point + 1:

		# setting max_workers on threads, more than 10 workers exhausts the server and returns 50x and 1003 errors and could also be considered as ddos attack!
		if nat:
			with ThreadPoolExecutor	(max_workers = workers) as ad_list:
				futures = [ad_list.submit(curl_req, ad_num) for ad_num in pool]
			pool = []
		# uses proxies from loaded proxy file 
		else:
			proxy = random.choice(proxy_list)
			with ThreadPoolExecutor	(max_workers = workers) as ad_list:
				futures = [ad_list.submit(curl_req_proxy, ad_num, proxy) for ad_num in pool]
			pool = []
		
		# checking futures for 429, 503 errors and appending on pool again, writing 200 success on json
		for future in as_completed(futures):
			try:
				for key in future.result().keys():
					if future.result()[key]['status'] == 429:
						pool.append(key)
						rot_digit = 1
					if future.result()[key]['status'] == 200:
						if store_mode == 'single':
							item.update({'ad_num':key, 'content':future.result()[key]})
							store_single(item)
						if store_mode == 'bulk':	
							js_file.append({'ad_num':key, 'content':future.result()[key]})
							if len(js_file) == 1000:
								js_file = sorted(js_file, key = operator.itemgetter('ad_num'))
								with open(os.getcwd() + '/car_db/cardb_' + str(js_file[0]['ad_num']) + '_' + str(js_file[len(js_file)-1]['ad_num']) + '_' +str(dpart), 'w') as cardb:
									data = json.dumps(js_file, ensure_ascii = False, indent = 4)
									cardb.write(data)
									js_file = []
									dpart += 1
			except Exception as e:
				with open('error_log.txt', 'a') as error:
					error.write(f'Error in ad {key}\t{e}\n')
		
		
		# rotating nat ip
		if rot_digit != 0 and nat:
			rotate_ip()
			rot_digit = 0


		# filling search list with 100 
		while len(pool) < 100:
			ad += 1
			pool.append(ad)	
			if ad == end_point and store_mode == 'bulk':
				js_file = sorted(js_file, key = operator.itemgetter('ad_num'))
				with open(os.getcwd() + '/car_db/cardb_' + str(js_file[0]['ad_num']) + '_' + str(js_file[len(js_file)-1]['ad_num']), 'w') as cardb:
					data = json.dumps(js_file, ensure_ascii = False, indent = 4)
					cardb.write(data)


def file_path(file):
    if os.path.isfile(file) or file == 'None':
        return file
    else:
        raise argparse.ArgumentTypeError(f"{file} is not a valid")

def main():
	create_db_folder()
	start_time = datetime.now().isoformat(timespec='milliseconds')

	parser = argparse.ArgumentParser(description='Python script to scrape car.gr, for no reason! Have fun!', epilog="Thanks for using carscrapper!")
	parser.add_argument('-f', '--download-from', help='First ad to be downloaded', default = 0)  # can 'store_false' for no-xxx flags
	parser.add_argument('-t', '--download-to', help='Last ad to be downloaded', default = 99999999)  # can 'store_false' for no-xxx flags
	parser.add_argument('-tpe', '--futures', help='Uses threads to download (need to define workers with -w)', action="store_true")
	parser.add_argument('-w', '--workers', help='Workers (threads) for futures download', default = 4)
	parser.add_argument('-s', '--store-mode', choices = ['single','bulk'], help='Choose if the ads would be downloaded as single file or in 1000 ads per file', default = 'single')
	parser.add_argument('-isp', '--isp-network', help='Chooses isp network for ads download. Requires android device connected in adb mode', action="store_true")
	parser.add_argument('-hd', '--headers', help='Generates user-agent headers',action="store_true")
	parser.add_argument('-p', '--proxy', help='Define proxy, example socks5://proxy:port', default = 'None')
	parser.add_argument('-apf', '--auto-proxy-file', help='Gets recent alive http proxies', action="store_true")
	parser.add_argument('-pf', '--proxy-file', type=file_path, help='Gets recent alive http proxies')

	parsed = parser.parse_args()

	print('Selected options:')
	print(f'From_ad:\t\t{parsed.download_from}')
	print(f'To_ad:\t\t\t{parsed.download_to}')
	if parsed.headers is True:
		print(f'Headers:\t\t{parsed.headers}')
	if parsed.proxy!='None':	
		print(f'Proxy:\t\t\t{parsed.proxy}')
	if parsed.auto_proxy_file is True:	
		print(f'Auto_proxy_file:\t{parsed.auto_proxy_file}')
	if parsed.proxy_file:	
		print(f'Proxy_file:\t\t{parsed.proxy_file}')
	if parsed.isp_network is True or parsed.proxy_file is True or parsed.futures is True:	
		print(f'Workers:\t\t{parsed.workers}')
	if parsed.futures is True:
		print(f'TPE_futures:\t\t{parsed.futures}')	
	print(f'Store_mode:\t\t{parsed.store_mode}')
	if parsed.isp_network is True:
		print(f'ISP_network:\t\t{parsed.isp_network}')
	print('\n\n')

	# req with headers only
	if parsed.headers and parsed.isp_network != True:
		for ad in range(int(parsed.download_from), int(parsed.download_to) + 1):
			header = generate_user_agent()+ '\' -H \'Accept: application/json'
			item = smp_download(ad, header, 'None')
			if type(item) is dict:
				store_single(item)

	# req with proxy only
	if parsed.proxy != 'None' and parsed.isp_network != True:
		for ad in range(int(parsed.download_from), int(parsed.download_to) + 1):
			smp_download(ad,'None',parsed.proxy)

	# req with auto proxy file
	if parsed.auto_proxy_file and parsed.isp_network != True:
		get_proxy_file()
		f = open('http.txt')
		proxy_list = f.readlines()
		for ad in range(int(parsed.download_from), int(parsed.download_to) + 1):
			if parsed.headers == 'True':
				header = generate_user_agent()
				smp_download(ad, header, random.choice(proxy_list))
			else:
				smp_download(ad, 'None', random.choice(proxy_list))

	# req with loaded proxy file			
	if parsed.proxy_file and parsed.futures != True and parsed.isp_network != True:
		f = open(parsed.proxy_file)
		proxy_list = f.readlines()
		for ad in range(int(parsed.download_from), int(parsed.download_to) + 1):
			if parsed.headers == 'True':
				header = generate_user_agent()
				smp_download(ad, header, random.choice(proxy_list))
			else:
				smp_download(ad, 'None', random.choice(proxy_list))

	# req with proxy file and thread_pool_executor
	if parsed.futures and parsed.proxy_file:
		f = open(parsed.proxy_file)
		proxy_list = f.readlines()
		tpe_download(int(parsed.download_from), int(parsed.download_to), int(parsed.workers), parsed.store_mode, proxy_list, False)

	# req with isp network:
	if parsed.isp_network:
		tpe_download(int(parsed.download_from), int(parsed.download_to), int(parsed.workers), parsed.store_mode, 'None', parsed.isp_network)

	if parsed.headers != True and parsed.proxy_file != True and parsed.auto_proxy_file != True and parsed.isp_network != True:
		for ad in range(int(parsed.download_from), int(parsed.download_to) + 1):
			smp_download(ad)
	
	time_end = perf_counter()
	print('elapsed ' + str(time_end-time_start))
	
if __name__ == "__main__":
    main()

