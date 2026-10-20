import re, numpy as np
def parse(d):
    toks=re.findall(r'[MLQCZ]|-?\d+\.?\d*',d); i=0; pts=[]; cur=None; start=None; contours=[]
    while i<len(toks):
        c=toks[i]; i+=1
        if c=='M': cur=np.array([float(toks[i]),float(toks[i+1])]); i+=2; start=cur; pts=[cur]; contours.append(pts)
        elif c=='L': p=np.array([float(toks[i]),float(toks[i+1])]); i+=2; pts.append(p); cur=p
        elif c=='Q':
            a=np.array([float(toks[i]),float(toks[i+1])]); p=np.array([float(toks[i+2]),float(toks[i+3])]); i+=4
            for t in np.linspace(0,1,201)[1:]: pts.append((1-t)**2*cur+2*(1-t)*t*a+t*t*p)
            cur=p
        elif c=='C':
            a=np.array([float(toks[i]),float(toks[i+1])]); b=np.array([float(toks[i+2]),float(toks[i+3])]); p=np.array([float(toks[i+4]),float(toks[i+5])]); i+=6
            for t in np.linspace(0,1,201)[1:]: pts.append((1-t)**3*cur+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*p)
            cur=p
        elif c=='Z': cur=start
    return [np.array(c) for c in contours]
def meanw(d):
    A=0;P=0
    for c in parse(d):
        x,y=c[:,0],c[:,1]; x2,y2=np.roll(x,-1),np.roll(y,-1)
        A+=0.5*np.sum(x*y2-x2*y); P+=np.sum(np.hypot(x2-x,y2-y))
    return 2*abs(A)/P, A, P
P={'sideburnL 207':'M 235,385 C 248,460 258,535 282,600 C 262,535 252,460 242,400 Z',
'sideburnR 208':'M 789,395 C 776,470 766,545 742,610 C 762,545 772,470 782,410 Z',
'sliverR 196':'M 815,525 C 832,490 838,455 832,420 C 840,460 832,495 820,535 Z',
'sliverL 195':'M 215,355 C 210,330 218,305 228,285 C 222,310 220,335 225,360 Z',
'sliverTop 197':'M 455,38 C 432,44 410,55 388,72 C 416,56 438,44 465,36 Z',
'upperlip 332':'M 425,638 Q 458,615 512,618 Q 566,615 599,638 Q 566,632 512,632 Q 458,632 425,638 Z',
'cavity 338':'M 432,642 Q 450,710 512,722 Q 574,710 592,642 Q 562,688 512,688 Q 462,688 432,642 Z',
'uteeth 341':'M 438,644 Q 465,665 512,668 Q 559,665 586,644 Q 559,658 512,658 Q 465,658 438,644 Z',
'lteeth 346':'M 446,680 Q 475,702 512,705 Q 549,702 578,680 Q 549,692 512,692 Q 475,692 446,680 Z',
'tongue 351':'M 454,696 Q 480,718 512,720 Q 544,718 570,696 Q 530,712 512,712 Q 494,712 454,696 Z',
'lowerlip 354':'M 422,678 Q 458,725 512,732 Q 566,725 602,678 Q 566,715 512,715 Q 458,715 422,678 Z',
'lliphl 357':'M 438,684 Q 472,708 512,708 Q 552,708 586,684 Q 552,700 512,700 Q 472,700 438,684 Z',
'stubble 169':'M 310,560 Q 412,890 512,905 Q 612,890 714,560 Q 650,760 512,770 Q 374,760 310,560 Z',
'browL 222':'M 288,362 C 318,330 378,318 425,340 C 452,352 468,378 462,395 C 435,373 392,362 342,363 C 305,364 288,380 288,362 Z',
'browL2 223':'M 298,370 C 324,345 375,336 415,352 C 435,362 448,382 445,395 C 420,376 382,367 345,372 C 315,377 298,392 298,370 Z',
'lidcrease 254':'M 324,422 Q 372,394 420,422 Q 372,410 324,422 Z',
'ear 123':'M 252,465 C 218,465 218,535 252,535 C 278,535 285,500 272,478 C 260,460 242,465 252,465 Z',
}
for k,d in P.items():
    w,A,Pm=meanw(d); print(f'{k:16s} mean {w:6.2f} u   z2 {w*0.390625:5.2f}px  hd {w*1080/1024:5.2f}px  area {A:8.1f}')
