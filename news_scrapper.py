from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import xml.etree.ElementTree as ET
from json import dump
import xml.sax.saxutils


class UnhandledException(Exception):
    pass


channel_elem = {'title': 'Feed', 'link': 'Link', 'lastBuildDate': 'Build Date',
                'pubDate': 'Date', 'language': 'Language', 'categories': 'Categories',
                'managingEditor': 'Editor', 'description': 'Description', 'item': None}
items_elem = {'title': 'Title', 'author': 'Author', 'pubDate': 'Date',
              'link': 'Link', 'categories': 'Categories', 'description': None}


def fin_dict(source, limit=None, json: bool=False):
    myroot = ET.fromstring(source)
    js_dict = {}
    for i in range(len(myroot)):
        for j in range(len(myroot[i])):
            for k in channel_elem:
                if myroot[i][j].tag == k and k != 'item':
                    js_dict[k] = myroot[i][j].text
                if myroot[i][j].tag == 'categories':
                    ll = []
                    for v in range(len(myroot[i][j])):
                        category = xml.sax.saxutils.unescape(myroot[i][j][v].text)
                        ll.append(category)
                    js_dict[k] = ', '.join(ll)
        js_dict['items'] = []
    for i in range(len(myroot)):
        for j in range(len(myroot[i])):
            if myroot[i][j].tag == 'item':
                dx = {}
                for k in range(len(myroot[i][j])):
                    for x in items_elem:
                        if myroot[i][j][k].tag == x:
                            if x in ['title', 'description']:
                                value = xml.sax.saxutils.escape(myroot[i][j][k].text)
                            else:
                                value = myroot[i][j][k].text
                            dx[x] = value
                js_dict['items'].append(dx)
    js_dict['items'] = js_dict['items'][:limit]
    if json:
        with open('new.json', 'w') as js:
            dump(js_dict, js, indent=2)
    return js_dict


def fin_list(d):
    result = []
    for key in channel_elem:
        if key in d:
            result.append(f"{channel_elem[key]}: {d[key]}")
    for i in range(len(d['items'])):
        for j in items_elem:
            if j in d['items'][i].keys():
                items = d['items'][i]
                s = f'{items_elem[j]}: {items[j]}'
                result.append(s)
    return result


def rss_parser(
        xml: str,
        limit: Optional[int] = None,
        json: bool = False,
) -> List[str]:
    final_dict = fin_dict(xml, limit, json)
    final_list = fin_list(final_dict)
    return final_list


def main(argv: Optional[Sequence] = None):
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )

    args = parser.parse_args(argv)
    source = requests.get(args.source).text
    try:
        print("\n".join(rss_parser(source, args.limit, args.json)))
        return 0
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()