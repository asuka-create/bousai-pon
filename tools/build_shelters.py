# 国土地理院の相模原市CSV（14150_1.csv=指定避難所, 14150_2.csv=指定緊急避難場所）から shelters-sagamihara.js を作る
# 使い方: python tools/build_shelters.py <CSVのあるフォルダ> shelters-sagamihara.js
import csv,json,sys,re
d,out=sys.argv[1],sys.argv[2]
a=list(csv.DictReader(open(d+'/14150_1.csv',encoding='utf-8-sig')))   # 指定避難所
b=list(csv.DictReader(open(d+'/14150_2.csv',encoding='utf-8-sig')))   # 指定緊急避難場所
HZ=[('洪水','f'),('崖崩れ、土石流及び地滑り','d'),('地震','e'),('大規模な火事','k'),('内水氾濫','n'),('津波','t'),('高潮','s'),('火山現象','v')]
def short(n): return re.sub(r'^相模原市立','',n.strip())
def ward(addr):
    m=re.search(r'相模原市(緑区|中央区|南区)',addr)
    return m.group(1) if m else '市外'
def addr(s): return re.sub(r'^神奈川県相模原市','',s.strip())
fac={}
for r in b:
    k=r['住所'].strip()+'|'+short(r['施設・場所名'])
    f=fac.setdefault(k,{'n':short(r['施設・場所名']),'a':addr(r['住所']),'w':ward(r['住所']),'la':round(float(r['緯度']),6),'lo':round(float(r['経度']),6),'s':0,'h':'','_ad':r['住所'].strip()})
    f['h']+=''.join(c for col,c in HZ if r[col].strip()=='1' and c not in f['h'])
for r in a:
    ad=r['住所'].strip();nm=short(r['施設・場所名'])
    cands=[f for f in fac.values() if f['_ad']==ad]
    hit=next((f for f in cands if f['n']==nm),None) or next((f for f in cands if nm in f['n'] or f['n'] in nm),None) or (cands[0] if len(cands)==1 else None)
    if hit: hit['s']=1
    else: fac[ad+'|'+nm]={'n':short(r['施設・場所名']),'a':addr(r['住所']),'w':ward(r['住所']),'la':round(float(r['緯度']),6),'lo':round(float(r['経度']),6),'s':1,'h':'','_ad':ad}
order={'緑区':0,'中央区':1,'南区':2}
lst=sorted(fac.values(),key=lambda x:(order.get(x['w'],9),x['n']))
for i,f in enumerate(lst): f['id']='sg%03d'%(i+1); f.pop('_ad')
meta={'city':'相模原市','source':'国土地理院「指定緊急避難場所・指定避難所データ」（相模原市登録分）を加工して作成','sourceUrl':'https://www.gsi.go.jp/bousaichiri/hinanbasho.html','dataUpdated':'2026-07-03','fetched':'2026-11-23'}
js='// 相模原市の 指定緊急避難場所・指定避難所（自動生成ファイル。手で編集しない）\n// '+meta['source']+'\n// h: f=洪水 d=崖崩れ・土石流・地滑り e=地震 k=大規模な火事 n=内水氾濫 ／ s:1=指定避難所\nwindow.SHELTER_DATA='+json.dumps({'meta':meta,'list':lst},ensure_ascii=False,separators=(',',':'))+';\n'
open(out,'w',encoding='utf-8').write(js)
from collections import Counter
print(len(lst),Counter(f['w'] for f in lst),sum(f['s'] for f in lst),'shelters;',sum(1 for f in lst if f['h']),'emergency')
