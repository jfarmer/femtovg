import sys
def readppm(p):
    b=open(p,'rb').read()
    # parse header
    parts=[];i=0
    while len(parts)<4:
        while b[i:i+1].isspace(): i+=1
        if b[i:i+1]==b'#':
            while b[i:i+1]!=b'\n': i+=1
            continue
        j=i
        while not b[j:j+1].isspace(): j+=1
        parts.append(b[i:j]); i=j
    i+=1
    w,h=int(parts[1]),int(parts[2])
    return w,h,b[i:i+w*h*3]
for p in sys.argv[1:]:
    w,h,d=readppm(p)
    cnt={}
    for k in range(0,len(d),3):
        c=tuple(d[k:k+3]); cnt[c]=cnt.get(c,0)+1
    top=sorted(cnt.items(),key=lambda x:-x[1])[:4]
    print(p,w,h,top)
