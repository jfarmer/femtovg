# red.py: reductions - off all three browsers, off the area reference, tip-window ink vs the area reference
import sys, numpy as np
from PIL import Image
from xy import s2f
L=lambda p: np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
def box(fr, x0,y0,x1,y1):
    a=s2f(x0,y0,fr); b=s2f(x1,y1,fr); return (int(a[0]),int(a[1]),int(np.ceil(b[0])),int(np.ceil(b[1])))
TIPS={'lip':[(360,640,420,735),(604,640,664,735)],'dart':[(360,640,400,705)],'nose':[(484,585,500,598),(524,585,540,598)]}
def ink(img,bgc,fc,b):
    x0,y0,x1,y1=b; ch=int(np.argmax(np.abs(np.array(fc)-np.array(bgc))))
    a=(img[y0:y1,x0:x1,ch]-bgc[ch])/(fc[ch]-bgc[ch]); return a.sum()
def run(k, bgc, fc, tips, builds=('mst4','fm','off')):
    for fr in ('z2','hd'):
        refs={x:L(f'refs/{x}_{k}_{fr}.png') for x in ('chr','ff','wk','id')}
        bx=[box(fr,*t) for t in TIPS[tips]]
        ri={x:sum(ink(refs[x],bgc,fc,b) for b in bx) for x in refs}
        line=f'{k:22s} {fr}: '
        for b in builds:
            o=L(f'png/{b}_{k}_{fr}.png')
            off=[np.abs(o-refs[x]).max(2)>20 for x in ('chr','ff','wk')]; all3=(off[0]&off[1]&off[2]).sum()
            offid=(np.abs(o-refs['id']).max(2)>20).sum()
            oi=sum(ink(o,bgc,fc,bb) for bb in bx)
            line+=f'[{b}: all3 {all3} offarea {offid} tipink {oi/ri["id"]:.2f}x] '
        line+=' browsers tipink '+' '.join(f'{x} {ri[x]/ri["id"]:.2f}' for x in ('chr','ff','wk'))
        line+='  browsers offarea '+' '.join(str(int((np.abs(refs[x]-refs['id']).max(2)>20).sum())) for x in ('chr','ff','wk'))
        print(line)
h=lambda s: tuple(int(s[i:i+2],16) for i in (1,3,5))
#run('t__r10_lip_skin',h('#df9a78'),h('#ab4f47'),'lip')
#run('t__r11_lip_dark',h('#1f0305'),h('#ab4f47'),'lip')
#run('t__r12_nose',h('#e8a080'),h('#5c1f14'),'nose')
#run('t__r13_dart_1seg',h('#df9a78'),h('#ab4f47'),'dart')
#run('t__r14_dart_split10',h('#df9a78'),h('#ab4f47'),'dart')
#run('t__r15_dart_split4',h('#df9a78'),h('#ab4f47'),'dart')
TIPS['dartc']=[(360,640,410,730)]
if len(sys.argv)>1:
    for k in sys.argv[1:]: run(k,h('#df9a78'),h('#ab4f47'),'dartc')
