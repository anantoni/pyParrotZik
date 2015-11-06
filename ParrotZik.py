#!/usr/bin/env python

import sys

if sys.platform == "darwin":
    import lightblue
else:
    import bluetooth

import ParrotProtocol
import struct
from BeautifulSoup import BeautifulSoup


class ParrotZik(object):
    def __init__(self, addr=None):
        uuid = "0ef0f502-f0ee-46c9-986c-54ed027807fb"

        if sys.platform == "darwin":
            service_matches = lightblue.findservices(name="Parrot RFcomm service", addr=addr)
        else:
            service_matches = bluetooth.find_service(uuid=uuid, address=addr)

        if len(service_matches) == 0:
            print "Failed to find Parrot Zik RFCOMM service"
            self.sock = ""
            return

        if sys.platform == "darwin":
            first_match = service_matches[0]
            port = first_match[1]
            name = first_match[2]
            host = first_match[0]
        else:
            first_match = service_matches[0]
            port = first_match["port"]
            name = first_match["name"]
            host = first_match["host"]

        print "Connecting to \"%s\" on %s" % (name, host)

        if sys.platform == "darwin":
            self.sock = lightblue.socket()
        else:
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.connect((host, port))

        self.sock.send('\x00\x03\x00')
        data = self.sock.recv(1024)

        self.BatteryLevel = 100
        self.BatteryCharging = False
        print "Connected"

    def get_battery_state(self):
        data = self.send_get_message("/api/system/battery/get")
        return data.answer.system.battery["state"]

    def get_battery_level(self):
        data = self.send_get_message("/api/system/battery/get")
        try:
            if data.answer.system.battery["level"] <> '':
                self.BatteryLevel = data.answer.system.battery["level"]
            if data.answer.system.battery["state"] == 'charging':
                self.BatteryCharging = True
            else:
                self.BatteryCharging = False
        except:
            pass

        try:
            print "notification received" + data.notify["path"]
        except:
            pass

        return self.BatteryLevel

    def get_version(self):
        data = self.send_get_message("/api/software/version/get")
        return data.answer.software["version"]

    def get_friendly_name(self):
        data = self.send_get_message("/api/bluetooth/friendlyname/get")
        return data.answer.bluetooth["friendlyname"]

    def get_auto_connection(self):
        data = self.send_get_message("/api/system/auto_connection/enabled/get")
        return data.answer.system.auto_connection["enabled"]

    def set_auto_connection(self, arg):
        data = self.send_set_message("/api/system/auto_connection/enabled/set", arg)
        return data

    def get_anc_phone_mode(self):
        data = self.send_get_message("/api/system/anc_phone_mode/enabled/get")
        return data.answer.system.anc_phone_mode["enabled"]

    def get_noise_cancel(self):
        data = self.send_get_message("/api/audio/noise_cancellation/enabled/get")
        return data.answer.audio.noise_cancellation["enabled"]

    def set_noise_cancel(self, arg):
        data = self.send_set_message("/api/audio/noise_cancellation/enabled/set", arg)
        return data

    def get_lou_reed_mode(self):
        data = self.send_get_message("/api/audio/specific_mode/enabled/get")
        return data.answer.audio.specific_mode["enabled"]

    def set_lou_reed_mode(self, arg):
        data = self.send_set_message("/api/audio/specific_mode/enabled/set", arg)
        return data

    def get_parrot_concert_hall(self):
        data = self.send_get_message("/api/audio/sound_effect/enabled/get")
        return data.answer.audio.sound_effect["enabled"]

    def set_parrot_concert_hall(self, arg):
        data = self.send_set_message("/api/audio/sound_effect/enabled/set", arg)
        return data

    def send_get_message(self, message):
        message = ParrotProtocol.get_request(message)
        return self.send_message(message)

    def send_set_message(self, message, arg):
        message = ParrotProtocol.set_request(message, arg)
        return self.send_message(message)

    def send_message(self, message):
        try:
            self.sock.send(str(message))
        except:
            self.sock = ""
            return
        if sys.platform == "darwin":
            data = self.sock.recv(30)
        else:
            data = self.sock.recv(7)
        data = self.sock.recv(1024)
        data = BeautifulSoup(data)
        return data

    def close(self):
        self.sock.close()
