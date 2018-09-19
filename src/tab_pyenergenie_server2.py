#!/usr/bin/python
import time
import energenie
import sys
import os
import threading
import RPi.GPIO as GPIO
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from httplib2 import Http
import traceback

from energenie import OpenThings
from energenie import Devices


class PIRCallback:
	def __init__(self,sensor):
		self.sensor=sensor
		
	def onMotion(self,sensor,on):
		if on:
			http_obj = Http( disable_ssl_certificate_validation=True )
			resp, content = http_obj.request(
				uri="https://192.168.1.1:8443/polestar/scripts/webhook/90697B320A017A92",
				method='POST',
				body=self.sensor
			)
			
class Radiator:
	def __init__(self,radiator,name):
		self.radiator=radiator
		self.name=name		
	def get_ambient_temperature(self):
		t=self.radiator.get_ambient_temperature()	
		if t==None:
			t=0.0
		return t
	def get_battery_voltage(self):
		v=self.radiator.get_battery_voltage()
		if v==None:
			v=0.0
		return v
	def get_diagnostics(self):
		d=self.radiator.get_diagnostics()
		if d==None:
			d=-1
		return d	
	def toXMLString(self):
		try:
			now=time.time()
			return "<{} temp='{:.2f}' voltage='{:.2f}' diag='{}' age='{:.0f}'/>".format(
				self.name,
				self.get_ambient_temperature(),
				self.get_battery_voltage(),
				self.get_diagnostics(),
				now-self.radiator.lastHandledMessage,
				)
		except:
			print traceback.print_exc()
			return "<{}/>".format(self.name);	

class EnergyMonitor:
	def __init__(self,monitor,name,
		dutyCycleThreshold=100,
		averageSamples=360, # 60 mins
		dutyCycleFilterFactor=0.5
		):
		self.name=name
		self.dutyCycleThreshold=dutyCycleThreshold
		self.powerReadingsSize=averageSamples
		self.dutyCycleFilterFactor=dutyCycleFilterFactor
		
		self.monitor=monitor
		self.powerReadings = [-1 for i in range(0,self.powerReadingsSize)]
		self.powerReadingsIndex=0
		self.avgPower=0.0;
		self.dutyCycle=0.0
		
		self.dutyCycle2=-1
		self.lastTransitionTime=None;
		self.lastPowerAboveDuty=None;
		self.lastDurationBelow=None;
		self.lastDurationAbove=None;

	def poll(self):
		realPower=self.monitor.get_readings().real_power
		self.powerReadings[self.powerReadingsIndex]=realPower
		self.powerReadingsIndex=(self.powerReadingsIndex+1)%self.powerReadingsSize
		
		#calculate duty cycle
		powerAboveDuty=realPower>self.dutyCycleThreshold
		if self.lastPowerAboveDuty!=None:
			now=time.time()
			if powerAboveDuty!=self.lastPowerAboveDuty:
				if self.lastTransitionTime!=None:
					if powerAboveDuty:
						self.lastDurationBelow=now-self.lastTransitionTime
					else:
						self.lastDurationAbove=now-self.lastTransitionTime
				self.lastTransitionTime=now
				if self.lastDurationBelow!=None and self.lastDurationAbove!=None:
					self.updateDuty()
			# enhancement to more rapidly adapt to changes in duty	
			if self.lastDurationBelow!=None and self.lastDurationAbove!=None:
				duration=now-self.lastTransitionTime
				if powerAboveDuty and duration>self.lastDurationAbove:
					self.lastDurationAbove=duration
					self.updateDuty()
				if (not powerAboveDuty) and duration>self.lastDurationBelow:
					self.lastDurationBelow=duration
					self.updateDuty()
		self.lastPowerAboveDuty=powerAboveDuty
			
	def updateDuty(self):
		dutyCycle=float(self.lastDurationAbove)/float(self.lastDurationAbove+self.lastDurationBelow)
		if self.dutyCycle2<0:
			self.dutyCycle2=dutyCycle
		else:
			self.dutyCycle2=dutyCycle*self.dutyCycleFilterFactor+self.dutyCycle2*(1-self.dutyCycleFilterFactor)
		
	def updateAverage(self):
		totalPower=0.0
		count=0
		heaterOn=0.0
		for power in self.powerReadings:
			if power>=0:
				totalPower+=power
				count=count+1
				if power>self.dutyCycleThreshold:
					heaterOn=heaterOn+1.0
		if count>0:
			self.avgPower=totalPower/float(count)	
			self.dutyCycle=heaterOn/float(count)
	def toXMLString(self):
		try:
			productId=self.monitor.product_id
			if productId==Devices.PRODUCTID_MIHO005:
				extra="switchState='{}'".format(self.monitor.is_on());
			else:
				extra=""
			now=time.time()
		
			return "<{} power='{}' avgPower='{:.2f}' dutyCycle='{:.2f}' dutyCycle2='{:.2f}' volt='{}' freq='{:.2f}' age='{:.0f}' {}/>".format(
				self.name,
				self.monitor.get_readings().real_power,
				self.avgPower,
				self.dutyCycle,
				self.dutyCycle2,
				self.monitor.get_voltage(),
				self.monitor.get_frequency(),
				now-self.monitor.lastHandledMessage,
				extra
				)
		except:
			print traceback.print_exc()
			return "<{}/>".format(self.name);
		
