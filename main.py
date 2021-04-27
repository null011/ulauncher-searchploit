import re
import subprocess
import json

from os import path
from types import SimpleNamespace

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction


icon = 'images/icon.png'


class IPsExtension(Extension):

    def __init__(self):
        super(IPsExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def searchsploit(self, query, ss_path):

        results = []

        ss = path.join(ss_path, 'searchsploit')

        args = [
            ss,
            '--json',
            query
        ]

        try:
            results = json.loads(subprocess.check_output(args, timeout=5))
        except Exception as e:
            return results

        return results


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):

        query = event.get_argument()

        if not query:
            return RenderResultListAction([
                ExtensionResultItem(
                    name="Search '%s'" % query,
                    description='No results. Try searching something else :)',
                    icon=icon,
                    on_enter=DoNothingAction()
                )
            ])

        results = []

        ss_results = extension.searchsploit(
            query, extension.preferences['ss_path'])

        if not ss_results['RESULTS_EXPLOIT']:
            return RenderResultListAction([
                ExtensionResultItem(
                    name="Search '%s'" % query,
                    description='No results. Try searching something else :)',
                    icon=icon,
                    on_enter=DoNothingAction()
                )
            ])

        for i in ss_results['RESULTS_EXPLOIT'][0:11]:

            copy_cmd = "searchsploit -m {}".format(i['Path'])
            description = "Date: {Date} EDB-ID: {EDB-ID} Author: {Author} Platform: {Platform}".format(
                **i)

            results.append(
                ExtensionResultItem(
                    name=i['Title'],
                    description=description,
                    icon=icon,
                    on_enter=CopyToClipboardAction(text=copy_cmd)
                )
            )

        return RenderResultListAction(results)


if __name__ == '__main__':
    IPsExtension().run()
