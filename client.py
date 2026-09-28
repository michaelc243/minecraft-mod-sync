import ctypes
import msvcrt
import os
import sys
from typing import Type, Any
import requests
import keyboard
from time import sleep
import json
import tkinter as tk
from tkinter import filedialog
from bs4 import BeautifulSoup
import ipaddress
from urllib.parse import unquote
from colorama import Fore
# from tqdm import tqdm


# class AppMutex:
#     from socket import socket, AF_INET, SOCK_DGRAM
#     # ^^put in imports
#     """
#     Class serves as single instance mutex handler (My application can be run only once).
#     It uses OS default property where single UDP port can be bind only once at time.
#     """
#
#     sock = None
#     @staticmethod
#     def enable():
#         """
#         By calling this you bind UDP connection on specified port.
#         If binding fails then port is already opened from somewhere else.
#         """
#
#         try:
#             AppMutex.sock = socket(AF_INET, SOCK_DGRAM)  # UDP
#             AppMutex.sock.bind(("127.0.0.1", 40000))
#         except OSError:
#             ctypes.windll.user32.MessageBoxW(0, "Minecraft Server Mod Sync is already running.", "Error", 0x30)
#             raise Exception("Application can be run only once.")


def updateJSONData(key: str, data: Any) -> None:
    """
    Updates the JSON data file with the given key and data.

    :param key: The key to update in the JSON file.
    :type key: str
    :param data: The data to update in the JSON file.
    :type data: Any

    :return: None
    """
    if not os.path.exists("data.json"):
        f = open("data.json", 'w')
        f.close()   # create empty file
    with open("data.json", "r") as jsonFile:
        try:
            jsonData: dict = json.load(jsonFile)
        except json.decoder.JSONDecodeError:
            jsonData: dict = {}
    jsonData[key] = data
    with open("data.json", "w") as jsonFile:
        json.dump(jsonData, jsonFile)


def readJSONData(key: str) -> str:
    """
    Reads the JSON data file and returns the value for the given key.

    :param key: The key to read from the JSON file.
    :type key: str

    :return: key: str
        The value for the given key in the JSON file.
    """
    with open("data.json", "r") as jsonFile:
        data: str = json.load(jsonFile)[key]
        return data

serverAddress: str
def setServerAddress(mode: str) -> None:
    """
    Sets the server address.

    :param mode: The mode to set the server address in. Can be 'change' or 'set'.
    :type mode: str

    :return: None
    """
    global serverAddress
    if mode == 'change':
        print("\n[Change Server Address]\n")
    if mode == 'set':
        print("\n[Set Server Address]\n")
    while True:
        keyboard.write(serverAddress)
        bufferServerAddress: str = input("Server Address: ")
        if bufferServerAddress == "" or bufferServerAddress.isspace():
            if mode == 'change':
                break   # continue if we are setting the var because we dont want an empty var
        try:
            ipaddress.ip_address(bufferServerAddress)   # check if its a valid IP, only here to raise a ValueError
            serverAddress = bufferServerAddress
            updateJSONData('serverAddress', serverAddress)
            break
        except ValueError:
            print("Invalid IP Address. Try again")

serverPort: str
def setServerPort(mode: str) -> None:
    """
    Sets the server port.

    :param mode: The mode to set the server address in. Can be 'change' or 'set'.
    :type mode: str

    :return: None
    """
    global serverPort
    if mode == 'change':
        print("\n[Change Server Port]\n")
    if mode == 'set':
        print("\n[Set Server Port]\n")
    while True:
        keyboard.write(serverPort)
        bufferServerPort: str = input("Server Port: ")
        if bufferServerPort == "" or bufferServerPort.isspace():
            if mode == 'change':
                break
        try:
            serverPort = bufferServerPort
            if 65535 >= int(serverPort) >= 1:
                updateJSONData('serverPort', serverPort)
                break
            else:
                print("Port must be an integer between 1-65535. Try again.")
        except ValueError:
            print("Port must be an integer between 1-65535. Try again.")

