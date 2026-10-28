# frame <-> svg coordinates for z2 (box 200 at 130,30, pivot 230,130, zoom 2) and hd (box 1080 at 420,0, zoom 1)
import sys
def f2s(x,y,fr='z2'):
    if fr=='hd': return ((x-420)*1024/1080,(y)*1024/1080)
    return (((x-230)/2+230-130)*1024/200, ((y-130)/2+130-30)*1024/200)
def s2f(x,y,fr='z2'):
    if fr=='hd': return (420+x*1080/1024, y*1080/1024)
    return (230+(130+x*200/1024-230)*2, 130+(30+y*200/1024-130)*2)
if __name__=='__main__':
    a=sys.argv; fn=f2s if a[1]=='f' else s2f; print(fn(float(a[2]),float(a[3]),a[4] if len(a)>4 else 'z2'))
