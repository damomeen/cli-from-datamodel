#!/usr/bin/python

"""
The MIT License (MIT)

Copyright (c) 2011 Poznan Supercomputing and Networking Center (PSNC)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Autor: Damian Parniewicz (damian.parniewicz at gmail.com)
"""

import sys, copy, json, traceback, os, copy, pickle
import os.path
from cmd import Cmd
import logging
import socket
import pprint
from functools import wraps
from xmlserializer import xml2obj, obj2xml


logger = logging.getLogger('cmd.default')

def configureLogger(_logger, logFile=None):
    _logger.setLevel(logging.DEBUG)
    
    if logFile is not None:
        logs = logging.FileHandler(logFile)
        logs.setLevel(logging.DEBUG)
    logs_formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(message)s")
    logs.setFormatter(logs_formatter)
    _logger.addHandler(logs)

    _logger = logging.getLogger('cmd')
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console.setFormatter(console_formatter)
    _logger.addHandler(console)

def unicodeConverter(obj):
    " Convert unicode string to standart Python string"
    def parseValue(value):
        if isinstance(value, dict):
            return unicodeConverter(value)
        elif isinstance(value, list):
            return [unicodeConverter(i) for i in value]
        elif isinstance(value, unicode):
            return str(value)
        elif value is None:
            return value
          
    if type(obj) is dict:
        newobj = {}
        for key, value in obj.iteritems():
            newobj[str(key)] = parseValue(value)
    elif type(obj) is list:
        newobj = [parseValue(value) for value in obj]
    elif isinstance(obj, unicode):
        return str(obj)
    elif obj is None:
        return obj
    else:
        logger.debug(" ERROR: Type %s has no implemented unicode converter")
        
    return newobj

def objectStdout(obj, indent=0):
    prefix = ' '*indent 
    if isinstance(obj, dict):
        for item in obj.items():
            sys.stdout.write(prefix + " %s : %s\n" % item)
    elif isinstance(obj, list):
        text = ' '.join(obj)
        sys.stdout.write(prefix + " %s\n" % text)
    else:
        sys.stdout.write(prefix + " %s\n" % str(obj))

def compareDict(dict1, dict2):
    " Compare two dictionaries"
    if len(dict1) != len(dict2):
        return False
    for v1, k1 in dict1.items():
        if dict2.get(v1) != k1:
            return False
    return True

def clearedDictValues(dictionary):
    d = {}
    for key, value in dictionary.items():
        if type(value) is dict:
            #d[key] = clearedDictValues(value)
            d[key] = {}
        elif type(value) is list:
            d[key] = []
        else:
            d[key] = None
    return d

def exception_handler(f):
    'intercepting all calls and checking for exceptions'
    wraps(f)
    def wrapper(*args, **kwargs):
        logger.debug("Calling %s with arguments: %s" % (f.__name__, str(args)))
        try:
            return f(*args, **kwargs)
        except:
            logger.debug("Exception" + traceback.format_exc())
    return wrapper

USING_READLINE = True
try:
    # For platforms without readline support go visit ...
    # http://pypi.python.org/pypi/readline/
    import readline
    delimiters = readline.get_completer_delims()
    delimiters.replace('/', '').replace(':', '')
    readline.set_completer_delims(delimiters)
except:
    try:
        # For Windows readline support go visit ...
        # https://launchpad.net/pyreadline
        import pyreadline
    except:
        USING_READLINE = False

