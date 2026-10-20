# assign.py: every pixel femtovg draws > 20/255 off all three browsers in the original frame, given one cause each
import numpy as np, json
from PIL import Image
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.int16)
def red(k,fr,b='mst4'):
    o=L(f'png/{b}_t__{k}_{fr}.png'); refs=[L(f'refs/{x}_t__{k}_{fr}.png') for x in ('chr','ff','wk')]
    off=[np.abs(o-r).max(2)>20 for r in refs]; a3=off[0]&off[1]&off[2]
    sp=np.zeros(a3.shape,bool)
    for i in range(3):
        for j in range(i+1,3): sp|=np.abs(refs[i]-refs[j]).max(2)>20
    return a3, a3&~sp
P=lambda l: set(tuple(map(int,s.split(','))) for s in l.split())
LISTS={'z2':{'other_fill_tips':P('260,0 342,0 377,43 162,148 289,148 290,148 209,236 250,236 184,182 275,182 175,180 268,194'),
             'teeth_corners':P('216,181 243,181 262,192 191,183 269,183'),
             'browsers_off_area':P('345,16'),
             'unexplained':P('376,4 283,112 283,113')},
       'hd':{'other_fill_tips':P('1021,31 1126,52 1120,63 1119,65 1117,68 1137,68 1116,70 715,73 925,95 757,137 1337,516 1083,681 1084,681'),
             'round_caps':P('1169,25 1180,64 1338,105 1337,106 1254,116 1369,222 1379,359 715,380 1189,401 1348,506'),
             'browsers_off_area':P('1024,19 1024,21 1022,22 1019,48 1266,234 1267,234 1268,234 1271,234 1272,234 1273,234 1274,234 923,736 995,736'),
             'teeth_corners':P('956,680 962,680 874,683 1047,683 873,715 1024,715 1044,722 853,684 855,684 1066,684 851,707 1079,707'),
             'unexplained':P('1105,460 741,518 1059,475 871,479')}}
EDITS={'z2':[('lower_lip_crescent','g01_no_lower_lip'),('iris_dashes','g03_no_iris_dashes')],
       'hd':[('lower_lip_crescent','g01_no_lower_lip'),('nose_crescent','g05_no_nose_crescent'),('iris_dashes','g03_no_iris_dashes')]}
out={}
for fr in ('z2','hd'):
    a3,ag=red('g00_orig',fr); left=a3.copy(); res={}
    for name,k in EDITS[fr]:
        e,_=red(k,fr); m=left&~e; res[name]=(int(m.sum()),int((m&ag).sum())); left&=~m
    for name,s in LISTS[fr].items():
        m=np.zeros(a3.shape,bool)
        for x,y in s: m[y,x]=True
        m&=left; res[name]=(int(m.sum()),int((m&ag).sum())); left&=~m
    res['unassigned']=(int(left.sum()),int((left&ag).sum()))
    print(fr,'all3',a3.sum(),'agreed',ag.sum()); [print(f'   {n:22s} {v[0]:4d} ({100*v[0]/a3.sum():5.1f} %)  agreed {v[1]:4d}') for n,v in res.items()]
    if left.sum(): print('   unassigned px',list(zip(*np.nonzero(left)[::-1])))
    out[fr]=res
json.dump(out,open('assign.json','w'),indent=1)
