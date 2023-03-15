import argparse
import os
import scapy.all as scapy
import subprocess


def checkRootPermission():
    if os.geteuid() != 0:
        print("Permission denied, run as root.")
        return False
    return True


def getArguments():
    argumentParser = argparse.ArgumentParser(description="Scan for devices in an IP range.")
    argumentParser.add_argument("-i", "--iprange", dest="ipRange", help="IP range to scan.")
    args = argumentParser.parse_args()
    if args.ipRange is None:
        print("No IP range entered, enter an IP range with '-i' parameter.")
        exit(0)
    else:
        return args


def sendAndReceivePackets(ipRange):
    arp = scapy.ARP(pdst=ipRange)
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    return scapy.srp(packet, timeout=3, verbose=0)[0]


def printDeviceList(packets):
    subprocess.call(["clear"])
    if len(packets) != 0:
        print("\n     IP Address         MAC Address")
        print(f"     {'-' * 15}    {'-' * 17}")
        i = 0
        for sent, received in packets:
            i += 1
            print("{:3}) {:15}    {:17}".format(i, received.psrc, received.hwsrc))
        print("\n{:3} device(s) found.".format(len(packets)))
    else:
        print("No devices found.")


if __name__ == "__main__":
    if checkRootPermission():
        arguments = getArguments()
        while True:
            printDeviceList(sendAndReceivePackets(arguments.ipRange))
