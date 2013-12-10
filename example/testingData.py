defaultDatabase = {
    'Loopback-address': '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
    'Router-ID': '192.168.10.1',
    'Interface':{
        '1':{
            'Link-Local-address': '2001:db8:85a3:0:0:8a2e:370:7334',
            'Status': 'Up',
            'Name': 'Test1',
            'Traffic_Class': {                
                '1': {                   
                    'WRED': '16000',
                    'DRR-weight': '20',
                    'Priority': 'Normal'                                         
                },
                '2': {                   
                    'WRED': '64000',
                    'DRR-weight': '201',
                    'Priority': 'High'                                         
                },                
            }, 
        },
        '2':{
            'Link-Local-address': '2001:db8:85a3::8a2e:370:7334',
            'Status': 'Down',
            'Name': 'Test2',
            'Traffic_Class': {
                '10': {                   
                    'WRED': '64000',
                    'DRR-weight': '20',
                    'Priority': 'Normal'                      
                },                
            },
        },        
    },
    'Route-Entry': [],
    'Virtual-Network': {
        '1': { 
            'Loopback-address': '0:0:0:0:0:0:0:1',
            'Core-Interface-address': '::ffff:c000:280/64',
            'Core-Interface-name': 'Testowa-nazwa',
            'Core-Interface-status': 'Up',
            'Access-Interface': {
                '::ffff:192.0.2.128/64': {
                    'L3-interface-index': '1',
                    'Status': 'Up',
                    'Name': 'Nazwa',
                    'Client-Network': ["cccc::ffff:4/32",]
                },
                '::ffff:192.0.2.100/64': {
                    'L3-interface-index': '2',
                    'Status': 'Down',
                    'Name': 'Nazwa2',
                    'Client-Network': ["eeee::ffff:5/64","dddd::ffff:6/64"]
                },
            },
            'Neigbor-Node': [
                {   'L3-Loopback-address': '::1/128',
                    'Core-Interface-address': '::ffff:1/64'
                },
                {   'L3-Loopback-address': '::ffff:2/64',
                    'Core-Interface-address': '::ffff:3/64'
                },
            ],
            'VRF-Route-Entry':[
                {   'Dest-Network-prefix':'1234::ffff:6/32',
                    'Edge-address': '::ffff:7/64',
                    'Outport': '1'
                },
            ],
            'PolicedFlow':[
                {   'Client-Src-IP': '::ffff:a/64',
                    'Client-Dst-IP': '::ffff:b/64',
                    'IP-protocol': 'TCP',
                    'Src-port': '2010',
                    'Dst-port': '1010',
                    'TrafficClass': '10',
                    'CIR': '9000',
                    'CBS': '1024'
                },
                {   'Client-Src-IP': '::ffff:c/64',
                    'Client-Dst-IP': '::ffff:d/64',
                    'IP-protocol': 'UDP',
                    'Src-port': '3010',
                    'Dst-port': '4010',
                    'TrafficClass': '10',
                    'CIR': '10000',
                    'CBS': '512'
                },
            ],
            'ShapedFlow':[
                {   'Client-Src-IP': '::ffff:7/64',
                    'Client-Dst-IP': '::ffff:8/64',
                    'IP-protocol': 'TCP',
                    'Src-port': '2010',
                    'Dst-port': '1010',
                    'TrafficClass': '10',
                    'CIR': '9000',
                    'CBS': '1024',
                    'WRED': '16000'
                },
                {   'Client-Src-IP': '::ffff:9/64',
                    'Client-Dst-IP': '::ffff:10/64',
                    'IP-protocol': 'UDP',
                    'Src-port': '3010',
                    'Dst-port': '4010',
                    'TrafficClass': '10',
                    'CIR': '4096',
                    'CBS': '512',
                    'WRED': '64000'
                },
            ],
        },
    },
}
