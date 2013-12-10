cli-from-datamodel
==================

Creates interactive general purpose console command line interface (commands interpreter with complementation) from declared data model schema.


Supporting CLI commands
-------------------------
* set - Create object or set parameter value
           (Examples: 
                set Interface [uchar] name [uchar]
                set Interface [uchar] status [Up|Down]
                set Virtual-Network [uint] Access-Interface [ipv6addr] Client-Network [ipv6addr]
            )
* delete - Delete object
            (Example: delete Route-Entry Dest-Network-prefix [ipv6addr] Outport [ushort])
* show - Show object or parameter value
* data - Show database subtree or overwrite loaded database subtree in declared formats (xml, json, python-types)
         (Example:
            data python-types {'param1':'p1', param2:['value1', 'value2']}
            data xml <section><param1>p1</param1><param2>value1<param2><param2>value2</param2></section>
          )
* schema - Present datamodel schema for current active node subtree
* commit - Save database
* open - Open subcommand for a database node specified by arguments
* exit - Terminates subcommand CLI and returns to upper node in database or close the command-line if current node is root
* [tab] - Command syntax complementation (shows list of available commands or current node values)
* [up|down] - View command history
* help or ? - Help about available options


About database
---------------
It is a tree of python objects [dictionaries, list, tuples, integers (i.e.: 'uint', 'ushort', 'uchar'), strings (i,e.: 'read-only', 'text', 'IPv6')] which is declared by a schema and stored in local file ("a database").

Dynamicly created CLI interpreter allows for accessing and manipulation (CRUD operations) of any parameter or object within a database tree. The CLI interpreter is created only basing on data model schema.

Example of the schema:
<pre>
{
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
</pre>

Requirements
-------------

1. Readline support:
* Linux: http://pypi.python.org/pypi/readline/
* MSWindows: https://pypi.python.org/pypi/pyreadline/1.7.1