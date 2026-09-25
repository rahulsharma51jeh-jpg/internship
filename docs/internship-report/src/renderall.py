import sys, build, raster, os
os.makedirs('/projects/sandbox/preview/pages', exist_ok=True)
d=build.make(None)
p={"refs":dict(d._collect),"figures":list(d.figures),"tables":list(d.tables_list)}
d2=build.make(p)
p2={"refs":dict(d2._collect),"figures":list(d2.figures),"tables":list(d2.tables_list)}
d3=build.make(p2)
lo=int(sys.argv[1]) if len(sys.argv)>1 else 1
hi=int(sys.argv[2]) if len(sys.argv)>2 else len(d3.pages)
for i in range(lo-1, min(hi, len(d3.pages))):
    raster.render(d3,i,"/projects/sandbox/preview/pages/page%03d.png"%(i+1),dpi=92)
print("rendered pages %d-%d of %d"%(lo,hi,len(d3.pages)))
