import asyncio
import aioping
import logging
from IPScraper import scan, ip_results
import time
import os
import sys
from datetime import datetime
import shutil

logging.basicConfig(level=logging.INFO)

# Set the duration for the loop in seconds
duration = 60*60  # Change this to the desired duration in seconds

# temp directory path
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

temp_path = os.path.join(application_path, "temp")

for item in os.listdir(temp_path):
    item_path = os.path.join(temp_path, item)
    if os.path.isfile(item_path):  # Check if it's a file
        os.remove(item_path)  # Remove the file
    elif os.path.isdir(item_path):  # Check if it's a directory
        shutil.rmtree(item_path)  # Remove the directory and its contents

# Date and time of when Ping Testing Begins
now = datetime.now()
dt_print = now.strftime("%m/%d/%Y at %I:%M:%S %p")
start_time = now.strftime("%I:%M:%S %p")

print("Scanning network for devices")
ip_addr = "192.168.1.1/23"
scanned_output = scan(ip_addr)
print("Testing the following IP Addresses " + dt_print + "\n")  
ip_addresses = ip_results(scanned_output)
print("Number of Devices:",len(ip_addresses))

hosts = ip_addresses

async def do_ping(host):

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    temp_path = os.path.join(application_path, "temp")
    temp_file_name = temp_path + "\\" + host + ".txt"

    program_start_time = time.time()
    retry_count = 0
    max_retries = 10

    with open(temp_file_name, "a") as file: 

        now = datetime.now()
        start_time = time.time()
        dt_print = now.strftime("%m/%d/%Y at %H:%M:%S PST ")
        state_before = "ONLINE"

        print("\nPinging...")

        while ((time.time() - program_start_time) < duration) and retry_count < max_retries:
            try:           
                delay = await aioping.ping(host, 0.5) * 1000
                state_after = "ONLINE"
                if state_before != state_after:
                    state_before = state_after
                    end_time = time.time()
                    on_time = end_time - start_time
                    file.write("\nOFFLINE for " + str(on_time) + " s")
                    start_time = end_time

            except TimeoutError:
                print(host + ": Timed out")
                retry_count += 1
                state_after = "OFFLINE"
                if state_before != state_after:
                    state_before = state_after
                    end_time = time.time()
                    on_time = end_time - start_time
                    file.write("\nONLINE for " + str(on_time) + " s")
                    start_time = end_time
                    
        else:
            if state_after == "OFFLINE":
                end_time = time.time()
                on_time = end_time - start_time
                file.write("\nOFFLINE for " + str(on_time) + " s DISCONNECTED DUE TO TIMEOUT")
            elif state_before == state_after:
                print("Ping Test Done")
                end_time = time.time()
                on_time = end_time - start_time
                file.write("\nONLINE for " + str(on_time) + " s")

async def main():
    tasks = [do_ping(host) for host in hosts]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())