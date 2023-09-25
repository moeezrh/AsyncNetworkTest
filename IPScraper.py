import scapy.all as scapy
import json 

def scan(ip):
    arp_req_frame = scapy.ARP(pdst = ip)

    broadcast_ether_frame = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    
    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame

    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout = 10, verbose = False)[0]
    result = []
    for i in range(0,len(answered_list)):
        client_dict = {"ip" : answered_list[i][1].psrc, "mac" : answered_list[i][1].hwsrc}
        result.append(client_dict)

    return result
  
def ip_results(result):
    print("-----------------------------------\nIP Address\tMAC Address\n-----------------------------------")
    ips = []
    f = open('config.json')
    data = json.load(f)
    target_macs = data.get("target_mac_addresses", [])
    excluded_ips = data.get("excluded_mac_addresses", [])
    end = target_macs[0].index('$')
    length = end - 1
    for i in result:
        mac_addr = (i["mac"])
        for macs in target_macs:
            if mac_addr[0:length] == macs[0:length] and (mac_addr not in excluded_ips):
                print("{}\t{}".format(i["ip"], i["mac"]))
                ips.append(i["ip"])

    return ips


