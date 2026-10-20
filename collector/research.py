"""Goodscroll 1.5: scholarly metadata collector with source diagnostics and diversity caps.
No AI-invented findings. All summaries are labelled abstract excerpts.
"""
import json, os, re, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta, timezone
from html import unescape
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
TODAY=datetime.now(timezone.utc).date()
UA='Goodscroll/1.5 (noncommercial research discovery; https://github.com/)' 
FIELDS={
 'Psychology':['psycholog','cogniti','behavio','perception','emotion','memory','attention','mental health'],
 'Neuroscience':['neuron','neural','brain','synap','neuroscien'],
 'Biology':['biolog','ecolog','gene','evolution','microbiome','species','animal'],
 'Medicine':['medical','clinic','patient','treatment','health','disease','therapy'],
 'Environment':['climate','carbon','biodiversity','conservation','ecosystem','sustainab'],
 'Technology':['machine learning','artificial intelligence','robot','computer','algorithm','software','digital'],
 'Physics':['physics','astronom','astrophys','quantum','particle','cosmolog'],
 'Society':['education','sociolog','econom','culture','policy','inequal','society'],
 'Design':['design','creativ','architect','human-computer interaction','interface']
}

# Classify using provider-assigned subject metadata first, then title and abstract.
# Titles carry more weight; generic "model", "learning" and "attention" never signal Psychology.
TOPICS={
 'AI & Computing':[r'\b(?:llm|llms|language model|machine learning|deep learning|neural network|transformer|reinforcement learning|generative ai|artificial intelligence|computer vision|multimodal|agentic|agent actions|fine.tuning|lora|model training|foundation model|software|cybersecurity|algorithm|computer.use|robotic process)\b'],
 'Robotics':[r'\b(?:robot|robots|robotic|autonomous navigation|manipulation task)\b'],
 'Creative Technology':[r'\b(?:video generation|image generation|3d generation|creative technolog|procedural generat|generative art|digital storytelling|web design|visual design|creative coding)\b'],
 'Psychology':[r'\b(?:psycholog|human cognition|human behavior|human behaviour|mental health|emotion regulation|personality|psychotherapy|psychometric|human perception)\b'],
 'Neuroscience':[r'\b(?:neuroscien|cerebral|brain|neuron|synap|fMRI|EEG|neural circuit)\b'],
 'Medicine':[r'\b(?:patient|clinical trial|hospital|treatment|cancer|vaccine|disease|diagnos|public health|medical|healthcare)\b'],
 'Biology':[r'\b(?:protein|genomic|gene expression|bacteri|organism|ecolog|microbiome|evolution|cellular|species|biolog)\b'],
 'Environment':[r'\b(?:climate|biodiversity|conservation|ecosystem|pollution|carbon emissions|renewable energy|habitat|environmental)\b'],
 'Engineering':[r'\b(?:engineering|semiconductor|battery|materials science|manufacturing|electrical circuit|mechanical design|aerospace)\b'],
 'Physics':[r'\b(?:astrophys|quantum|cosmolog|particle physics|astronom|gravitational|condensed matter|optics)\b'],
 'Design':[r'\b(?:design thinking|industrial design|user experience|human.computer interaction|architecture|interface design|design research)\b'],
 'Business':[r'\b(?:leadership|management|marketing|entrepreneur|organizational|corporate|consumer behavior|business strategy)\b'],
 'Society':[r'\b(?:sociolog|education|inequality|social policy|public policy|demograph|community|political science|ethnograph)\b']
}
ARXIV_TOPICS={'cs.AI':'AI & Computing','cs.CL':'AI & Computing','cs.LG':'AI & Computing','cs.CV':'AI & Computing','cs.HC':'Design','cs.RO':'Robotics','cs.CR':'AI & Computing','cs.SE':'AI & Computing','q-bio.NC':'Neuroscience','q-bio.MN':'Biology','physics.soc-ph':'Physics','astro-ph.EP':'Physics'}
OPENALEX_MAP={'computer science':'AI & Computing','artificial intelligence':'AI & Computing','psychology':'Psychology','neuroscience':'Neuroscience','medicine':'Medicine','biology':'Biology','environmental science':'Environment','engineering':'Engineering','physics and astronomy':'Physics','social sciences':'Society','business, management and accounting':'Business','arts and humanities':'Design'}

