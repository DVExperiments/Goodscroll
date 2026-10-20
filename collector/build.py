"""Goodscroll collector. Uses public endpoints conservatively; never invents image rights."""
import json, os, pathlib, datetime, urllib.request, urllib.parse, re, html, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'app'/'data';OUT.mkdir(exist_ok=True)
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat();UA='Goodscroll/1.0 (open source discovery app; contact via repository issues)'
def request(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=14) as r:return json.load(r)
def text(s):return re.sub(r'<[^>]+>','',html.unescape(str(s or ''))).strip()
def item(source,key,title,summary,pillar,url,media=None):
    if not title or not summary or not url:return None
    x={'id':source+'-'+str(key),'type':'discovery','pillar':pillar,'title':text(title)[:130],'summary':text(summary)[:440],'source':{'name':source,'url':url},'quality_score':82,'read_time':'A quick discovery'}
    if media:x['media']=media
    return x
def nasa():
    key=os.getenv('NASA_API_KEY','DEMO_KEY');j=request('https://api.nasa.gov/planetary/apod?'+urllib.parse.urlencode({'api_key':key,'count':5}))
    if isinstance(j,dict):j=[j]
    out=[]
    for v in j:
        media=None
        if v.get('media_type')=='image' and v.get('url','').startswith('https://'):
            media={'url':v['url'],'alt':v.get('title','Space image'),'creator':v.get('copyright','NASA / APOD'),'license':'See NASA media guidelines'}
        x=item('NASA APOD',v.get('date','today'),v.get('title'),v.get('explanation'),'Wonder',v.get('hdurl') or v.get('url') or 'https://apod.nasa.gov/apod/',media)
        if x:out.append(x)
    return out
def met():
    # API v1.1: search result shapes may vary; guard rather than guess.
    j=request('https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q=flower')
    ids=j.get('objectIDs') or []
    out=[]
    for oid in ids[:10]:
        try:
            o=request('https://collectionapi.metmuseum.org/public/collection/v1/objects/'+str(oid))
            if not o.get('isPublicDomain') or not o.get('primaryImageSmall'):continue
            media={'url':o['primaryImageSmall'],'alt':o.get('title','Artwork'),'creator':o.get('artistDisplayName') or 'The Metropolitan Museum of Art','license':'Public domain'}
            x=item('The Met',oid,o.get('title'),f"{o.get('objectDate','')} · {o.get('medium','Artwork')}. Discover this object from The Met's Open Access collection.",'Creativity',o.get('objectURL'),media)
            if x:out.append(x)
        except Exception:continue
        if len(out)>=4:break
    return out
def wikimedia():
    # MediaWiki API returns file usage information; keep rights/creator attribution conservative.
    url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','generator':'categorymembers','gcmtitle':'Category:Featured_pictures_of_animals','gcmtype':'file','gcmlimit':12,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1000,'format':'json','origin':'*'})
    j=request(url);out=[]
    for p in j.get('query',{}).get('pages',{}).values():
        info=(p.get('imageinfo') or [{}])[0];meta=info.get('extmetadata') or {};license_=text(meta.get('LicenseShortName',{}).get('value',''))
        creator=text(meta.get('Artist',{}).get('value',''))
        img=info.get('thumburl');title=p.get('title','').replace('File:','').rsplit('.',1)[0].replace('_',' ')
        if not img or not license_ or not creator:continue
        media={'url':img,'alt':title,'creator':creator[:130],'license':license_}
        x=item('Wikimedia Commons',p.get('pageid'),title,'A featured animal photograph from Wikimedia Commons. Explore the original file to discover its story and creator.','Joy',info.get('descriptionurl'),media)
        if x:out.append(x)
        if len(out)>=5:break
    return out
def main():
    seed=json.loads((ROOT/'content'/'seed.json').read_text());existing=OUT/'feed.json';previous=[]
    if existing.exists():
        try:previous=json.loads(existing.read_text()).get('items',[])
        except Exception:pass
    fresh=[];results={}
    for name,fn in [('nasa',nasa),('met',met),('wikimedia',wikimedia)]:
        try:
            new=fn();fresh.extend(new);results[name]={'status':'ok' if new else 'empty','items':len(new)}
        except Exception as exc:results[name]={'status':'failed','items':0,'error':str(exc)[:160]}
    combined=[];seen=set()
    for x in fresh+previous+seed:
        if not x.get('id') or x['id'] in seen:continue
        if x.get('pillar') not in ['Joy','Wonder','Creativity','Calm','Play']:continue
        if not x.get('title') or not x.get('summary'):continue
        seen.add(x['id']);combined.append(x)
    combined=combined[:350]
    # If all collectors fail, preserve prior valid content plus curated seeds.
    (OUT/'feed.json').write_text(json.dumps({'updated_at':NOW,'items':combined},ensure_ascii=False,indent=2))
    health={'updated_at':NOW,'published_items':len(combined),'new_collected':len(fresh),'seed_items':len(seed),'source_results':results}
    (OUT/'health.json').write_text(json.dumps(health,indent=2));print(json.dumps(health,indent=2))
if __name__=='__main__':main()
