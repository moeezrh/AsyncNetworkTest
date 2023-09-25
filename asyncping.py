import asyncio
import aioping
import logging
from IPScraper import scan, ip_results
import time
import os
import sys
from datetime import datetime
import shutil


# Gets the path to the script
async def get_app_path():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path


async def do_ping(host, duration):

    application_path = get_app_path()

    # Makes the path to the temp files
    temp_path = os.path.join(application_path, "temp")
    temp_file_name = temp_path + "\\" + host + ".txt"

    program_start_time = time.time()
    retry_count = 0
    max_retries = 100

    with open(temp_file_name, "a") as file: 
        
        # Initialize start time and status
        start_time = time.time()
        state_before = "ONLINE"
        # Initializing variables
        total_offline = 0
        total_online = 0
        uptime = 0
        result = 0

        # Event Log Header
        file.write("EVENT LOG:")

        # While the current time passed is less than the test duration, and it hasn't failed to
        # connect more than the max retries
        while ((time.time() - program_start_time) < duration) and retry_count < max_retries:
            # Tries to ping the host with timeout of 2 seconds, and if Timeout, records as offline
            try:           
                delay = await aioping.ping(host, 2) * 1000
                state_after = "ONLINE"
                if state_before != state_after:
                        retry_count = 0
                        state_before = state_after
                        end_time = time.time()
                        off_time = end_time - start_time
                        total_offline += off_time
                        file.write("\nOFFLINE for " + str(off_time) + " s")
                        start_time = end_time

            except TimeoutError:
                print(host + ": Timed out")
                retry_count += 1
                state_after = "OFFLINE"
                if state_before != state_after:
                        state_before = state_after
                        end_time = time.time()
                        on_time = end_time - start_time
                        total_online += on_time
                        file.write("\nONLINE for " + str(on_time) + " s")
                        start_time = end_time
                    
        if state_after == "OFFLINE":
                end_time = time.time()
                off_time = end_time - start_time
                total_offline += off_time
                file.write("\nOFFLINE for " + str(on_time) + " s DISCONNECTED DUE TO TIMEOUT")
        elif state_before == state_after:
                end_time = time.time()
                on_time = end_time - start_time
                total_online += on_time
                file.write("\nONLINE for " + str(on_time) + " s")
        
        file.write("\nEVENT LOG END")

        uptime = float(((total_online) / (total_online + total_offline)) * 100)
        uptime = round(uptime, 2)

        if uptime == float(100):
            result = "PASS"
        elif total_online == 0:
            result = "N/A"
        else:
            result = "FAIL"

        file.write("\nSUMMARY: \n" + host + "\t\t" + str(uptime) + "% uptime" + "\t\t" + result + "\nSUMMARY END")    



async def main():

    logging.basicConfig(level=logging.INFO)

    # temp directory path (to delete all files in it)
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

    # Initial Start Date and Time of Program
    now = datetime.now()
    dt_string = now.strftime("%m_%d_%Yat%I_%M_%S%p")

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
 
    output_folder = 'Outputs\\'

    # Path for output file
    output_path = os.path.join(application_path, output_folder)   

    # Saving the path for output, summary, and event file
    output_summary_file = output_path
    output_event_file = output_path

    output_summary_file += dt_string + "_Summary.txt"
    output_event_file += dt_string + "_Event_Log.txt"

    # User inputs testing time length
    hours = 8
    print("How many hours would you like to test for?")
    test_hours = float(input("Type in the correct hours: "))
    if (str(test_hours) != ""):
         hours = test_hours
    print(hours)
    seconds = float(3600 * hours)
    duration = seconds

    # Date and time of when Ping Testing Begins
    now = datetime.now()
    dt_print = now.strftime("%m/%d/%Y at %I:%M:%S %p")
    start_time = now.strftime("%I:%M:%S %p")

    # Scanning network for devices
    print("Scanning network for devices")
    ip_addr = "192.168.1.1/23"
    scanned_output = scan(ip_addr)
    print("Testing the following IP Addresses " + dt_print + "\n")  
    ip_addresses = ip_results(scanned_output)
    print("Number of Devices:",len(ip_addresses))

    hosts = ip_addresses

    print("\nPinging...")

    tasks = [do_ping(host, duration) for host in hosts]
    await asyncio.gather(*tasks)

    print("Ping Test Complete")
    
    # Summary File Header
    with open(output_summary_file, "a") as file:
        file.write("Summary Results\n\n" + str(hours) + " Hour Test\n\nSTART TIME: " + start_time + "\n\n")

    # Event Log Header
    with open(output_event_file, "a") as file:
         file.write("Event Log \n\n" + str(hours) + " Hour Test\n\nSTART TIME: " + start_time + "\n") 


    for each_file in os.listdir(temp_path):
        file_ip = each_file
        file_ip_start = 0
        file_ip_end = file_ip.find(".txt")
        file_ip = file_ip[file_ip_start: file_ip_end]
        each_file = os.path.join(temp_path, each_file)
        with open(each_file, "r") as source_file, open(output_event_file, "a") as destination_file:
            output = source_file.read()
            event_file_start = output.find("EVENT LOG:")
            event_file_end = output.find("EVENT LOG END")
            event_file = output[event_file_start + 10: event_file_end]
            destination_file.write(file_ip + ":" + event_file + "\n")
        with open(each_file, "r") as source_file, open(output_summary_file, "a") as destination_file:
            output = source_file.read()
            summary_file_start = output.find("SUMMARY")
            summary_file_end = output.find("SUMMARY END")
            summary_file = output[summary_file_start + 10: summary_file_end]
            destination_file.write(summary_file)

    # date and time of end of ping test
    now = datetime.now()
    end_time = now.strftime("%I:%M:%S %p")


    with open(output_summary_file, "a") as file:
        file.write("\nEND TIME: " + end_time)

    with open(output_event_file, "a") as file:
         file.write("END TIME: " + end_time)


if __name__ == "__main__":
    asyncio.run(main())