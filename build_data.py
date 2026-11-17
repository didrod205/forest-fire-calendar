# 산림청_산불통계데이터(공공데이터포털 15121380, 2026-11-17 내려받음)를 시군구별로 집계
import csv, json, collections, re
SRC='fire_stats_20251110.csv'
rows=list(csv.DictReader(open(SRC,encoding='cp949')))
RULES=[('입산자 실화',['입산','등산객','산행']),('성묘객 실화',['성묘']),('담뱃불',['담배','담뱃']),
 ('쓰레기 소각',['쓰레기']),('논밭두렁과 영농부산물 소각',['농산','영농','논밭','밭두렁','논두렁','부산물','농업','소각']),
 ('건물과 차량 화재가 옮겨붙음',['화재','비화','농막','보일러','화목','건축물']),
 ('전기 요인',['전기','전선','전서','합선','누전','스파크','단락','발전기','발열']),
 ('불씨 취급 부주의',['불씨','아궁이','화기','모닥불','난로','연소재','재처리','재투기']),
 ('작업장 실화',['작업','산업','사업장','공사','용접','예초']),('방화',['방화']),('낙뢰',['낙뢰']),
 ('원인 미상, 조사중',['미상','조사중','불명'])]
def cause(r):
    t=(r['발생원인_세부원인'] if r['발생원인_세부원인']!='기타(직접입력)' else '')+' '+r['발생원인_기타']
    for name,keys in RULES:
        if any(k in t for k in keys): return name
    return '그 밖의 원인'
def hb(t):
    h=int(t.split(':')[0]); return h
agg={}; nat=collections.defaultdict(lambda:collections.Counter())
check=collections.Counter()
for r in rows:
    sd=r['발생장소_시도'].strip(); sg=r['발생장소_시군구'].strip()
    c=cause(r); check[(r['발생원인_세부원인'],r['발생원인_기타'],c)]+=1
    for key in [(sd,sg),(sd,'_all'),('_all','_all')]:
        a=agg.setdefault(key,{'n':0,'area':0.0,'y':collections.Counter(),'m':collections.Counter(),'h':collections.Counter(),'w':collections.Counter(),'c':collections.Counter(),'emd':collections.Counter()})
        a['n']+=1; a['area']+=float(r['피해면적_합계'] or 0)
        a['y'][r['발생일시_년']]+=1; a['m'][int(r['발생일시_월'])]+=1; a['h'][hb(r['발생일시_시간'])]+=1
        a['w'][r['발생일시_요일']]+=1; a['c'][c]+=1
        if key[1]!='_all': a['emd'][r['발생장소_읍면'].strip()]+=1
out={}
for (sd,sg),a in agg.items():
    out.setdefault(sd,{})[sg]={'n':a['n'],'area':round(a['area'],2),'y':dict(a['y']),'m':[a['m'][i] for i in range(1,13)],
      'h':[a['h'][i] for i in range(24)],'w':[a['w'][d] for d in '월화수목금토일'],'c':a['c'].most_common(),'emd':a['emd'].most_common(5)}
json.dump({'meta':{'rows':len(rows),'from':'2022-01-01','to':max(r['발생일시_년']+'-'+r['발생일시_월']+'-'+r['발생일시_일'] for r in rows)},'d':out},open('data.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
with open('cause_mapping.tsv','w') as f:
    for (a,b,c),n in sorted(check.items(),key=lambda x:-x[1]): f.write(f'{n}\t{a}\t{b}\t{c}\n')
A=agg[('_all','_all')]
print('rows',len(rows),'area',round(A['area'],2)); print(A['c'].most_common()); print('years',A['y'])
print('m',[A['m'][i] for i in range(1,13)]); print('w',[A['w'][d] for d in '월화수목금토일'])
print('h',[A['h'][i] for i in range(24)])