minecraftVersion: str
def setMinecraftVersion(mode: str, inputStyle: str) -> None:
    """
    Sets the Minecraft server version.

    :param mode: The mode to set the server address in. Can be 'change' or 'set'.
    :type mode: str

    :param inputStyle: The input style to use. Can be 'text' or 'choice'.
    :type inputStyle: str

    :return: None
    """
    global minecraftVersion
    if mode == 'change':
        print("\n[Change Server Version]\n")
    if mode == 'set':
        print("\n[Set Server Version]\n")
    if inputStyle == 'text' or setMinecraftVersionTextEnabled:
        while True:
            # Autofill stored value
            keyboard.write(minecraftVersion)
            # Get user input
            bufferMinecraftVersion: str = input("Server Version: ")
            if bufferMinecraftVersion == "" or bufferMinecraftVersion.isspace():
                # If the mode is 'change' we already have a value for minecraftVersion
                if mode == 'change':
                    break
                # If the mode is 'set' we dont have a value for minecraftVersion
                elif mode == 'set':
                    print("Please enter a server version.\n")
            # Check for prohibited characters
            if '/' in bufferMinecraftVersion:
                print('Prohibited character "/". Try again.\n')
            elif '\\' in bufferMinecraftVersion:
                print('Prohibited character "\\". Try again.\n')
            # Check if the version exists
            elif requests.get(f'http://{serverAddress}:{serverPort}/{bufferMinecraftVersion}/').status_code == 404:
                print("Invalid version. Please try again.\n")   # . and .. pass the check, FIX LATER
            # If all checks pass, update minecraftVersion
            else:
                minecraftVersion = bufferMinecraftVersion
                updateJSONData('minecraftVersion', minecraftVersion)
                break
    elif inputStyle == 'choice':
        baseURL = f"http://{serverAddress}:{serverPort}/"
        availableVersionURLS: list[str] = getHTTPDirectoryListing(f"http://{serverAddress}:{serverPort}/", '/')
        if availableVersionURLS != ConnectionError:
            availableVersionsWithSlash: list[str] = [item.replace(baseURL, '') for item in availableVersionURLS]
            availableVersions: list[str] = [version.replace('/', '') for version in availableVersionsWithSlash]
            leave = False
            while not leave:
                print('\n'.join(f"[{i}] {version}" for i, version in enumerate(availableVersions, start=1)))
                print("\n\n    [9] Back     [0] Quit")
                keyPress: str = getKeyboardInput()
                for i, version in enumerate(availableVersions, start=1):
                    if keyPress == str(i):
                        leave = True    # let us leave the while loop
                        minecraftVersion = version
                        updateJSONData('minecraftVersion', minecraftVersion)
                        break    # break for loop
                    elif keyPress == '9':
                        break
                    elif keyPress == '0':
                        raise SystemExit()


modsFolder: str
def setModsFolder(mode: str) -> None:
    """
    Sets the mods folder path.

    :param mode: The mode to set the mods folder in. Can be 'change' or 'set'.

    :return: None
    """
    global modsFolder
    if mode == 'change':
        print("\n[Change Mods Folder]\n")
    if mode == 'set':
        print("\n[Set Mods Folder]\n")
    root = tk.Tk()
    root.withdraw()
    # root.iconbitmap(fr"{programPath}icon.ico")
    inputDirectory: str = filedialog.askdirectory(title='Choose mods folder path')
    root.destroy()
    if inputDirectory == '""':
        if mode == 'set':
            print("You need to specify a mod folder. Program will close in 3...")
            sleep(3)
            raise SystemExit()
    else:
        modsFolder = inputDirectory
        updateJSONData('modsFolder', inputDirectory)


def mainScreen() -> None:
    """
    Displays the main screen of the Minecraft Server Mod Sync application.

    :return: None
    """
    os.system("cls")
    print(f"""

    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
    |Minecraft Server Mod Sync|
    ___________________________


    Server Address: {serverAddress}

    Server Port: {serverPort}

    Minecraft Version: {minecraftVersion}

    Mods Folder: {modsFolder}


    [1] Sync Mods

    [2] View Host List

    [3] View Client List

    [4] Configuration


    [0] Quit
    """)
    while True:
        match getKeyboardInput():
            case '1':
                hostClientSyncMenu(); break
            case '2':
                hostListMenu(); break
            case '3':
                clientListMenu(); break
            case '4':
                configurationMenu(); break
            case '0':
                raise SystemExit()
            case _:
                print("Invalid key...")
        # We break after the menu is done with because it asks for its own keyboard input,
        # so once we press 9 to go back, we want to leave the loop of the first keyboard check
        # and end up with mainScreen() finishing


