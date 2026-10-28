# frame <-> svg coordinates for the framings
S={'z2':(30.0,-70.0,0.390625),'hd':(420.0,0.0,1080/1024),'z1':(130.0,30.0,200/1024),'z4':(-170.0,-370.0,0.78125)}
def to_svg(fr,x,y):
    ox,oy,s=S[fr]; return ((x+0.5-ox)/s,(y+0.5-oy)/s)
def to_frame(fr,u,v):
    ox,oy,s=S[fr]; return (ox+u*s, oy+v*s)
