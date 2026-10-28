from lib import *
# boxes in svg units -> frame boxes
SVGBOX = {
 'lipL': (355, 640, 420, 712), 'lipR': (604, 640, 669, 712),
 'nose': (484, 584, 540, 600),
 'irisL': (403, 432, 443, 472), 'irisR': (581, 429, 619, 467),
}
def fbox(name, fr):
    f, s = tf(fr); x0, y0, x1, y1 = SVGBOX[name]
    X0, Y0 = f(x0, y0); X1, Y1 = f(x1, y1)
    return int(np.floor(X0)), int(np.floor(Y0)), int(np.ceil(X1)), int(np.ceil(Y1))
def counts(m, fr):
    out = {}
    tot = int(m.sum()); used = np.zeros(m.shape, bool)
    for k in SVGBOX:
        x0, y0, x1, y1 = fbox(k, fr); x0 = max(x0, 0); y0 = max(y0, 0)
        sub = np.zeros(m.shape, bool); sub[y0:y1, x0:x1] = True
        out[k] = int((m & sub & ~used).sum()); used |= sub
    out['rest'] = int((m & ~used).sum()); out['total'] = tot
    return out
