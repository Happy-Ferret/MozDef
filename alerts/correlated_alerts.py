#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Copyright (c) 2017 Mozilla Corporation

from lib.alerttask import AlertTask
from query_models import SearchQuery, TermMatch, ExistsMatch, PhraseMatch


class AlertCorrelatedIntelNotice(AlertTask):
    def main(self):
        self.parse_config('correlated_alerts.conf', ['url'])

        # look for events in last 15 mins
        search_query = SearchQuery(minutes=15)
        search_query.add_must([
            TermMatch('_type', 'bro'),
            TermMatch('eventsource', 'nsm'),
            TermMatch('category', 'bronotice'),
            ExistsMatch('details.sourceipaddress'),
            PhraseMatch('details.note', 'CrowdStrike::Correlated_Alerts')
        ])
        self.filtersManual(search_query)

        # Search events
        self.searchEventsSimple()
        self.walkEvents()

    # Set alert properties
    def onEvent(self, event):
        category = 'correlatedalerts'
        tags = ['nsm,bro,correlated']
        severity = 'NOTICE'
        hostname = event['_source']['hostname']
        url = self.config.url

        # the summary of the alert is the same as the event
        summary = '{0} {1}'.format(hostname, event['_source']['summary'])

        # Create the alert object based on these properties
        return self.createAlertDict(summary, category, tags, [event], severity=severity, url=url)
