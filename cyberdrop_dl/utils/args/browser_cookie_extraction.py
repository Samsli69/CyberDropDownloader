from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

import browser_cookie3
from InquirerPy import inquirer
from rich.console import Console

from cyberdrop_dl.utils.dataclasses.supported_domains import SupportedDomains

if TYPE_CHECKING:
    from typing import Dict

    from cyberdrop_dl.managers.manager import Manager


def cookie_wrapper(func):
    """Wrapper handles errors for url scraping"""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except PermissionError:
            console = Console()
            console.clear()
            console.print("We've encountered a Permissions Error. Please close all browsers and try again.",
                          style="bold red")
            console.print(
                "If you are still having issues, make sure all browsers processes are closed in a Task Manager.",
                style="bold red")
            console.print("Nothing has been saved.", style="bold red")
            inquirer.confirm(message="Press enter to return menu.").execute()
            return

    return wrapper


# noinspection PyProtectedMember
@cookie_wrapper
def get_forum_cookies(manager: Manager, browser: str) -> None:
    """Get the cookies for the forums"""
    auth_args: Dict = manager.config_manager.authentication_data
    for forum in SupportedDomains.supported_forums:
        try:
            cookie = get_cookie(browser, forum)
            if forum == 'simpcity.su':
                auth_args['Forums']['simpcity_ddg_cookie_1'] = cookie._cookies['.' + forum]['/']['__ddg1_'].value
                auth_args['Forums']['simpcity_ddg_cookie_2'] = cookie._cookies['.' + forum]['/']['__ddg2_'].value
                auth_args['Forums']['simpcity_ddg_cookie_5'] = cookie._cookies['.' + forum]['/']['__ddg5_'].value
                auth_args['Forums']['simpcity_ddg_id'] = cookie._cookies['.' + forum]['/']['__ddgid_'].value
                auth_args['Forums']['simpcity_ddg_mark'] = cookie._cookies['.' + forum]['/']['__ddgmark_'].value
            else:
                try:
                    auth_args['Forums'][f'{SupportedDomains.supported_forums_map[forum]}_xf_user_cookie'] = \
                        cookie._cookies[forum]['/']['xf_user'].value
                except KeyError:
                    pass
        except KeyError:
            try:
                cookie = get_cookie(browser, "www." + forum)
                if forum == 'simpcity.su':
                    auth_args['Forums']['simpcity_ddg_cookie_1'] = cookie._cookies["www." + forum]['/']['__ddg1_'].value
                    auth_args['Forums']['simpcity_ddg_cookie_2'] = cookie._cookies["www." + forum]['/']['__ddg2_'].value
                    auth_args['Forums']['simpcity_ddg_cookie_5'] = cookie._cookies["www." + forum]['/']['__ddg5_'].value
                    auth_args['Forums']['simpcity_ddg_id'] = cookie._cookies["www." + forum]['/']['__ddgid_'].value
                    auth_args['Forums']['simpcity_ddg_mark'] = cookie._cookies["www." + forum]['/']['__ddgmark_'].value
                else:
                    auth_args['Forums'][f'{SupportedDomains.supported_forums_map[forum]}_xf_user_cookie'] = \
                        cookie._cookies["www." + forum]['/']['xf_user'].value
            except KeyError:
                pass

    manager.cache_manager.save("browser", browser)


def get_cookie(browser: str, domain: str):
    """Get the cookies for a specific domain"""
    if browser == 'chrome':
        cookie = browser_cookie3.chrome(domain_name=domain)
    elif browser == 'firefox':
        cookie = browser_cookie3.firefox(domain_name=domain)
    elif browser == 'edge':
        cookie = browser_cookie3.edge(domain_name=domain)
    elif browser == 'safari':
        cookie = browser_cookie3.safari(domain_name=domain)
    elif browser == 'opera':
        cookie = browser_cookie3.opera(domain_name=domain)
    elif browser == 'brave':
        cookie = browser_cookie3.brave(domain_name=domain)
    else:
        raise ValueError('Invalid browser specified')

    return cookie