class DefaultCmd(Cmd):
    def __init__(self, database=None, dataSchema=None):
        Cmd.__init__(self)
        if not USING_READLINE:
            self.completekey = None
        self.prompt = "> "
        self.intro  = "Default Command-line."
        self.dataFile = 'data.json'
        self.defaultDatabase = {}
        if dataSchema:
            self.databaseSchema = dataSchema
        else:
            self.databaseSchema = {}
        if database:
            self.database = database
        else:
            self.database = self.loadData()

    @exception_handler
    def loadData(self):
        """ 
        Loads data model information to run-time
        Creates data model json file if missing 
        """ 
        if os.path.isfile(self.dataFile) is False:
             os.system('touch %s' % self.dataFile) # creates the file if missing 
        data = ''        
        try:
            data = file(self.dataFile, 'r').read()
        except:
            logger.error("Exception" + traceback.format_exc())

        if len(data) == 0:
            database = self.defaultDatabase
        else:
            database = json.loads(data)
            database = unicodeConverter(database)
        return database

    @exception_handler
    def saveData(self, database):
        " Dumping data model to the json file "
        file(self.dataFile, 'w').write(json.dumps(database, indent=4))

    @exception_handler
    def localizeObj(self, args, stopCondition=2):
        " Go through data model nodes to a parent of the object refered by args"
        args = args.split()
        arg = None
        _args = []
        obj = self.database
        schema = self.databaseSchema
        while len(args) > stopCondition and type(obj) is dict:
            arg = args.pop(0)
            _args.append(arg)              
            if arg in obj:
                obj = obj[arg]
                if arg not in schema:
                    paramType = schema.keys()[0]
                    schema = schema[paramType]
                else:
                    schema = schema[arg]
            else:
                break
        arg = args.pop(0)
        _args.append(arg)

        logger.debug('arg=%s, args=%s', arg, args)

        return arg, args, _args, obj, schema

    @exception_handler
    def do_show(self, args):
        """
        Show object or parameter value
        """
        try:
            arg, args, _args, obj, schema = self.localizeObj(args)

            if arg == 'list':
                if type(obj) is dict:
                    # listing object parameters or indexes
                    objectStdout(obj.keys())
                else:
                    raise Exception()
            elif type(obj[arg]) is dict and len(args) == 0:
                logger.debug('obj %s', obj[arg])
                # listing object parameters or indexes
                objectStdout(obj[arg].keys())
            elif type(obj[arg]) is dict and len(args) > 0:
                if args[0] == 'list':
                    # listing object parameters or indexes
                    objectStdout(obj[arg].keys())
                    return
                obj = obj[arg][args[0]]
                logger.debug('obj %s', obj)
                if type(obj) is dict:
                    # listing dict object parameters and values
                    objectStdout(obj)
                elif type(obj) in (list, tuple):
                    # listing list object values
                    for index, item in enumerate(obj):
                        sys.stdout.write(" %s.%s item #%i:\n" % ('.'.join(_args), args[0], index))
                        objectStdout(item, indent = 2)
                else:
                    # listing simple object within dict
                    objectStdout(obj)
            else:
                # listing any other kind of object
                objectStdout(obj[arg])       
        except:
            logger.info(" Error: Command parameters not recognized!")
            logger.debug(traceback.format_exc())

    def complete_show(self, text, line, begidx, endidx):
        " Completing show command"
        ret = self._completedefault(text, line, begidx, endidx)
        line = line.split()
        if (len(line) == 2 and len(text) == 0) or (len(line) == 3 and ('list'.startswith(text) and len(text) > 0)):
            obj = self.database[line[1]]
            if isinstance(obj, dict):
                ret.append('list')
        return ret      

    @exception_handler
    def do_set(self, args):
        """
        Create object or set parameter value
        """
        try:
            arg, args, _args, obj, schema = self.localizeObj(args)

            if type(obj) is dict:
                # setting/adding value to dict
                if arg not in schema:
                    logger.info(" Error: Parameter %s not recognized", '.'.join(_args))
                    return
                logger.debug('obj keys %s', obj.keys())
                logger.debug('schema keys %s', schema.keys())
                if type(obj[arg]) in (str, type(None)):
                    # setting simple parameter value within dict
                    obj[arg] = args[0]
                    logger.info(" OK: Setting parameter %s to %s", '.'.join(_args), args[0])
                elif type(obj[arg]) is dict:
                    # creating a new dict object within dict
                    obj = obj[arg]
                    schema = schema[arg]
                    arg = args.pop(0)
                    _args.append(arg)
                    logger.debug('arg %s %s', arg, args)
                    logger.debug('obj keys %s', obj.keys())
                    logger.debug('schema keys %s', schema.keys())
                    paramType = schema.keys()[0]
                    if paramType not in self.knownTypes():
                        raise Exception()
                    if self.validateValue(arg, paramType) is False:
                        return
                    if len(args) == 0 and (arg not in obj or len(obj[arg]) == 0):
                        # creating a new object (a dict)
                        obj[arg] = clearedDictValues(schema[paramType])
                        logger.info(" OK: Setting default value of %s", '.'.join(_args))
                    else:
                        logger.info(" Error: Object %s already exist", '.'.join(_args))
                elif type(obj[arg]) is list:
                    # adding simple value to the list within dict
                    obj = obj[arg]
                    schema = schema[arg]
                    arg = args.pop(0)
                    _args.append(arg)
                    logger.debug('arg %s %s', arg, args)
                    logger.debug('obj %s', obj)
                    logger.debug('schema %s', schema)
                    if self.validateValue(arg, schema[0]) is False:
                        return
                    obj.append(arg)
                    logger.info(' OK: Adding %s to %s', arg, '.'.join(_args))

            elif type(obj) is list:
                # adding a dict value within list
                logger.debug('obj list %s', obj)
                logger.debug('schema list %s', schema)
                if arg in schema[0]:
                    item = clearedDictValues(schema[0])
                    args.insert(0, arg)
                    _args.pop()
                    # create dict object to be inserted in list
                    while len(args) > 0:
                        paramName, paramValue = args[:2]
                        args = args[2:]
                        if paramName not in schema[0]:
                            logger.info(" Error: Unknown parameter %s.%s", '.'.join(_args), paramName)
                            return
                        if self.validateValue(paramValue, schema[0][paramName]) is False:
                            return
                        item[paramName] = paramValue
   
                    obj.append(item)   
                    
                    #new
                    swhere = '.'.join(_args)
                    if swhere.count('Policed') > 0:
                        #do it only for flows                       
                        f1 = open('/tmp/flow_connection', 'w')                            
                        pickle.dump("policedFlow", f1)
                        pickle.dump(_args[1], f1)
                        pickle.dump(item, f1)      
                        f1.close()  
                       
                    elif swhere.count('Shaped') > 0 :
                        #do it only for flows                       
                        f1 = open('/tmp/flow_connection', 'w')  
                        pickle.dump("shapedFlow", f1)
                        pickle.dump(_args[1], f1)
                        pickle.dump(item, f1)      
                        f1.close()                                       
                    else:
                        # check if item already on list
                        found = False
                        for i in obj:
                            if compareDict(i, item):
                                found = True
                        if found is False:                                      
                            logger.info(" OK: Adding %s to %s", item, '.'.join(_args))                                
                        else:
                            logger.info(" Error: %s is already in %s", item, '.'.join(_args))
                else:
                    logger.info(" Error: Other type of object %s %s", type(obj), obj)
        except:
            logger.info(" Error: Command parameters not recognized!")
            logger.debug(traceback.format_exc())

    @exception_handler
    def do_delete(self, args):
        """
        Delete object
        """
        try:
            arg, args, _args, obj, schema = self.localizeObj(args)

            if type(obj) is str:
                logger.debug('obj %s', obj)
                logger.info(" Error: %s deletion not is allowed", '.'.join(_args))
                return                
            elif type(obj) is dict:
                logger.debug('obj keys %s', obj.keys())
                logger.debug('schema keys %s', schema.keys())
                if arg not in obj:
                    logger.info(" Error: Object %s is not present", '.'.join(_args)) 
                elif arg in schema and len(args) == 0 and type(obj[arg]) is not list:
                    logger.info(" Error: %s deletion not is allowed", '.'.join(_args))
                elif type(obj[arg]) is dict:
                    # removing an object
                    if len(args) == 1:
                        obj = obj[arg]
                        arg = args.pop()
                        _args.append(arg)
                    del obj[arg]
                    logger.info(" OK: %s was deleted", '.'.join(_args))
                elif type(obj[arg]) is list:
                    # removing simple value from the list
                    if args[0].isdigit() and obj.count(args[0]) == 0: # deletion using position in list diseabled when an integer value in list
                        # removing by index
                        del obj[int(args[0])]
                    else:
                        # removing by value
                        obj[arg].remove(args[0])
                    logger.info(" OK: %s was deleted from %s", args[0], '.'.join(_args))
                else:
                    logger.info(" Error: Missing deletion handling for %s", '.'.join(_args)) 
            elif type(obj) is list:
                logger.debug('obj list %s', obj)
                logger.debug('schema list %s', schema)
                if arg.isdigit():
                    # removing by index
                    del obj[int(arg)]
                    logger.info(" OK: %s was deleted", '.'.join(_args))
                elif arg in schema[0]:
                    # removing by value (a dict)
                    item = {}
                    args.insert(0, arg)
                    _args.pop()
                    # create dict object for search
                    while len(args) > 0:
                        paramName, paramValue = args[:2]
                        if paramName not in schema[0]:
                            logger.info(" Error: Parameter %s not recognized", paramName)
                            return
                        args = args[2:]
                        item[paramName] = paramValue
                    # search value on list
                    removed = False
                    for i in obj:
                        if compareDict(i, item):
                            obj.remove(i)
                            removed = True
                            break                            
                    if removed:             
                        logger.info(" OK: %s was removed from %s", item, '.'.join(_args))
                    else:
                        logger.info(" Error: %s was not found in %s", item, '.'.join(_args))
                        
                    #new
                    swhere = '.'.join(_args)
                    if swhere.count('Policed') > 0:
                        #do it only for flows                       
                        f1 = open('/tmp/flow_connection', 'w')                            
                        pickle.dump("policedFlow", f1)
                        pickle.dump(_args[1], f1)
                        pickle.dump(item, f1)      
                        f1.close()  
                       
                    elif swhere.count('Shaped') > 0 :
                        #do it only for flows                       
                        f1 = open('/tmp/flow_connection', 'w')  
                        pickle.dump("shapedFlow", f1)
                        pickle.dump(_args[1], f1)
                        pickle.dump(item, f1)      
                        f1.close()     
                        
                else:
                    logger.info(" Error: Parameter %s not recognized", arg)
            else:
                logger.info(" Error: Other type of object %s %s", type(obj), obj)
        except:
            logger.info(" Error: Command parameters not recognized!")
            logger.debug(traceback.format_exc())

    def completenames(self, text, *ignored):
        " Small modification to base method in order to add space after method token completition"
        dotext = 'do_'+text
        return [a[3:]+' ' for a in self.get_names() if a.startswith(dotext)]
    
    def completedefault(self, text, line, begidx, endidx):
        " Completing any command with non-already defined completion"
        return self._completedefault(text, line, begidx, endidx)

    @exception_handler
    def _completedefault(self, text, line, begidx, endidx):
        " Default completing command"
        line_orginal = copy.copy(line)
        def getSubItem(obj):
            if type(obj) is dict:
                return obj.keys()
            else:
                return obj[0]

        def completeAttributes(schema, arg, line):
            '''complete attributes of object, defined by schema, stored in list'''
            if line_orginal.startswith("show"):
                return [] 
            schema = getSubItem(schema)
            logger.debug("Schema for attributes is %s", schema)
            attributes = []
            #if len(arg) > 0:
            #    line.insert(0, arg)
            while len(line) > 0:
                logger.debug("Line is %s", line)
                arg = line.pop(0)
                logger.debug('Arg is %s', arg)
                if arg in schema:
                    attributes.append(arg)
                    if len(line) == 0:
                        break
                    line.pop(0) # skip value of attribute
                else:
                    break
            logger.debug("Completed attributes are %s", attributes)
            ret = [attribute for attribute in schema if attribute.startswith(text) and attribute not in attributes]
            logger.debug(" Ret is %s", ret)
            if len([attr for attr in schema if attr not in attributes]) == 0:
                return 'Finalized' 
            if len(ret) == 1:           
                ret = [ret[0] + ' '] # adding space after a single parameter to help typing a value
            return ret

        ret = []         
        line = line.split()
        line.pop(0)
        obj = self.database
        schema = self.databaseSchema
        try:
            while len(line) > 1:
                arg = line[0]
                if arg in obj:
                    arg = line[0]   
                    line.pop(0)
                    obj = obj[arg]
                    if arg not in schema:
                        paramType = schema.keys()[0]
                        schema = schema[paramType]
                    else:
                        schema = schema[arg]
                else:
                    schema = getSubItem(schema)
                    ret = completeAttributes(schema, "", line)
                    if ret == 'Finalized':
                        return []
                    if len(ret) > 0:
                        return ret
                    logger.debug("Unknown %s", line)
                    break
                                        
            logger.debug("Line is %s", ' '.join(line))
            logger.debug("Schema is %s", schema)

            if (len(line) == 0 and len(text) == 0) or (len(line) == 1 and len(text) > 0):
                try:
                    logger.debug('line=0, obj %s', obj)
                    obj = getSubItem(obj)
                    if type(obj) is dict:
                        obj = getSubItem(obj)
                except IndexError:
                    schema = getSubItem(schema)
                    ret = completeAttributes(schema, "", line)
                    if ret == 'Finalized':
                        return []
                    if len(ret) > 0:
                        return ret
            elif (len(line) == 1 and len(text) == 0) or (len(line) == 2 and len(text) > 0):
                try:
                    logger.debug('line=1, obj %s', obj)
                    obj = getSubItem(obj[line[0]])
                    if type(obj) is dict:
                        obj = getSubItem(obj)
                except IndexError:
                    schema = getSubItem(schema[line[0]])
                    line.pop(0)
                    ret = completeAttributes(schema, "", line)
                    if ret == 'Finalized':
                        return []
                    if len(ret) > 0:
                        return ret
                    
                
        except:
            logger.debug(traceback.format_exc())
        
        logger.debug("Obj %s", obj)
        
        if type(obj) is not list or type(obj) is str: 
            return []
        else:   
            ret = [param for param in obj if param.startswith(text)]

        if len(ret) == 1:           
            ret = [ret[0] + ' '] # adding space after a single parameter to help typing a value
        return ret

    @exception_handler
    def do_data(self, args):
        """        
        Show or overwrite loaded database in declared formats:
            data format       - showing database in format
            data format text  - overwriting database with database expressed as formated text
        Example:
            data python-types {'param1':'p1', param2:['value1', 'value2']}
            data xml <section><param1>p1</param1><param2>value1<param2><param2>value2</param2></section>
        """
        args = args.split()
        if len(args) == 1:
            if args[0] == 'python-types':
                text = pprint.pformat(self.database, indent=4)
            elif args[0] == 'json':
                text = json.dumps(self.database, indent=4)
            elif args[0] == 'xml':
                text = obj2xml(self.database, indent=None)
            else:
                logger.info(" Error: Command parameters %s not recognized!", args)
            sys.stdout.write(text+'\n')
        elif len(args) > 1:
            data = ' '.join(args[1:])
            if args[0] == 'python-types':
                data = eval(data)
            elif args[0] == 'json':
                data = json.loads(data)
            elif args[0] == 'xml':
                data = xml2obj(data)
            else:
                logger.info(" Error: Command parameters not recognized!")
                return
            if self.validateData(data, self.databaseSchema):
                self.database = data
        else:
            sys.stdout.write(pprint.pformat(self.database, indent=4)+'\n')
            
    def complete_data(self, text, line, begidx, endidx):
        return [param for param in ['json', 'xml', 'python-types'] if param.startswith(text)]

    @exception_handler
    def do_open(self, args):
         " Open subcommand for a database node specified by arguments"
         arg, args, _args, obj, schema = self.localizeObj(args, stopCondition=1)
         
         if arg not in obj:
            logger.info(" Error: Command parameters not recognized!")
            return

         paramType = schema.keys()[0]
         if paramType in self.knownTypes():
            schema = schema[paramType]
         else:
            schema = schema[arg]
         subCmd = DefaultCmd(database  = obj[arg],
                             dataSchema = schema)
         subCmd.prompt = '%s-%s> ' % (self.prompt[:-2], '.'.join(_args))
         subCmd.cmdloop()

    def do_schema(self, args):
        " Show loaded data schema"
        sys.stdout.write(pprint.pformat(self.databaseSchema, indent=4)+'\n')
      
        
    def complete_schema(self, text, line, begidx, endidx):
        pass # No data completition for 'data' command
 
    def do_exit(self, args):
        " Terminates the command-line"
        return True

    def complete_exit(self, text, line, begidx, endidx):
        pass # No data completition for 'exit' command

    def emptyline(self):
        pass

    def knownTypes(self):
        return ['IPv6', 'uint', 'ushort', 'uchar', 'read-only', 'text']

    @exception_handler
    def validateValue(self, value, schema, checkReadOnly=True):
        if schema is None:
            logger.info(' Unknown parameter %s', value)
            return False
        try:
            if schema == 'IPv6':
                addr = value.split('/')
                if len(addr) == 2:
                    prefix = addr[1]
                else:
                    prefix = '128'
                addr = addr[0]
                if socket.inet_pton(socket.AF_INET6, addr) and  4 <= int(prefix) <= 128:
                    return True
            if schema == 'IPv4':
                if socket.inet_pton(socket.AF_INET, value):
                    return True
            elif schema == 'uint':
                if 0 <= int(value):
                    return True
            elif schema == 'ushort':
                if 0 <= int(value) <= 65535:
                    return True
            elif schema == 'uchar':
                if 0 <= int(value) <= 255:
                    return True
            elif '|' in schema:
                for desc in schema.split('|'):
                    if desc == value:
                        return True
            elif schema == 'read-only':
                if checkReadOnly:
                    logger.info(" Error: Cannot set parameter - it is read-only!")
                    return False
                return True
            elif schema == 'text':
                _value = copy.copy(value)
                _value = _value.replace('-', '').replace('_', '').replace('.', '')
                if _value.isalnum():
                    return True
            else:
                logger.info(' Error: Unknown type %s', schema)
                return False
        except:
            logger.debug(traceback.format_exc())
        logger.info(' Error: Validation failed - parameter %s is not type of %s', value, schema)
        return False

    @exception_handler
    def validateData(self, database, dataschema):
        " Validates data agains data schema"
        validated = True
        if type(dataschema) is dict:     
            for name, schema in dataschema.items():
                obj = database.get(name)
                if obj is None:
                    logger.info(" Error: Lack of %s object/parameter in object %s", name, database)
                    validated = False
                    continue
                if type(obj) != type(schema):
                    logger.info(" Error: Unproper %s parameter value type %s", name, obj)
                    validated = False
                    continue
                if type(schema) is str:
                    if self.validateValue(obj, schema, checkReadOnly=False) is False:
                        validated = False
                        continue
                elif type(schema) is dict:
                    indexType, valueSchema = schema.items()[0]
                    for index, value in obj.items():              
                        if indexType in self.knownTypes():
                            if self.validateValue(index, indexType) is False:
                                logger.info(" Error: Unproper index %s of %s", index, name)
                                validated = False
                                continue
                            if self.validateData(value, valueSchema) is False:
                                validated = False
                                continue
                        else:
                            if self.validateData(value, schema[index]) is False:
                                validated = False
                                continue
                elif type(schema) in (list, tuple):
                    valueSchema = schema[0]
                    for value in obj:
                        if self.validateData(value, valueSchema) is False:
                            validated = False
                            continue
                else:
                    logger.info(' Error: Validation is not implemented for %s', type(schema))
        elif type(dataschema) is list:
            for value in database:
                 if self.validateData(value, dataschema[0]) is False:
                    validated = False
                    continue
        return validated
