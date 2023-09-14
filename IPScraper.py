import scapy.all as scapy
  
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
    excluded_ips = ["e4:5f:01:c0:98:44",
                    "d8:3a:dd:0c:85:62",
                    "e4:5f:01:c1:0c:75"]
    for i in result:
        macAddr = (i["mac"])
        if macAddr[0:8] == "d8:3a:dd" or macAddr[0:8] == "e4:5f:01" and (macAddr not in excluded_ips):
            print("{}\t{}".format(i["ip"], i["mac"]))
            ips.append(i["ip"])
    return ips


