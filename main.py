import socket
import select
import time
from threading import Thread, Event

# Logging Imports
import logging
from logging.config import fileConfig
import traceback
import colorlog

# Global Imports
from config import plug, plugstates, toggleclients

# Rest Server Imports
from _initRestApi import create_app
import uvicorn

fileConfig('logging.ini')

class CustomFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        levelname_color = self.log_colors.get(record.levelname, 'white')
        message_color = self.secondary_log_colors.get('message', {}).get(record.levelname, 'white')
        asctime_color = self.secondary_log_colors.get('asctime', {}).get(record.levelname, 'white')

        record.log_color = colorlog.escape_codes.escape_codes[levelname_color]
        record.message_color = colorlog.escape_codes.escape_codes[message_color]
        record.asctime_color = colorlog.escape_codes.escape_codes[asctime_color]

        return super().format(record)

handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter(
    fmt='%(log_color)s[%(levelname)s]%(reset)s %(asctime_color)s[%(asctime)s]%(reset)s %(message_color)s%(message)s%(reset)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'green',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    },
    secondary_log_colors={
        'message': {
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white'
        },
        'asctime': {
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white'
        }
    }
))

# Add the color handler to the root logger
logging.getLogger().addHandler(handler)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 1821))  # Server, which redirects the plug to the runtime server
s.listen()

t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
t.bind(("", 1822))  # Runtime Server
t.setblocking(0)    # Must be non-blocking or hangs waiting for keepalive to perform toggle
t.listen()

def plughandler(socket,retAddr): # Runtime Control Thread
	# Add the color handler to the root logger
	logging.getLogger().addHandler(handler)

	flag = True
	socket.setblocking(1)
	logging.debug("retAddr: "+str(retAddr))
	if retAddr[0] not in plugstates:
		plugstates[retAddr[0]] = plug(ip=retAddr[0],name=retAddr[0],retAdr=retAddr[1],state=-1) # Add new plug to Dict
	try:
		data=socket.recv(1024) # Initial Plug Runtime Setup  
		reply=bytes.fromhex("24000300001a001d0000000000000000000700010000080001000009000100000a00020064000b000400015180")
		socket.sendall(reply)
		data=socket.recv(1024)
		logging.info(f"Handled Plug: {str(retAddr)}")
		while socket:
			# try:
			r,w,x = select.select([socket],[],[],1) # Wait for incoming data for 1s, else do toggle check
			if len(r) > 0 :
				lpkt=time.time()
				data = socket.recv(1024)
			if data :
				if data[5] == 101 : #0x65
					#print("Sent KA to Plug "+str(retAddr)+" at "+str(int(time.time()))+"!")
					reply=bytes.fromhex("24000300006600000000000000000000")
					socket.sendall(reply)
				if data[5] == 102 : #0x66
					if len(data) == 60:
						logging.info("Update Plug {retAddr}'s State: "+str(chr(data[58]))+" at "+str(int(time.time()))+"!")
						logging.debug(f"Plug: {str(retAddr)}")
						plugstates[retAddr[0]].state = int(chr(data[58]))
						# plugstates.update({retAddr:str(chr(data[58]))}) # Update Plug State in Dict
			
			if retAddr in toggleclients : # Toggle command pending for this plug
				reply=bytes.fromhex("24000300015d000c000000005f0c00007b22616374696f6e223a317d")
				socket.sendall(reply)
				toggleclients.remove(retAddr)
			
			if time.localtime().tm_hour == 18 and time.localtime().tm_min == 30 and flag:
				reply=bytes.fromhex("24000300015d000c000000005f0c00007b22616374696f6e223a317d")
				socket.sendall(reply)
				flag = False

		
			if time.localtime().tm_hour == 22 and not flag:
				reply=bytes.fromhex("24000300015d000c000000005f0c00007b22616374696f6e223a317d")
				socket.sendall(reply)
				flag = True
			# if time.localtime().tm_hour  
		
			if time.time() > lpkt+101 : # KA interval 98 secs
				# print("Timeout waiting for keepalive from Plug "+str(retAddr)+" at "+str(int(time.time()))+"!")
				raise Exception("Lost Connection")   
			# except socket.error as e:
			#   if e[0] == 10035 and socketerror10035count < 5:
			#     socketerror10035count = socketerror10035count  +1
			#     time.sleep(1)
			#   else: 
			#     break
	except Exception as e:
		logging.warning(f"Lost Connection with Plug: {str(retAddr)}")
		logging.warning(f"{traceback.format_exc()}")

		plugstates.pop(retAddr[0],None) # Remove dead plug from Dict
		while retAddr in toggleclients :
			toggleclients.remove(retAddr)
		socket.close()

def plugredirector(socket,retAddr):
	# Add the color handler to the root logger
	logging.getLogger().addHandler(handler)

	socket.recv(1024)
	logging.info(f"Redirected Plug ({str(retAddr)}")
	reply=bytes.fromhex("2400020000d2000e000000000000000000100004c0a8017300110002071e") #Send Plug to Target (192.168.1.115:1822)

	# Format of Reply
	# 2400020000d2000e000000000000000000100004 c0a85014 00110002 071e
	#                                          IPAddress         Port

	socket.sendall(reply)
	socket.close()

stop_threads = Event()

def main_beli():
	logging.info("Tenda Beli SP3 Simple Plug Server by Gough Lui (goughlui.com) modified by J.C. Started!")
	logging.info("Modifications v5.3")
	while not stop_threads.is_set(): # Main Loop
		r,w,x = select.select([s,t],[],[]) # Whatever socket has data
		for v in r :
			if v is s :
				socket, retAddr = s.accept()
				Thread(target=plugredirector,args=(socket,retAddr)).start()
			elif v is t :
				socket, retAddr = t.accept()
				Thread(target=plughandler,args=(socket,retAddr)).start()

app = create_app()

def main_rest():
	from uvicorn.config import LOGGING_CONFIG
	
	# Remove the default Console Handlers
	# uvicorn_log_config = uvicorn.LOGGING_CONFIG
	for key in list(LOGGING_CONFIG["loggers"].keys()):
		del LOGGING_CONFIG["loggers"][key]
	
	# for key in list(uvicorn_log_config["handlers"].keys()):
	# 	del uvicorn_log_config["handlers"][key]

	# for h in logging.getLogger().handlers[:]:
	# 	logging.getLogger().removeHandler(h)

	# Add the color handler to the root logger
	logging.getLogger().addHandler(handler)

	# Start Uvicorn Server
	while not stop_threads.is_set():
		uvicorn.run(app, port=6789, host="0.0.0.0", log_config="logging.ini")


if __name__ == "__main__":
	# try:
	logging.warning("This server communicates via HTTP with no authentication.\n It is not secure and should not be used on a network which may be accessed by untrusted parties.")
	t1 = Thread(target=main_rest)
	t2 = Thread(target=main_beli)
	t1.start()
	t2.start()
	# except KeyboardInterrupt:
	#     stop_threads.set()
	#     t1.join()
	#     t2.join()

	
	