class Main:
	
	def __init__(self,energenie):
		self.energenie=energenie

		self.kitchenPIR = energenie.registry.get("MIHO032_kitchen");
		self.kitchenPIR.setCallback(PIRCallback("urn:motion:energenie1").onMotion)
		self.loungePIR = energenie.registry.get("MIHO032_lounge");
		self.loungePIR.setCallback(PIRCallback("urn:motion:energenie2").onMotion)

		self.rad1 = Radiator(energenie.registry.get("MIHO013_rad1"),"MIHO013_rad1")
		self.rad2 = Radiator(energenie.registry.get("MIHO013_rad2"),"MIHO013_rad2")
		self.rad3 = Radiator(energenie.registry.get("MIHO013_rad3"),"MIHO013_rad3")
		self.rad4 = Radiator(energenie.registry.get("MIHO013_rad4"),"MIHO013_rad4")
		
		self.aquarium = EnergyMonitor(energenie.registry.get("MIHO004_aquarium"),"MIHO004_aquarium")
		self.deskLight = EnergyMonitor(energenie.registry.get("MIHO004_desklamp"),"MIHO004_fridge",
			dutyCycleThreshold=40, averageSamples=1440) # 4 hours
		self.freezer = EnergyMonitor(energenie.registry.get("MIHO004_freezer"),"MIHO004_freezer",
			dutyCycleThreshold=50, averageSamples=1440) # 4hours
		#self.miho005 = EnergyMonitor(energenie.registry.get("MIHO005_something"),"MIHO005_something",
		#	dutyCycleThreshold=20)
		
			

	def loop(self):
		print "sleeping to allowing readings first"
		self.energenie.loop(receive_time=10)
		print "ok looping"
	
		global stopEnergenie
		lastTime=time.time()
		while not(stopEnergenie):
			self.energenie.loop(receive_time=10)
			
			now=time.time()
			if now-lastTime>=10:
				lastTime=now
				self.aquarium.poll()
				self.deskLight.poll()
				self.freezer.poll()
				#self.miho005.poll()
			
		stopEnergenie=False
			
	def getData(self):
		self.aquarium.updateAverage()
		self.deskLight.updateAverage()
		self.freezer.updateAverage()
		
		data="<data>"
		data+=self.deskLight.toXMLString()
		data+=self.aquarium.toXMLString()
		data+=self.freezer.toXMLString()
		#data+=self.miho005.toXMLString()
		
		data+=self.rad1.toXMLString()
		data+=self.rad2.toXMLString()
		data+=self.rad3.toXMLString()
		data+=self.rad4.toXMLString()
		data+="</data>"
		return data
		
	def getRadiator(self,radNum):
		if radNum=="1":
			rad=self.rad1.radiator
		elif radNum=="2":
			rad=self.rad2.radiator
		elif radNum=="3":
			rad=self.rad3.radiator
		elif radNum=="4":
			rad=self.rad4.radiator
		else:
			rad=None
		return rad

	def onSetRadiator(self,radNum, temp):
		rad=self.getRadiator(radNum)	
		if rad!=None:
			rad.enable_thermostat()
			rad.set_setpoint_temperature(temp)
	
		return "<div>setRadiator {:s} {:f}</div>".format(rad,temp)
	
	def onSetRadiatorValve(self,radNum, onOff):
		rad=self.getRadiator(radNum)	
		if rad!=None:
			if onOff=="on":
				rad.turn_on()
			elif onOff=="off":
				rad.turn_off()
			elif onOff=="thermostatic":
				rad.enable_thermostat()
			elif onOff=="identify":
				rad.set_identify()
		return "<div>setRadiatorValve {:s} {:s}</div>".format(rad,onOff)
	
	def setLegacySwitch(self,house, device, onOff):
		print house, device, onOff
		socket = energenie.Devices.ENER002((house, device))
		if (onOff=='on'):
			socket.turn_on()
		else:
			socket.turn_off()
		return "<div>setLegacySwitch {} {} {}</div>".format(house,device,onOff)
	
		
	
