import math
def cd(radius, arc, tol):
    da = math.acos(radius/(radius+tol))*2
    return max(2, math.ceil(arc/da))
tol=0.125; fr=1.0
print('w     r    | master pts segs sag(0.5)  | B cd(r)+1 pts sag | C cd(r+f/2)+1 pts sag | ink deficit/cap master px^2')
for w in [0.5,1,1.2,1.4,1.6,2,2.5,2.64,3,3.16,4,4.9,5,6,8,12,16]:
    lw=max(w,fr); r=lw/2; R=r+fr/2
    out=[]
    for segs in (cd(r,math.pi,tol)-1, cd(r,math.pi,tol), cd(R,math.pi,tol)):
        th=math.pi/segs
        sag=r*(1-math.cos(th/2))
        out.append((segs+1,segs,sag))
    segs=out[0][1]; th=math.pi/segs
    deficit=math.pi*r*r/2 - segs*0.5*r*r*math.sin(th)
    print(f'{w:4.2f} {r:5.2f} | {out[0][0]:2d} {out[0][1]:2d} {out[0][2]:.3f} | {out[1][0]:2d} {out[1][2]:.3f} | {out[2][0]:2d} {out[2][2]:.3f} | {deficit:.3f} ({deficit/(math.pi*r*r/2)*100:.0f}% of the half-disc)')
