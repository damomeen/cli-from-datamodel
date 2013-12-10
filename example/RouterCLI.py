#!/usr/bin/python

import copy
import traceback
import os
import sys
import struct
import socket
import logging

sys.path.append(os.getcwd()+"/../")
from defaultCmd import DefaultCmd, configureLogger, clearedDictValues
del sys.path[-1]

import testingData

logger = logging.getLogger('cmd')
configureLogger(logger, "router-cli.log")   

TESTING = True



class RouterCLI(DefaultCmd):
    def __init__(self):
        DefaultCmd.__init__(self)

        self.conf = 'data.json'

        self.databaseSchema = {
            'Loopback-address': 'IPv6',
            'Router-ID': 'IPv4',
            'Interface':{
                'uchar': {
                    'Link-Local-address': 'IPv6',
                    'Status': 'Up|Down',
                    'Name': 'text',                   
                    'Traffic_Class': {                        
                        'uint': {
                            'WRED': 'uint',
                            'DRR-weight': 'uchar',
                            'Priority': 'High|Normal',                      
                        },
                    },
                },
            },
            'Route-Entry':[{
                'Dest-Network-prefix': 'IPv6',
                'Outport': 'ushort',
            },],
            'Virtual-Network': {
                'uint': {
                    'Loopback-address': 'IPv6',
                    'Core-Interface-address': 'IPv6',
                    'Core-Interface-name': 'text',
                    'Core-Interface-status': 'Up|Down',
                    'Access-Interface': {
                        'IPv6': {
                            'L3-interface-index': 'ushort',
                            'Status': 'Up|Down',
                            'Name': 'text',
                            'Client-Network':['IPv6',],
                        },
                    },
                    'Neigbor-Node': [{
                        'L3-Loopback-address': 'IPv6',
                        'Core-Interface-address': 'IPv6',
                    },],
                    'VRF-Route-Entry':[{
                        'Dest-Network-prefix': 'IPv6',
                        'Edge-address': 'IPv6',
                        'Outport': 'ushort',
                    },],
                    'PolicedFlow':[{                        
                        'Client-Src-IP': 'IPv6',
                        'Client-Dst-IP': 'IPv6',
                        'IP-protocol': 'TCP|UDP',
                        'Src-port': 'ushort',
                        'Dst-port': 'ushort',
                        'TrafficClass': 'uchar',
                        'CIR': 'uint',
                        'CBS': 'ushort',
                    },],
                    'ShapedFlow':[{                        
                        'Client-Src-IP': 'IPv6',
                        'Client-Dst-IP': 'IPv6',
                        'IP-protocol': 'TCP|UDP',
                        'Src-port': 'ushort',
                        'Dst-port': 'ushort',
                        'TrafficClass': 'uchar',
                        'CIR': 'uint',
                        'CBS': 'uint',
                        'WRED': 'ushort',
                    },],
                },
            },
        }

        self.defaultDatabase = clearedDictValues(self.databaseSchema)
        if TESTING:
            self.defaultDatabase = testingData.defaultDatabase

        self.prompt = "Router> "
        self.intro  = "IPv6 QoS Configuration and Management command-line."
        self.database = self.loadData()   
            
    def do_commit(self, args):  
        " Validates data and save to a file"
        if self.validateData(self.database, self.databaseSchema) and self.checkDataConsistency(self.database): 
            self.saveData(self.database)
            logger.info(' OK: Data committed to a file')
        else:
            logger.info(' Error: Data commit unsucessful!')    

    def checkDataConsistency(self, database):
        " Check reference values consistency"
        consisted = True
        for vn_index, vn in self.database['Virtual-Network'].items():
            for access_addr, access in vn['Access-Interface'].items():
                if access['L3-interface-index'] not in self.database['Interface']:
                    logger.info(" VN %s Access-Interface %s L3-Interface %s not present in Interfaces" 
                                % (vn_index, access_addr, access['L3-interface-index']))
                    consisted = False
        for interface_index, value in self.database['Interface'].items():
            if interface_index == '192' or interface_index == '193':
                logger.info(" Interface indexes 0hC0 (192) and 0hC1 (193) are reserved")
                consisted = False
                    
        return consisted   
        
# *** MAIN LOOP ***
if __name__ == '__main__':
    cmdLine = RouterCLI()
    cmdLine.cmdloop()
