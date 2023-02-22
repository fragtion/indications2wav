import os,math as A,struct as Q,wave,configparser as R
F,D=len,int
def S(f,m_f,m_d,s_r,dur):
 C=s_r;E=[];G=D(C*dur)
 for F in range(G):H=A.sin(2*A.pi*f*F/C);I=(1+m_d*A.sin(2*A.pi*m_f*F/C))/2;B=H*I;B=max(min(B,0.9),-0.9);B*=32767;E.append(D(B))
 return E
def B(f,d,s,o):
 P='*';I=s;G=d*I;J=R.ConfigParser();J.read(f)
 for M in J.sections():
  for(K,T)in J.items(M):
   if K!='description'and K!='ringcadence':
    U=os.path.join(o,M+'_'+K+'.wav');V=T.split(',');B=[];C=0
    for A in V:
     B.append([0]);A=A.split('/');N=D(A[1])/1000 if F(A)>1 else 1;B[C].append(N)
     if A[0].startswith('!'):A[0]=A[0][1:];B[C][0]=1
     A=A[0].split('+')
     for L in A:B[C].append(S(D(L.split(P)[0]),D(L.split(P)[1]if F(L.split(P))>1 else 0),0.9,I,N))
     C+=1
     if F(B[C-1])>3:W=zip(*B[0][2:]);B[C-1]=B[C-1][:2]+[list(map(lambda x:D(sum(x)/F(x)),W))]
    E=[]
    while F(E)<G:
     for H in B:
      if H[0]<2:
       E.extend(H[2:][0])
       if H[0]==1:H[0]=2
    E=E[:G]
    with wave.open(U,'w')as O:O.setparams((1,2,I,G,'NONE','not compressed'));O.writeframes(Q.pack('h'*G,*E))
B('indications.conf',10,4000,'output')
