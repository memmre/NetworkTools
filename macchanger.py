import argparse
import os
import random
import re
import subprocess


def checkRootPermission():
    if os.geteuid() != 0:
        print("Permission denied, run as root.")
        return False
    return True


def checkCommand(command):
    if os.system(f"command -v {command} >/dev/null 2>&1") != 0:
        print(f"{command} not found, please install required package(s).")
        return False
    return True


def getArguments():
    argumentParser = argparse.ArgumentParser(description="Change MAC address of a network interface.")
    argumentParser.add_argument('-i', '--interface', dest='interface', help="Interface to change MAC address.")
    argumentParser.add_argument('-m', '--macaddress', dest='macAddress', help="New MAC address to change.")
    args = argumentParser.parse_args()
    if args.interface is None:
        print("No interface entered, enter an interface with '-i' parameter.")
        exit(0)
    else:
        return args


def checkInterface(interface):
    command = subprocess.run(['ifconfig', interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if command.returncode != 0:
        print(f"Interface '{interface}' not found.")
        return False
    return True


def findMACAddress(interface):
    output = subprocess.check_output(["ifconfig", interface])
    mac_address = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(output))
    return mac_address.group(0) if mac_address else None


def generateRandomMACAddress():
    values = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, values))


def changeMACAddress(interface, newMACAddress):
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", newMACAddress])
    subprocess.call(["ifconfig", interface, "up"])


if __name__ == "__main__":
    if checkRootPermission() and checkCommand("ifconfig"):
        arguments = getArguments()
        if checkInterface(arguments.interface):
            macAddress = arguments.macAddress if arguments.macAddress is not None else generateRandomMACAddress()
            print(f"Current MAC address of {arguments.interface}: {findMACAddress(arguments.interface)}")
            changeMACAddress(arguments.interface, macAddress)
            if macAddress == findMACAddress(arguments.interface):
                print(f"MAC address changed successfully!")
                print(f"New MAC address of {arguments.interface}: {findMACAddress(arguments.interface)}")
            else:
                print("An error occurred while changing the MAC address.")
