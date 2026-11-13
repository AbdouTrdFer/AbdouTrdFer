"""Check metric integrity and unavailable-data behavior, without network calls."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('activity',ROOT/'scripts/update_activity.py')
activity=importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)

def graphql_response():
    return {'data':{'user':{'followers':{'totalCount':7},'repositories':{'totalCount':12},'contributionsCollection':{
        'startedAt':'2025-11-13T00:00:00Z','endedAt':'2026-11-13T00:00:00Z',
        'totalCommitContributions':4,'totalPullRequestContributions':2,
        'totalPullRequestReviewContributions':1,'totalIssueContributions':1,
        'contributionCalendar':{'totalContributions':10,'weeks':[{'contributionDays':[
            {'date':'2026-11-12','contributionCount':4},{'date':'2026-11-13','contributionCount':6}]}]}
    }}}}

class ActivityTests(unittest.TestCase):
    def collect(self,response=None):
        with patch.object(activity,'request',return_value=json.dumps(response or graphql_response())),patch.object(activity,'api',return_value=[]):
            return activity.collect('test-token')

    def test_ring_matches_total_and_does_not_add_pushes(self):
        data=self.collect()
        self.assertEqual(data['other'],2)
        self.assertEqual(sum(data[k] for k in ['commits','prs','reviews','issues','other']),data['total'])
        self.assertEqual(data['pushes'],0)
        ET.fromstring(activity.render(data))
        ET.fromstring(activity.render_mobile(data))

    def test_bad_graphql_response_rejected(self):
        with self.assertRaises(ValueError):
            self.collect({'errors':[{'message':'Unavailable'}]})

    def test_inconsistent_breakdown_rejected(self):
        response=graphql_response()
        response['data']['user']['contributionsCollection']['totalCommitContributions']=100
        with self.assertRaises(ValueError):
            self.collect(response)

    def test_missing_push_feed_is_not_zero(self):
        with patch.object(activity,'request',return_value=json.dumps(graphql_response())),patch.object(activity,'api',side_effect=OSError('offline')):
            data=activity.collect('test-token')
        self.assertIsNone(data['pushes'])
        self.assertEqual(data['total'],10)

    def test_zero_activity_renders_without_division_error(self):
        data=self.collect()
        for k in ['total','commits','prs','reviews','issues','other']:
            data[k]=0
        data['days']=[{'date':'2026-11-13','count':0}]
        ET.fromstring(activity.render(data))
        ET.fromstring(activity.render_mobile(data))

    def test_calendar_parses_counts_and_sort_order(self):
        source='''<td data-date="2026-11-13" data-level="2" id="b"></td>
          <td data-date="2026-11-12" data-level="0" id="a"></td>
          <tool-tip for="a">No contributions on November 12th.</tool-tip>
          <tool-tip for="b">12 contributions on November 13th.</tool-tip>'''
        days=activity.public_calendar(source)
        self.assertEqual([d['count'] for d in days],[0,12])
        with self.assertRaises(ValueError):
            activity.public_calendar('<td data-date="2026-11-13" data-level="2" id="b"></td>')

    def test_feed_pagination_deduplication_cap_and_age(self):
        now=activity.datetime.now(activity.timezone.utc).isoformat()
        batch=[{'id':str(i),'type':'PushEvent','created_at':now} for i in range(100)]
        with patch.object(activity,'request',return_value=json.dumps(graphql_response())),patch.object(activity,'api',side_effect=[batch,batch,[]]) as api:
            data=activity.collect('test-token')
        self.assertEqual(api.call_count,3)
        self.assertEqual(data['pushes'],100)
        old={'id':'old','type':'PushEvent','created_at':'2000-01-01T00:00:00Z'}
        batches=[[{'id':str(i),'type':'PushEvent','created_at':now} for i in range(n,n+100)] for n in [0,100,200]]
        batches[2][-1]=old
        with patch.object(activity,'request',return_value=json.dumps(graphql_response())),patch.object(activity,'api',side_effect=batches):
            data=activity.collect('test-token')
        self.assertTrue(data['events_capped'])
        self.assertEqual(data['pushes'],299)

    def test_committed_artwork_and_snapshot(self):
        data=json.loads((ROOT/'data/activity.json').read_text(encoding='utf-8'))
        self.assertTrue(data['days'])
        self.assertEqual(sum(d['count'] for d in data['days']),data['total'])
        for path in (ROOT/'assets').glob('*.svg'):
            ET.parse(path)
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        for path in activity.re.findall(r'(?:src|srcset)="\./([^"]+)"',readme):
            self.assertTrue((ROOT/path).exists(),path)

if __name__=='__main__':
    unittest.main()
