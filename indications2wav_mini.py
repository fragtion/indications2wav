import os,math as M,struct as S,wave as W,configparser as C
g=lambda f,m,r,d:[int(max(min(M.sin(2*M.pi*f*i/r)*(1+.9*M.sin(2*M.pi*m*i/r))/2,.9),-.9)*32767)for i in range(int(r*d))]
c=C.ConfigParser();c.read('indications.conf');L=40000
for s in c.sections():
 for k,v in c.items(s):
  if k not in['description','ringcadence']:
   w=W.open(os.path.join('output',s+'_'+k+'.wav'),'w');B=[];a=[]
   for x in v.split(','):x=x.split('/');d=int(x[1])/1000 if len(x)>1 else 1;n=1 if x[0].startswith('!')else 0;T=[g(int(f.split('*')[0]),int(f.split('*')[1]if'*'in f else 0),4000,d)for f in x[0].lstrip('!').split('+')];B.append([n,[int(sum(y)/len(T))for y in zip(*T)]if len(T)>1 else T[0]])
   while len(a)<L:
    for i in range(len(B)):B[i][0]<2 and(a.extend(B[i][1])or B[i].__setitem__(0,2 if B[i][0]else 0))
   w.setparams((1,2,4000,L,'NONE',''));w.writeframes(S.pack('h'*L,*a[:L]));w.close()
