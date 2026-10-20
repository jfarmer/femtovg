import sys; sys.path.insert(0,'scripts')
from flat import *
segs=[('M',(252,465)),('C',(218,465),(218,535),(252,535)),('C',(278,535),(285,500),(272,478)),('C',(260,460),(242,465),(252,465))]
for fr,T in [('z2',(30.0,-70.0,0.390625)),('hd',(420.0,0.0,1080/1024))]:
    pts=flatten(segs,T); A=area(pts)
    if A>0: pts=pts[::-1]   # expand_fill: polygon_area = -shoelace; reversed when polygon_area<0
    J=joins(pts)
    print(fr,'points',len(pts),'area',A)
    for k,(p,f,dm,mag,l0,l1) in enumerate(J):
        if mag<0.5 or (f&(BEVEL|INNER)):
            fl='|'.join(n for n,b in [('CORNER',1),('LEFT',2),('BEVEL',4),('INNER',8)] if f&b)
            print(f'  #{k} pos ({p[0]:.3f},{p[1]:.3f}) flags {fl:22s} |dm|={mag:.4f} |dmpos|={np.hypot(*dm):.2f} len0={l0:.3f} len1={l1:.3f} p+dm*1.5=({p[0]+dm[0]*1.5:.1f},{p[1]+dm[1]*1.5:.1f}) p-dm*0.5=({p[0]-dm[0]*0.5:.1f},{p[1]-dm[1]*0.5:.1f})')
