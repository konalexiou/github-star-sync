#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script copies all gihtub stars from a user to the authenticated user
# It utilizes the following GITHUB API requests
# Get starred repos from user
# GET /user/:user/starred
# Star repo to authenticated user
# PUT /user/starred/:user/:repo
#
# Author: Konstantinos Alexiou
# Email: konalexiou@gmail.com
# Date: 2017-11-13
#

import sys
import argparse
import requests
import re
from colorama import init, Fore, Back, Style
init()

def sync(from_username, username, password):
    # init
    starlist = []
    auth = ()

    # set vars
    auth = (username, password)
    to = get_username(auth)

    # copy stars to starlist
    print 'Discovering github stars from ' + from_username + '... '
    get_starlist('https://api.github.com/users/' + from_username + '/starred', auth, starlist)
    print Fore.GREEN + 'Found ' + str(len(starlist)) + Style.RESET_ALL

    # star repos in starlist
    print 'Syncing github stars to ' + to + '... '
    for repo in starlist:
        star_repo(repo, auth)

    print Fore.GREEN + 'Done!' + Style.RESET_ALL



def get_username(auth):
    r = requests.get('https://api.github.com/user', auth=auth)
    try:
        user = r.json()
        return user['login']
    except Exception:
        print Fore.RED + "Error: Check username, password"  + Style.RESET_ALL
        sys.exit()



def star_repo(repo, auth):
    """Star a github repo"""
    r = requests.put('https://api.github.com/user/starred/'+repo, auth=auth)
    print 'starred: ' + Fore.CYAN + repo + Style.RESET_ALL



def get_starlist(uri, auth, starlist):
    """Return a list with github repos"""
    r = requests.get(uri, auth=auth)
    for repo in r.json():
        print 'found: ' + Fore.CYAN + repo['full_name'] + Style.RESET_ALL
        starlist.append(repo['full_name'])
    links = parse_header_links(r.headers['link'])
    if 'next' in links:
        get_starlist(links['next'], auth, starlist)
    return starlist



def parse_header_links(value):
    """Get a dict of parsed link headers. And then return pages"""
    links = []
    pages = {}
    replace_chars = " '\""
    for val in re.split(", *<", value):
        try:
            url, params = val.split(";", 1)
        except ValueError:
            url, params = val, ''
        link = {}
        link["url"] = url.strip("<> '\"")
        for param in params.split(";"):
            try:
                key, value = param.split("=")
            except ValueError:
                break
            link[key.strip(replace_chars)] = value.strip(replace_chars)
        links.append(link)
    for link in links:
        pages[link['rel']] = link['url']
    return pages



if __name__ == "__main__":
    # get command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("from_username", help="the github username from whom you want to sync the stars from")
    parser.add_argument("username", help="your github username")
    parser.add_argument("password", help="your github password")
    args = parser.parse_args()

    sync(args.from_username, args.username, args.password)