def hostClientSyncMenu() -> None:
    """
    Displays the host client sync menu.

    :return: None
    """
    os.system("cls")
    print("\n[Sync Mods]\n")
    missingMods: list = hostClientSync()
    if missingMods:
        if missingMods != ConnectionError:
            print("\n".join(
                f"{Fore.LIGHTBLACK_EX}┌{Fore.RESET}{missingMods[0]}" if i == 0 else f"{Fore.LIGHTBLACK_EX}│{Fore.RESET}{item}"
                for i, item in enumerate(missingMods)))
            print(f"{Fore.LIGHTBLACK_EX}│\n└{Fore.RESET}{len(missingMods)} mods available for download.")
            print("\n\n    [1] Download     [9] Back     [0] Quit")
            while True:
                match getKeyboardInput():
                    case '1':
                        downloadModsMenu(missingMods)
                        break
                    case '9':
                        break
                    case '0':
                        raise SystemExit()
                    case _:
                        print("Invalid key...")
    else:
        print("0 mods available for download.")
    backQuitOptions()


def hostListMenu() -> None:
    """
    Displays the host list menu.

    :return: None
    """
    os.system("cls")
    print("\n[View Host List]\n")
    base_url: str = f"http://{serverAddress}:{serverPort}/{minecraftVersion}/"
    hostList: list[str] = getHTTPDirectoryListing(f"{base_url}", 'jar')
    if hostList:
        if hostList != ConnectionError:
            clean_hostList: list[str] = [item.replace(base_url, '') for item in hostList]
            print("\n".join(
                f"{Fore.LIGHTBLACK_EX}┌{Fore.RESET}{clean_hostList[0]}" if i == 0 else f"{Fore.LIGHTBLACK_EX}│{Fore.RESET}{item}"
                for i, item in enumerate(clean_hostList)))
            print(f"{Fore.LIGHTBLACK_EX}│\n└{Fore.RESET}{len(hostList)} Mods Installed")
    else:
        print(" No mods installed.")

    backQuitOptions()


def clientListMenu() -> None:
    """
    Displays the client list menu.

    :return: None
    """
    os.system("cls")
    print("\n[View Client List]\n")

    try:
        localList: list[str] = [x for x in os.listdir(modsFolder) if '.jar' in x]
        if localList:
            for i, item in enumerate(localList):
                if i != 0:
                    print(f"{Fore.LIGHTBLACK_EX}│{Fore.RESET}{item}")
                elif i == 0:
                    print(f"{Fore.LIGHTBLACK_EX}┌{Fore.RESET}{item}")

            print(f"{Fore.LIGHTBLACK_EX}│\n"
                  f"└{Fore.RESET}{len(localList)} Mods Installed")
        else:
            print("0 mods installed.")
    except FileNotFoundError:
        print("Invalid path.")

    backQuitOptions()


def configurationMenu() -> None:
    """
    Displays the configuration menu.

    :return: None
    """
    os.system("cls")
    print("""

    [Configuration]

    [1] Change Server Address

    [2] Change Server Port

    [3] Change Server Version

    [4] Change Mods Folder


    [9] Back     [0] Quit
    """)
    while True:
        match getKeyboardInput():
            case '1':
                os.system("cls")
                setServerAddress('change')
                break
            case '2':
                os.system("cls")
                setServerPort('change')
                break
            case '3':
                os.system("cls")
                setMinecraftVersion('change', 'choice')
                break
            case '4':
                os.system("cls")
                setModsFolder('change')
                break
            case '9':
                break
            case '0':
                raise SystemExit()
            case _:
                print("Invalid key...")


def hostClientSync() -> list[str] | Type[ConnectionError] | Type[FileNotFoundError]:
    """
    Compares the local mods folder with the server's mods folder and returns a list of missing mods.

    :return: list[str]: A list of missing mods. If a ConnectionError occurs, returns ConnectionError.
    """
    # Get the list of local mods
    try:
        localList: list[str] = [x for x in os.listdir(modsFolder) if '.jar' in x]
    except FileNotFoundError:
        localList: list[str] = []


    # Get the list of mods from the server
    hostList: list[str] | Type[ConnectionError] = getHTTPDirectoryListing(
        f"http://{serverAddress}:{serverPort}/{minecraftVersion}/", 'jar')

    # If a ConnectionError occurs, return it
    if hostList == ConnectionError:
        return ConnectionError

    # Clean the host list by removing the server URL
    cleanHostList: list[str] = [x.replace(f"http://{serverAddress}:{serverPort}/{minecraftVersion}/", "") for x in
                                hostList]

    # Find the missing mods by comparing the local list with the clean host list
    missingMods: list[str] = [x for x in cleanHostList if x not in localList]

    return missingMods


