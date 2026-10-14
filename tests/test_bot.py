import copy
import json
import unittest
from datetime import date
from unittest.mock import patch
from jobfinder.bot import title_ok, local_date, schema_job, geography, select, canonical, md, public_url, collect
TODAY = date(2026, 10, 13)

def job(i=1):
    return dict(id=f'greenhouse:test:{i}', company='Test', title='Senior Program Manager', official_url=f'https://job-boards.greenhouse.io/test/jobs/{i}', description='Agile QA delivery', location='USA', posted='2026-10-13', salary='No publicado')

def metrics():
    return dict(applied_excluded=0, seen_excluded=0, reviewed=0, sources_ok=0, unverified=0, errors=[])

def page(**overrides):
    data = {'@type':'JobPosting', 'title':'Program Manager', 'datePosted':'2026-10-13', 'hiringOrganization':{'name':'Test'}, 'description':'Agile', 'jobLocation':{'address':{'addressCountry':'US','addressLocality':'Los Angeles'}}}
    data.update(overrides)
    return '<script type="application/ld+json">' + json.dumps(data) + '</script>'

class CollectorTests(unittest.TestCase):
    def test_requested_titles_and_lead_exclusion(self):
        for t in ('Program Manager','Senior Producer','Technical Program Manager','Delivery Manager','Senior Technical Program Manager – Games','Sr. Technical Program Manager','Marketing Program Manager'):
            self.assertTrue(title_ok(t), t)
        for t in ('Lead Program Manager','Program Manager, Lead','Principal Program Manager','Producer Lead','Associate Producer','Product Manager'):
            self.assertFalse(title_ok(t), t)
    def test_california_day_and_dst(self):
        self.assertEqual(local_date('2026-10-14T00:30:00Z'), TODAY)
        self.assertEqual(local_date('2026-01-02T07:30:00Z'), date(2026,1,1))
        with self.assertRaises(ValueError): local_date('2026-10-13T17:00:00')
        with self.assertRaises(ValueError): local_date(None)
    def test_missing_dates_never_substituted(self):
        with self.assertRaises(ValueError): schema_job(page(datePosted=None), job()['official_url'], TODAY)
        self.assertIsNone(schema_job(page(datePosted='2026-10-12'), job()['official_url'], TODAY))
        self.assertIsNotNone(schema_job(page(), job()['official_url'], TODAY))
    def test_closed_and_ambiguous_pages(self):
        self.assertIsNone(schema_job(page(validThrough='2026-10-12'), job()['official_url'], TODAY))
        self.assertIsNone(schema_job(page()+page(), job()['official_url'], TODAY))
    def test_remote_country_restrictions(self):
        self.assertTrue(geography('Remote Canada',['CA'],True))
        self.assertTrue(geography('Remote Canada'))
        self.assertTrue(geography('Remote Colombia',['CO'],True))
        self.assertFalse(geography('Remote Germany',['DE'],True))
        self.assertTrue(geography('Los Angeles, California'))
        self.assertTrue(geography('Remote',[],True))
        self.assertTrue(geography('Ciudad de México'))
        self.assertIsNone(schema_job(page(jobLocationType='TELECOMMUTE',applicantLocationRequirements={'name':'Germany'}), job()['official_url'], TODAY))
    def test_limit_dedup_applied_seen_and_rerun(self):
        state={'seen':{}}
        candidates=[job(i) for i in range(30)]+[job(5)]
        applied=[{'id':job(0)['id']},{'official_url':job(1)['official_url']}]
        result=select(candidates,state,applied,TODAY,metrics(),{'skills':['Agile','QA']})
        self.assertEqual(len(result),20)
        self.assertEqual(len({x['official_url'] for x in result}),20)
        self.assertNotIn(job(0)['id'],[x['id'] for x in result])
        self.assertNotIn(job(1)['id'],[x['id'] for x in result])
        self.assertEqual(len(select(copy.deepcopy(candidates),state,applied,TODAY,metrics(),{'skills':[]})),20)
        # Applied rows were never marked seen; still exclude them tomorrow.
        self.assertEqual(select(candidates,state,applied,date(2026,10,14),metrics(),{'skills':[]}),[])
    def test_url_identity_and_output_escaping(self):
        self.assertEqual(canonical('https://company.com/jobs?gh_jid=123&utm_source=a'),'https://company.com/jobs?gh_jid=123')
        self.assertNotEqual(canonical('https://company.com/jobs?gh_jid=123'),canonical('https://company.com/jobs?gh_jid=456'))
        self.assertNotIn('<script>',md('<script>alert(1)</script> | [click]'))
        self.assertNotIn('|',md('evil | table'))
    def test_private_urls_refused(self):
        with self.assertRaises(ValueError): public_url('http://company.com/jobs/1',['company.com'])
        with self.assertRaises(ValueError): public_url('https://unknown.com/jobs/1',['company.com'])
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaises(ValueError): public_url('https://company.com/jobs/1',['company.com'])
    def test_greenhouse_updated_at_not_publication(self):
        class Fake:
            def json(self,url):
                if url.endswith('/jobs'): return {'jobs':[dict(id=1,title='Program Manager',absolute_url=job()['official_url'])]}
                return dict(first_published='2026-10-12',updated_at='2026-10-13',title='Program Manager')
            def get(self,url): raise AssertionError('Old job must not be fetched')
        self.assertEqual(collect({'boards':[{'type':'greenhouse','slug':'test','company':'Test'}]},Fake(),TODAY,metrics()),[])
    def test_ashby_last_publication_not_proof(self):
        class Fake:
            def json(self,url): return {'jobs':[dict(title='Program Manager',isListed=True,publishedAt='2026-10-13',jobUrl=job()['official_url'])]}
            def get(self,url): return page(datePosted='2026-10-12'),url
        self.assertEqual(collect({'boards':[{'type':'ashby','slug':'test','company':'Test'}]},Fake(),TODAY,metrics()),[])
    def test_historical_run_preserves_dashboard_and_seen(self):
        import tempfile
        from pathlib import Path
        from jobfinder import bot
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'config').mkdir()
            (root/'data').mkdir()
            (root/'README.md').write_text('Current dashboard')
            (root/'data/state.json').write_text('{"seen": {"existing": {}}}')
            (root/'data/applied.json').write_text('[]')
            (root/'config/sources.json').write_text('{"official_hosts": [], "boards": [{"type":"greenhouse","slug":"test","company":"Test"}]}')
            (root/'config/profile.json').write_text('{"skills": []}')
            def fake_collect(config, client, day, stats):
                stats['sources_ok']=1
                self.assertEqual(day, date(2000,1,1))
                return []
            with patch.object(bot,'ROOT',root), patch.object(bot,'collect',side_effect=fake_collect), patch.object(bot,'linkedin'), patch('sys.argv',['bot','run','--date','2000-01-01']):
                bot.main()
            self.assertEqual((root/'README.md').read_text(),'Current dashboard')
            self.assertEqual((root/'data/state.json').read_text(),'{"seen": {"existing": {}}}')
            self.assertTrue((root/'reports/2000-01-01.json').exists())

    def test_california_has_priority_over_higher_match_elsewhere(self):
        california_job=job(99)
        california_job['location']='Los Angeles, California'
        california_job['description']=''
        other=job(100)
        other['description']='Agile QA delivery'
        chosen=select([other,california_job],{'seen':{}},[],TODAY,metrics(),{'skills':['Agile','QA','delivery']})
        self.assertEqual(chosen[0]['id'],california_job['id'])

    def test_amazon_declared_publication_date_and_identity(self):
        from jobfinder.bot import collect
        entry={'id_icims':'12345','title':'Senior Technical Program Manager','posted_date':'October 13, 2026','location':'US, CA, Sunnyvale','country_code':'USA','job_path':'/en/jobs/12345/senior-technical-program-manager','description':'Agile','preferred_qualifications':'USA, CA, Sunnyvale - 132,000.00 - 154,000.00 USD annually'}
        class Fake:
            def json(self,url): return {'hits':1,'jobs':[entry]}
            def get(self,url): return 'Job 12345',url
        result=collect({'boards':[{'type':'amazon','slug':'amazon','company':'Amazon'}]},Fake(),TODAY,metrics())
        self.assertTrue(result)
        self.assertEqual(result[0]['posted'],'October 13, 2026')
        self.assertIn('132,000',result[0]['salary'])
        entry['posted_date']='October 12, 2026'
        self.assertEqual(collect({'boards':[{'type':'amazon','slug':'amazon','company':'Amazon'}]},Fake(),TODAY,metrics()),[])

if __name__=='__main__': unittest.main()