class HTTPHandler(BaseHTTPRequestHandler):
	global m
	
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/xml')
		self.end_headers()
		self.wfile.write(self.onGet(self.path));

	def do_HEAD(self):
		self._set_headers()
		
	def do_POST(self):
		# Doesn't do anything with posted data
		self._set_headers()
		self.wfile.write("<html><body><h1>POST!</h1></body></html>")
		
	def onGet( self, path ):
		if (path=="/data"):
			#sys.exit(0)
			result=m.getData()
		elif path.startswith("/setRadiator/"):
			tokens=path.split("/")
			result=m.onSetRadiator(tokens[2],float(tokens[3]))
		elif path.startswith("/setRadiatorValve/"):
			tokens=path.split("/")
			result=m.onSetRadiatorValve(tokens[2],tokens[3])  
		elif path.startswith("/setLegacySwitch/"):
			tokens=path.split("/")
			result=m.setLegacySwitch(int(tokens[2]),int(tokens[3]),tokens[4])               
		else:
			result="<html><body><h1>{0}</h1></body></html>".format(path)
		return result;    
  	
def cleanupGPIO():
	GPIO.setmode(GPIO.BCM)

	GPIO.setup(27, GPIO.IN) # Green LED
	GPIO.setup(22, GPIO.IN) # Red LED
	GPIO.setup(7, GPIO.IN)  # CS
	GPIO.setup(8, GPIO.IN)  # CS
	GPIO.setup(11, GPIO.IN) # SCLK
	GPIO.setup(10, GPIO.IN) # MOSI
	GPIO.setup(9, GPIO.IN)  # MISO
	GPIO.setup(25, GPIO.IN) # RESET

	GPIO.cleanup()
	
	

try:
	stopEnergenie=False
	scriptDir=os.path.dirname(os.path.realpath(sys.argv[0]))
	os.chdir(scriptDir)
	energenie.init()
	m=Main(energenie)
	p = threading.Thread(target=m.loop)
	p.daemon = True
	p.start()

	httpd = HTTPServer(('', 8082), HTTPHandler)
	print 'Starting httpd...'
	httpd.serve_forever()
except:
	stopEnergenie=True
	print traceback.print_exc()
	raise
finally:
	stopEnergenie=True
	c=0
	while c<10:
		time.sleep(0.25)
		c=c+1
	energenie.finished()
	cleanupGPIO()
	print "finished"		