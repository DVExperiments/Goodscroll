"""Goodscroll research metadata collector. Stdlib only; graceful per-provider failures."""
import json, os, re, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta, timezone
from html import unescape
ROOT=Path(__file__).resolve().parents[1]
UA='GoodscrollResearch/1.1 (public research discovery; contact via GitHub repository)'
TOPICS={'Technology':['artificial intelligence','machine learning','robot','computer','software','quantum computing'],'Psychology':['psychology','cognition','behaviour','behavior','perception','memory','emotion'],'Biology':['biology','ecology','genetics','evolution','microbiome'],'Medicine':['medicine','clinical','therapy','health','patient'],'Environment':['climate','sustainability','conservation','biodiversity','environment'],'Physics':['physics','astronomy','astrophysics','quantum','particle'],'Society':['education','sociology','economics','culture','policy']}
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json, application/atom+xml, */*'})
 with urllib.request.urlopen(req,timeout=25) as r:return r.read()
def clean(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',s or ''))).strip()
def category(text):
 t=text.lower();counts={k:sum(t.count(w) for w in words) for k,words in TOPICS.items()};best=max(counts,key=counts.get);return best if counts[best] else 'Other'
def record(title,abstract,date,url,authors,venue,provider,doi='',status='Research record'):
 title=clean(title);abstract=clean(abstract)
 if not title or not url or not date:return None
 if date>datetime.now(timezone.utc).date().isoformat():return None
 if len(title)<20:return None
 key=(doi or url).lower().strip();return dict(id=key,title=title,abstract=abstract,date=date[:10],url=url,authors=authors[:8],venue=venue,provider=provider,doi=doi,publication_type=status,category=category(title+' '+abstract),insight='A recently published research record. Read its abstract, methods and limitations to understand what the authors actually found.')
def openalex():
 start=(datetime.now(timezone.utc)-timedelta(days=21)).date().isoformat();params={'filter':f'from_publication_date:{start},has_abstract:true','sort':'publication_date:desc','per_page':'100'}
 if os.getenv('OPENALEX_API_KEY'):params['api_key']=os.environ['OPENALEX_API_KEY']
 data=json.loads(fetch('https://api.openalex.org/works?'+urllib.parse.urlencode(params)));out=[]
 for w in data.get('results',[]):
  inv=w.get('abstract_inverted_index') or {};words={pos:word for word,positions in inv.items() for pos in positions};abstract=' '.join(words[i] for i in sorted(words))
  loc=w.get('primary_location') or {};source=loc.get('source') or {};doi=w.get('doi') or ''
  r=record(w.get('title'),abstract,w.get('publication_date'),doi or w.get('id'),[a.get('author',{}).get('display_name','') for a in w.get('authorships',[])],source.get('display_name',''),'OpenAlex',doi,'Research work (review status not verified)')
  if r:out.append(r)
 return out
def crossref():
 start=(datetime.now(timezone.utc)-timedelta(days=14)).date().isoformat();params={'filter':f'from-pub-date:{start},type:journal-article','sort':'published','order':'desc','rows':'80','select':'DOI,title,abstract,author,container-title,published,URL,type'}
 data=json.loads(fetch('https://api.crossref.org/works?'+urllib.parse.urlencode(params)));out=[]
 for w in data.get('message',{}).get('items',[]):
  parts=(w.get('published') or {}).get('date-parts',[[None]])[0];date='-'.join(str(v).zfill(2) if i else str(v) for i,v in enumerate(parts));doi=w.get('DOI','');url='https://doi.org/'+doi if doi else w.get('URL','')
  r=record((w.get('title') or [''])[0],w.get('abstract',''),date,url,[((x.get('given','')+' '+x.get('family','')).strip()) for x in w.get('author',[])],(w.get('container-title') or [''])[0],'Crossref',doi,'Journal article (review status not verified)')
  if r and r['abstract']:out.append(r)
 return out
def arxiv():
 # arXiv's export API supports Atom; respect slow query and its usage policies.
 params={'search_query':'cat:cs.AI OR cat:cs.HC OR cat:q-bio.NC OR cat:physics.pop-ph','start':'0','max_results':'50','sortBy':'submittedDate','sortOrder':'descending'}
 root=ET.fromstring(fetch('https://export.arxiv.org/api/query?'+urllib.parse.urlencode(params)));ns={'a':'http://www.w3.org/2005/Atom'};out=[]
 for e in root.findall('a:entry',ns):
  get=lambda tag:(e.findtext('a:'+tag,default='',namespaces=ns) or '').strip();authors=[x.findtext('a:name',default='',namespaces=ns) for x in e.findall('a:author',ns)];url=get('id');date=get('published')[:10]
  r=record(get('title'),get('summary'),date,url,authors,'arXiv','arXiv',status='Preprint — peer review not established')
  if r:out.append(r)
 return out
def europepmc():
 # Public Europe PMC REST API; records with abstracts and recent first-publication dates.
 start=(datetime.now(timezone.utc)-timedelta(days=45)).date().isoformat()
 params={'query':f'FIRST_PDATE:[{start} TO *] AND HAS_ABSTRACT:Y','format':'json','pageSize':'100','sort':'FIRST_PDATE_D desc','resultType':'core'}
 data=json.loads(fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(params)));out=[]
 for w in data.get('resultList',{}).get('result',[]):
  doi=w.get('doi','');pmid=w.get('id','');url=('https://doi.org/'+doi) if doi else ('https://europepmc.org/article/'+w.get('source','MED')+'/'+pmid)
  authors=[a.get('fullName','') for a in (w.get('authorList') or {}).get('author',[]) if a.get('fullName')]
  r=record(w.get('title',''),w.get('abstractText',''),w.get('firstPublicationDate') or w.get('firstIndexDate',''),url,authors,w.get('journalTitle',''),'Europe PMC',doi,'Research record (review status not verified)')
  if r and r['abstract']:out.append(r)
 return out
def main():
 output=ROOT/'app/data';output.mkdir(exist_ok=True,parents=True);old=output/'feed.json';existing=[]
 if old.exists():
  try:existing=json.loads(old.read_text()).get('items',[])
  except Exception:pass
 results=[];stats={};errors={}
 for name,fn in [('OpenAlex',openalex),('Crossref',crossref),('arXiv',arxiv),('Europe PMC',europepmc)]:
  try:
   items=fn();results.extend(items);stats[name]=len(items)
  except Exception as e:errors[name]=str(e)[:250];stats[name]=0
  time.sleep(1)
 # Preserve previously verified papers on transient API failures.
 allitems={}
 for item in existing+results:
  if not item.get('url') or not item.get('title') or not item.get('date'):continue
  key=(item.get('doi') or item['url']).lower().replace('https://doi.org/','').replace('http://doi.org/','')
  if key not in allitems or len(item.get('abstract',''))>len(allitems[key].get('abstract','')):allitems[key]=item
 final=sorted(allitems.values(),key=lambda x:x.get('date',''),reverse=True)[:1200]
 if final:old.write_text(json.dumps({'items':final},ensure_ascii=False,indent=2))
 health={'updated_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'items':len(final),'new_records':len(results),'sources':stats,'errors':errors,'fallback_retained':bool(errors)}
 (output/'health.json').write_text(json.dumps(health,indent=2));print(json.dumps(health,indent=2))
 if not final:print('No records available; catalogue remains empty until first successful collection.')
if __name__=='__main__':main()
