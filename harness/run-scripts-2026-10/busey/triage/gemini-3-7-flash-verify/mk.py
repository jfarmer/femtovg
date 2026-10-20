import math
bg='#150304'; col='#f0c090'
hdr='<svg viewBox="0 0 1024 1024" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">\n<rect width="1024" height="1024" fill="BG"/>\n'.replace('BG',bg)
def w(name, body):
    open(f'svg/{name}.svg','w').write(hdr+body+'\n</svg>\n')
cres='M 345 645 C 380 710 430 762 512 762 C 594 762 644 710 679 645 C 654 715 594 772 512 772 C 430 772 370 715 345 645 Z'
w('v00_crescent', f'<path d="{cres}" fill="{col}"/>')
tx,ty=345,645
def unit(x,y):
    l=math.hypot(x,y); return x/l,y/l
e0=unit(35,65); e1=unit(25,70)
L=150
p0=(tx+L*e0[0],ty+L*e0[1]); p1=(tx+L*e1[0],ty+L*e1[1])
w('v01_wedge', f'<path d="M {tx} {ty} L {p0[0]:.4f} {p0[1]:.4f} L {p1[0]:.4f} {p1[1]:.4f} Z" fill="{col}"/>')
w('v02_wedge_rev', f'<path d="M {tx} {ty} L {p1[0]:.4f} {p1[1]:.4f} L {p0[0]:.4f} {p0[1]:.4f} Z" fill="{col}"/>')
a=math.degrees(math.acos(e0[0]*e1[0]+e0[1]*e1[1])); print('tip angle',a)
mid=((p0[0]+p1[0])/2,(p0[1]+p1[1])/2)
notch=(tx+0.8*(mid[0]-tx), ty+0.8*(mid[1]-ty))
w('v03_dart', f'<path d="M {tx} {ty} L {p0[0]:.4f} {p0[1]:.4f} L {notch[0]:.4f} {notch[1]:.4f} L {p1[0]:.4f} {p1[1]:.4f} Z" fill="{col}"/>')
def rot(v,t): return (v[0]*math.cos(t)-v[1]*math.sin(t), v[0]*math.sin(t)+v[1]*math.cos(t))
ang=math.radians(40); c=unit(30,67.5)
f0=rot(c,ang/2); f1=rot(c,-ang/2)
q0=(tx+L*f0[0],ty+L*f0[1]); q1=(tx+L*f1[0],ty+L*f1[1]); m2=((q0[0]+q1[0])/2,(q0[1]+q1[1])/2); n2=(tx+0.8*(m2[0]-tx),ty+0.8*(m2[1]-ty))
w('v04_dart_wide', f'<path d="M {tx} {ty} L {q0[0]:.4f} {q0[1]:.4f} L {n2[0]:.4f} {n2[1]:.4f} L {q1[0]:.4f} {q1[1]:.4f} Z" fill="{col}"/>')