def downloadModsMenu(missingMods: list[str]) -> None:
    """
    Downloads the mods that are missing from the client folder.

    :param missingMods: A list of mods missing from the client folder.
    :type missingMods: list[str]

    :return: None
    """
    # Clear the console and print header
    os.system("cls")
    print("\n[Sync Mods]\n")

    # Download the missing mods
    downloadMods(missingMods)

    # No need to call backQuitOptions() here because it's handled in hostClientSyncMenu()


def getHTTPDirectoryListing(url: str, ext: str) -> list[str] | Type[ConnectionError] | None:
    """
    Retrieves the directory listing from the server.

    :param url: The URL of the server.
    :type url: str
    :param ext: The file extension to filter by.
    :type ext: str

    :return: list[str]: A list of URLs of files with the specified extension. If a ConnectionError occurs, returns ConnectionError. If no files are found, returns None.
    """
    # Print a message to indicate that the program is connecting to the server
    print("    Connecting to server...", end="", flush=True)

    try:
        # Send a GET request to the server
        response = requests.get(url)

        # If the response is OK, parse the HTML
        if response.ok:
            response_text = response.text
        else:
            # If the response is not OK, raise an exception
            return response.raise_for_status()

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response_text, 'html.parser')

        # Find all links with the specified extension
        result: list[str] = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

        # Unquote the URLs
        unpercent_result: list[str] = [unquote(x) for x in result]

        # Print a message to indicate that the connection is successful
        print('\r                            ', end="\r")

        return unpercent_result

    except requests.exceptions.ConnectionError:
        # If a ConnectionError occurs, print an error message and return ConnectionError
        print('\r                            ', end="\r")
        print("    Unable to connect to server. Try again later.")
        return ConnectionError


def downloadMods(missingMods: list) -> None:
    """
    Download from the server the missing mods.

    :param missingMods: list: The list of mods missing from the client folder.

    :return: None
    """
    for modName in missingMods:
        print(f"    Downloading {modName}...", flush=True)
        response = requests.get(f"http://{serverAddress}:{serverPort}/{minecraftVersion}/" + modName, stream=True)
        with open(f"{modsFolder}/{modName}", 'wb') as handle:
            # for data in tqdm(response.iter_content(chunk_size=1024*1024), desc=f"Downloading {modName}", unit="B", unit_scale=True, unit_divisor=1024*1024):
            for data in response.iter_content(chunk_size=1024*1024):    # 1 MB
                handle.write(data)


def getKeyboardInput() -> str:
    """
    Wait for a key to be pressed and return it in utf-8 format.

    :return: str: The pressed key in utf-8 format.
    """
    while True:
        return msvcrt.getch().decode('utf-8')


def backQuitOptions() -> None:
    """
    Display back and quit options and handle user input.

    :return: None
    """
    print("\n\n    [9] Back     [0] Quit")
    while True:
        match getKeyboardInput():
            case '9':
                break
            case '0':
                raise SystemExit()
            case _:
                print("Invalid key...")


def get_console_pid() -> int | None:
    """
    Get the process ID of the current console window.

    :return:
        int | None: The process ID of the current console window, or None if no console window is found.
    """
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    console_handle = kernel32.GetConsoleWindow()
    if console_handle == 0:
        return None

    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(console_handle, ctypes.byref(pid))
    return pid.value


if __name__ == "__main__":
    os.system("title Minecraft Server Mod Sync")
    # AppMutex.enable()

    helpArgs = ['-h', '--help', '-?']
    try:
        if sys.argv[1] in helpArgs:
            print("Usage: python main.py [OPTION]...\n Args: --setMinecraftVersionTextEnabled")
            raise SystemExit()
        if sys.argv[1] == '--setMinecraftVersionTextEnabled':
            setMinecraftVersionTextEnabled = True
    except IndexError:
        setMinecraftVersionTextEnabled = False

    try:
        serverAddress: str = readJSONData('serverAddress')
    except (KeyError, FileNotFoundError):
        serverAddress = ''
        setServerAddress('set')

    try:
        serverPort: str = readJSONData('serverPort')
    except (KeyError, FileNotFoundError):
        serverPort = ''
        setServerPort('set')

    try:
        minecraftVersion: str = readJSONData('minecraftVersion')
    except (KeyError, FileNotFoundError):
        minecraftVersion = ''
        setMinecraftVersion('set', 'choice')

    try:
        modsFolder: str = readJSONData('modsFolder')
    except (KeyError, FileNotFoundError):
        modsFolder = ''
        setModsFolder('set')
    while True:
        mainScreen()
