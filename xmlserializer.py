"""Helper to convert Python data structures into XML. Used so we can return
intuitive data from resource methods which are usable as JSON but can also be
returned as XML.
"""

from xml.sax.saxutils import escape as xml_escape
import xml.dom.minidom

def obj2xml(obj, indent=4):
    document = dumps(obj)
    if indent != None:
        d = xml.dom.minidom.parseString(document)
        document = d.toprettyxml(indent=' '*indent)
    return document
        
def dumps(obj, root_tag=''):
    """Serialize :arg:`obj` to an XML :class:`str`.
    """
    xml = _get_xml_value(obj)
    starter = '<?xml version="1.0" encoding="UTF-8"?>'
    if root_tag == '':
        return starter + xml
    else:
        root = root_tag
        return starter + '<' + root + '>' + xml + '</' + root + '>'


def _get_xml_value(value):
    """Convert an individual value to an XML string. Calls itself
    recursively for dictionaries and lists.

    Uses some heuristics to convert the data to XML:
        - In dictionaries, the keys become the tag name.
        - In lists the tag name is 'child' with an order-attribute giving
          the list index.
        - All other values are included as is.

    All values are escaped to fit into the XML document.

    :param value: The value to convert to XML.
    :type value: Any valid Python value
    :rtype: string
    """
    retval = []
    if isinstance(value, dict):
        for key, subvalue in value.items():
            key_prefix = key.split('_')[0]
            attributes = key.split('_')[1:]
            if ':' in key_prefix or '/' in key_prefix or key_prefix[0].isdigit():
                if len(attributes) > 0:
                    key = "Key_key=\"%s\"_%s" % (key_prefix, attributes)
                else:
                    key = "Key_key=\"%s\"" % key_prefix
            if '\"' in key:
                startkey = key.replace('_', ' ')
                endkey = key.split('_')[0]
            else:
                startkey = key
                endkey = key
            if isinstance(subvalue, list):
                for v in subvalue:
                    retval.append('<' + xml_escape(str(startkey)) + '>')
                    retval.append(_get_xml_value(v))
                    retval.append('</' + xml_escape(str(endkey)) + '>')
            else:
                retval.append('<' + xml_escape(str(startkey)) + '>')
                retval.append(_get_xml_value(subvalue))
                retval.append('</' + xml_escape(str(endkey)) + '>')
    elif isinstance(value, list):
        for key, subvalue in enumerate(value):
            retval.append(_get_xml_value(subvalue))
    elif isinstance(value, bool):
        retval.append(xml_escape(str(value).lower()))
    elif isinstance(value, unicode):
        retval.append(xml_escape(value.encode('utf-8')))
    elif isinstance(value, type(None)):
        pass
    else:
        retval.append(xml_escape(str(value)))
    return "".join(retval)


import xml.etree.ElementTree as etree

def xml2obj(text):
    """Convert xml string to python object composed of dictionaries, list, etc."""
    tree = etree.fromstring(text)
    res = _xml_to_dict(tree)
    return res

  
def _xml_to_dict(elem):
    children = elem.getchildren()
    if len(children) == 0:
        return {elem.tag:elem.text}
    d = {}
    for child in children:
        if "Key key=\"" in child.tag[:8]:
            child.tag = child.tag[8:]
            child.tag.replace("\" ", '', 1)
        for name, value in child.attrib.items():
            child.tag += "_%s=\"%s\"" % (name, value)
        res = _xml_to_dict(child)
        key, value = res.items()[0]
        if elem.tag not in d:
            d[elem.tag] = res
        elif key not in d[elem.tag]:
            d[elem.tag][key] = value
        else:
            if not isinstance(d[elem.tag], list):
                d[elem.tag][child.tag] = [d[elem.tag][child.tag]]
            d[elem.tag][child.tag].append(res[child.tag])
    return d


if __name__ == '__main__':
    import pprint
    import testingData
    obj = testingData.defaultDatabase
    text = obj2xml(obj, indent=None)
    file('conf.xml', 'w').write(text)
  