def classification(title,abstract='',source_topics=None,venue=''):
 title=str(title or '').lower(); abstract=str(abstract or '').lower(); primary_meta=[str(x).lower() for x in (source_topics or [])]
 scores={k:0 for k in TOPICS}
 for name,patterns in TOPICS.items():
  for pat in patterns:
   if re.search(pat,title,re.I):scores[name]+=6
   if re.search(pat,abstract[:2000],re.I):scores[name]+=1
 for raw in primary_meta:
  for code,name in ARXIV_TOPICS.items():
   if raw==code.lower():scores[name]+=12
  for term,name in OPENALEX_MAP.items():
   if term==raw or term in raw:scores[name]+=7
 # Explicit AI/robot terms override ambiguous generic cognitive vocabulary.
 if re.search(r'\b(?:llm|language model|transformer|agentic|multimodal|deep learning|reinforcement learning|agent actions|lora|fine.tuning)\b',title):scores['AI & Computing']+=12
 if re.search(r'\b(?:robot|robotics|multi.robot)\b',title):scores['Robotics']+=14
 ordered=sorted(scores,key=lambda x:(-scores[x],list(TOPICS).index(x)))
 tags=[x for x in ordered if scores[x]>=4][:4]
 if not tags:return 'Other',['Other'],0
 return tags[0],tags,round(min(1,scores[tags[0]]/20),2)

def sentence_list(text):
 text=clean(text)
 return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[A-Z(])',text) if len(x.strip())>=28]

def evidence_excerpt(sentences,patterns):
 for sentence in sentences:
  if any(re.search(p,sentence,re.I) for p in patterns):return sentence[:680]
 return ''

def explain(p):
 abstract=p.get('abstract','') or ''; title=p.get('title','') or ''; sentences=sentence_list(abstract)
 objective=evidence_excerpt(sentences,[r'\b(?:we investigate|we examine|we study|we explore|this study aims|the aim|we ask|our objective|this paper (?:investigates|examines|explores))\b'])
 method=evidence_excerpt(sentences,[r'\b(?:we (?:conducted|surveyed|evaluated|tested|analysed|analyzed)|participants|patients|dataset|experiment|trial|interview|systematic review|meta.analysis|retrospective|simulation)\b'])
 findings=evidence_excerpt(sentences,[r'\b(?:we find|we found|results (?:show|indicate|suggest)|our findings|we demonstrate|the results|we observed|was associated|improved by|increased by|decreased by)\b'])
 limitation=evidence_excerpt(sentences,[r'\b(?:limitation|caution|however|future research|further studies|cannot|small sample|uncertain|not generaliz)\b'])
 # Extractive evidence: snippets stay traceable to abstract, never supplied as independently validated findings.
 return {'question':objective,'method':method,'findings':findings,'limitations':limitation,
 'why_it_matters':'This paper addresses '+(p.get('category') or 'research').lower()+' questions. Read the abstract and original study to assess its relevance.',
 'basis':'extractive_abstract','has_explicit_findings':bool(findings)}

def enrich(p):
 oldcat=p.get('category','Other')
 p['category'],p['topics'],p['category_confidence']=classification(p.get('title'),p.get('abstract'),p.get('source_topics'),p.get('venue'))
 if p['category']=='Other' and oldcat!='Other':
  p['category']=oldcat if oldcat not in ('Technology',) else 'AI & Computing'
  p['topics']=[p['category']]
  p['category_confidence']=.15
 p['explanation']=explain(p)
 p['quality_flags']=([ 'abstract_missing' ] if len(p.get('abstract',''))<100 else [])+(['category_uncertain'] if p['category_confidence']<.45 else [])+(['doi_missing'] if not p.get('doi') else [])+(['findings_not_explicit_in_abstract'] if not p['explanation']['has_explicit_findings'] else [])
 return p

