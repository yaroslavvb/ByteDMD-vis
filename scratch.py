import sys
import os

# add ByteDMD-vis to path
sys.path.append("/Users/yaroslavvb/Library/CloudStorage/Dropbox/git0/ByteDMD-vis")
from bytedmd import trace_ir

def dot2(x0, x1, y0, y1):
    return x0 * y0 + x1 * y1

trace_ir(dot2, (1, 2, 3, 4))