FETCH_STATS={}
def fetch(url,provider):
 start=time.monotonic()
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json, application/atom+xml, */*'})
 try:
  with urllib.request.urlopen(req,timeout=35) as r:
   body=r.read();FETCH_STATS.setdefault(provider,[]).append({'status':r.status,'bytes':len(body),'elapsed_ms':round((time.monotonic()-start)*1000)})
   return body
 except Exception as e:
  FETCH_STATS.setdefault(provider,[]).append({'error':str(e)[:180]});raise

def clean(x):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',str(x or '')))).strip()
def discipline(text,source_label=''):
 s=(text+' '+source_label).lower();scores={name:sum(1 for term in terms if term in s) for name,terms in FIELDS.items()}
 best=max(scores,key=scores.get);return best if scores[best] else 'Other'
def normaldoi(x):
 x=str(x or '').strip();return re.sub(r'^https?://(?:dx\.)?doi\.org/','',x,flags=re.I).lower()
def record(title,abstract,date,url,authors,venue,provider,doi='',status='Review status unverified',oa=False,referenced=None,openalex_id=''):
 title=clean(title);abstract=clean(abstract);date=str(date or '')[:10]
 if not title or len(title)<18 or not url or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):return None
 if date>TODAY.isoformat():return None
 key=normaldoi(doi) or url.strip().lower()
 return {'id':key,'title':title,'abstract':abstract[:9000],'date':date,'url':url,'authors':[clean(a) for a in authors if a][:8],
 'venue':clean(venue),'provider':provider,'doi':normaldoi(doi),'publication_type':status,
 'category':discipline(title+' '+abstract[:1400],venue),'source_topics':[],'open_access':bool(oa),
 'references':list(dict.fromkeys(referenced or []))[:120],'openalex_id':openalex_id,
 'summary_basis':'abstract_metadata_only','insight':'Research discovery: this is a description from publication metadata, not an independently verified account of findings.'}
def reconstruct(inv):
 if not isinstance(inv,dict):return ''
 pairs=sorted((p,w) for w,positions in inv.items() for p in positions if isinstance(p,int))
 return ' '.join(w for _,w in pairs)
def openalex():
 out=[];start=(TODAY-timedelta(days=60)).isoformat()
 # Sample by subject rather than letting the newest single discipline dominate.
 queries=['psychology cognition','ecology biodiversity','health medicine','artificial intelligence','social science education','physics astronomy','design human computer interaction']
 for q in queries:
  params={'filter':f'from_publication_date:{start},has_abstract:true','search':q,'sort':'publication_date:desc','per_page':'35'}
  if os.getenv('OPENALEX_API_KEY'):params['api_key']=os.environ['OPENALEX_API_KEY']
  if os.getenv('OPENALEX_EMAIL'):params['mailto']=os.environ['OPENALEX_EMAIL']
  data=json.loads(fetch('https://api.openalex.org/works?'+urllib.parse.urlencode(params),'OpenAlex'))
  for w in data.get('results',[]):
   loc=w.get('primary_location') or {};src=loc.get('source') or {};doi=w.get('doi') or ''
   r=record(w.get('title'),reconstruct(w.get('abstract_inverted_index')),w.get('publication_date'),doi or w.get('id'),[a.get('author',{}).get('display_name','') for a in w.get('authorships',[])],src.get('display_name',''),'OpenAlex',doi,'Journal article / research work — verify review status',bool((w.get('open_access') or {}).get('is_oa')),[ref for ref in w.get('referenced_works',[]) if ref],w.get('id',''))
   if r:
    concepts=[t.get('display_name','') for t in (w.get('topics') or [])[:3]]
    concepts += [x.get('display_name','') for x in (w.get('primary_topic') or {}).get('field',{}).values() if isinstance(x,str)] if False else []
    primary=(w.get('primary_topic') or {}).get('field') or {}
    if primary.get('display_name'):concepts.insert(0,primary['display_name'])
    r['source_topics']=concepts
    out.append(r)
  time.sleep(.25)
 return out

def crossref():
 start=(TODAY-timedelta(days=90)).isoformat();out=[]
 for q in ['psychology cognition','conservation biodiversity','health neuroscience','education society']:
  params={'filter':f'from-pub-date:{start},type:journal-article','query.title':q,'rows':'45','select':'DOI,title,abstract,author,container-title,published,URL,type,reference,license'}
  data=json.loads(fetch('https://api.crossref.org/works?'+urllib.parse.urlencode(params),'Crossref'))
  for w in data.get('message',{}).get('items',[]):
   parts=(w.get('published') or {}).get('date-parts',[[None]])[0]
   if len(parts)<3:continue
   date=f'{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}'
   doi=w.get('DOI','');refs=[normaldoi(x.get('DOI')) for x in w.get('reference',[]) if x.get('DOI')]
   r=record((w.get('title') or [''])[0],w.get('abstract',''),date,'https://doi.org/'+doi if doi else w.get('URL'),[(x.get('given','')+' '+x.get('family','')).strip() for x in w.get('author',[])],(w.get('container-title') or [''])[0],'Crossref',doi,'Journal article — peer review not independently verified',False,refs)
   if r and len(r['abstract'])>=100:out.append(r)
  time.sleep(.25)
 return out

def arxiv():
 out=[];ns={'a':'http://www.w3.org/2005/Atom'}
 for q in ['cat:cs.AI OR cat:cs.HC','cat:q-bio.NC OR cat:q-bio.MN','cat:physics.soc-ph OR cat:astro-ph.EP']:
  params={'search_query':q,'start':0,'max_results':45,'sortBy':'submittedDate','sortOrder':'descending'}
  root=ET.fromstring(fetch('https://export.arxiv.org/api/query?'+urllib.parse.urlencode(params),'arXiv'))
  for e in root.findall('a:entry',ns):
   get=lambda tag:(e.findtext('a:'+tag,default='',namespaces=ns) or '').strip()
   authors=[x.findtext('a:name',default='',namespaces=ns) for x in e.findall('a:author',ns)]
   r=record(get('title'),get('summary'),get('published')[:10],get('id'),authors,'arXiv','arXiv',status='Preprint — peer review not established',oa=True)
   if r:
    r['source_topics']=[x.attrib.get('term','') for x in e.findall('{http://arxiv.org/schemas/atom}primary_category')+e.findall('{http://arxiv.org/schemas/atom}category')]
    out.append(r)
  time.sleep(2.5)
 return out

def europepmc():
 out=[];start=(TODAY-timedelta(days=90)).isoformat()
 for terms in ['NEUROSCIENCE','ECOLOGY','PSYCHOLOGY','PUBLIC HEALTH']:
  params={'query':f'FIRST_PDATE:[{start} TO {TODAY.isoformat()}] AND HAS_ABSTRACT:Y AND {terms}','format':'json','pageSize':60,'resultType':'core','sort':'FIRST_PDATE_D desc'}
  data=json.loads(fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(params),'Europe PMC'))
  for w in data.get('resultList',{}).get('result',[]):
   doi=w.get('doi','');pmid=w.get('id','');url='https://doi.org/'+doi if doi else 'https://europepmc.org/article/'+w.get('source','MED')+'/'+pmid
   authors=[a.get('fullName','') for a in (w.get('authorList') or {}).get('author',[]) if a.get('fullName')]
   r=record(w.get('title'),w.get('abstractText'),w.get('firstPublicationDate') or w.get('firstIndexDate'),url,authors,(w.get('journalInfo') or {}).get('journal',{}).get('title') or w.get('journalTitle',''),'Europe PMC',doi,'Biomedical record — verify article type and peer review',bool(w.get('isOpenAccess')=='Y'))
   if r and len(r['abstract'])>=100:out.append(r)
  time.sleep(.25)
 return out

def key(item):return normaldoi(item.get('doi')) or item.get('url','').strip().lower()
def main():
 output=ROOT/'app/data';output.mkdir(exist_ok=True,parents=True);path=output/'feed.json';existing=[]
 if path.exists():
  try:existing=json.loads(path.read_text(encoding='utf-8')).get('items',[])
  except (OSError,ValueError):pass
 collected=[];counts={};errors={};diagnostics={}
 for name,func in [('OpenAlex',openalex),('Crossref',crossref),('arXiv',arxiv),('Europe PMC',europepmc)]:
  try:result=func();counts[name]=len(result);collected+=result
  except Exception as ex:errors[name]=str(ex)[:300];counts[name]=0
  diagnostics[name]={'accepted_before_dedup':counts[name],'requests':FETCH_STATS.get(name,[]),'error':errors.get(name)}
  time.sleep(1)
 merged={}
 for p in existing+collected:
  if not isinstance(p,dict) or not p.get('url') or not p.get('title') or not p.get('date'):continue
  k=key(p)
  if not k:continue
  if k not in merged:merged[k]=p.copy()
  else:
   previous=merged[k]
   if len(p.get('abstract',''))>len(previous.get('abstract','')):
    # Keep the richer abstract, preserve citation metadata when possible.
    p=p.copy();p['references']=list(dict.fromkeys(previous.get('references',[])+p.get('references',[])))[:120]
    p['openalex_id']=p.get('openalex_id') or previous.get('openalex_id','');merged[k]=p
   else:
    previous['references']=list(dict.fromkeys(previous.get('references',[])+p.get('references',[])))[:120]
    previous['openalex_id']=previous.get('openalex_id') or p.get('openalex_id','')
 # Preserve a full unique count and enrich records without asserting review status.
 unique_before_caps=len(merged)
 for pp in merged.values():
  enrich(pp)
  pp['summary_basis']='abstract_metadata_only' if pp.get('abstract') else 'title_metadata_only'
  pp['evidence_label']=('Preprint / not necessarily peer reviewed' if 'preprint' in pp.get('publication_type','').lower() else 'Publication record / review unverified')
  pp['has_abstract']=bool(len(pp.get('abstract','').strip())>=100)
  pp['has_doi']=bool(pp.get('doi'))
  pp['has_citation_metadata']=bool(pp.get('references'))
 allpapers=sorted(merged.values(),key=lambda x:x.get('date',''),reverse=True)

 # Restrict domination from any one category, while preserving reasonable evergreen history.
 seen=Counter();final=[]
 for p in allpapers:
  cat=p.get('category','Other')
  if seen[cat]>=240:continue
  if len(final)>=1600:break
  seen[cat]+=1;final.append(p)
 if final:path.write_text(json.dumps({'items':final},ensure_ascii=False,indent=2),encoding='utf-8')
 def age_days(p):
  try:return (TODAY-datetime.strptime(p['date'],'%Y-%m-%d').date()).days
  except (ValueError, KeyError, TypeError):return 999999
 quality={
  'with_abstract':sum(bool(p.get('has_abstract')) for p in final),
  'without_abstract':sum(not p.get('has_abstract') for p in final),
  'with_doi':sum(bool(p.get('has_doi')) for p in final),
  'with_open_access_indicator':sum(bool(p.get('open_access')) for p in final),
  'with_citation_metadata':sum(bool(p.get('has_citation_metadata')) for p in final),
  'preprints':sum('preprint' in p.get('publication_type','').lower() for p in final),
  'last_7_days':sum(0<=age_days(p)<=7 for p in final),
  'last_30_days':sum(0<=age_days(p)<=30 for p in final),
  'last_90_days':sum(0<=age_days(p)<=90 for p in final),
  'duplicate_or_replaced_candidates':max(0,len(existing)+len(collected)-unique_before_caps),
  'excluded_by_category_or_total_caps':unique_before_caps-len(final),
  'classification_uncertain':sum('category_uncertain' in p.get('quality_flags',[]) for p in final),
  'without_explicit_findings':sum(not p.get('explanation',{}).get('has_explicit_findings') for p in final),
  'by_primary_topic':dict(Counter(p.get('category','Other') for p in final)),
  'note':'Metrics describe metadata quality, not independent verification of scientific findings or peer review.'
 }
 previous_keys={key(p) for p in existing if isinstance(p,dict)}
 health={'version':'1.5.0','updated_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'items':len(final),'new_records':len(collected),'new_unique_vs_previous':sum(key(p) not in previous_keys for p in final),'sources':counts,'errors':errors,'fallback_retained':bool(errors),'by_category':dict(Counter(p.get('category','Other') for p in final)),'quality_flags':dict(Counter(flag for p in final for flag in p.get('quality_flags',[]))),'quality':quality,'diagnostics':diagnostics,'note':'Source counts are accepted pre-dedup. Research summaries are metadata-grounded excerpts, not independently verified findings.'}
 (output/'health.json').write_text(json.dumps(health,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in health.items() if k!='diagnostics'},indent=2))
 if not final:print('Feed is empty; source errors and diagnostics are in health.json')
if __name__=='__main__':main()
