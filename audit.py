"""Dashboard Integrity Audit: builds a misleading "before" dashboard and a corrected "after" one
from Sample Superstore, and prints every number used in the README."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import FuncFormatter
SRC='https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv'
raw=pd.read_csv(SRC,encoding='latin1')
# the public file has non-order rows appended; keep real orders only (9,994 rows)
d=raw[pd.to_numeric(raw['Row ID'],errors='coerce').notna() & raw['Order Date'].notna()].copy()
d['Order Date']=pd.to_datetime(d['Order Date'])
d.to_csv('superstore_clean.csv',index=False)
print('rows',len(d),'sales',round(d.Sales.sum()),'profit',round(d.Profit.sum()))
def k(x,p=None): return f'${x/1000:,.0f}k'
def stats(df):
    o={}
    o['region']=df.groupby('Region').Sales.sum().sort_values(ascending=False)
    o['avg_margin']=(df.Profit/df.Sales).mean()
    o['true_margin']=df.Profit.sum()/df.Sales.sum()
    f=df[df.Category=='Furniture']; o['f_avg']=(f.Profit/f.Sales).mean(); o['f_true']=f.Profit.sum()/f.Sales.sum()
    o['sub']=df.groupby('Sub-Category').Profit.sum().sort_values()
    y=df[df['Order Date'].dt.year==2018]
    o['m']=y.groupby(y['Order Date'].dt.month)[['Sales','Profit']].sum()
    return o
B=stats(d[d['Order Date']<='2018-12-15']); A=stats(d)
months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# ---------- BEFORE ----------
bg='#0f1b2d'; fg='#e8eef7'; acc='#38bdf8'; acc2='#f59e0b'
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':fg,'axes.labelcolor':fg,'xtick.color':fg,'ytick.color':fg,'axes.edgecolor':'#2b3b55'})
fig=plt.figure(figsize=(16,10),facecolor=bg)
fig.text(.03,.955,'Superstore Executive Dashboard',fontsize=22,weight='bold')
fig.text(.03,.925,'FY2018 performance overview',fontsize=12,color='#9fb3c8')
fig.text(.97,.955,'last refresh 15/12/2018',fontsize=8,color='#4b5d78',ha='right')
kp=[('Total Sales (all years)',k(B['region'].sum())),('Avg Profit Margin',f"{B['avg_margin']*100:.1f}%"),('Furniture Margin',f"{B['f_avg']*100:.1f}%")]
for i,(t,v) in enumerate(kp):
    ax=fig.add_axes([.03+i*.32,.80,.30,.1]); ax.set_facecolor('#16263d'); ax.set_xticks([]);ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.text(.05,.68,t,fontsize=11,color='#9fb3c8',transform=ax.transAxes); ax.text(.05,.18,v,fontsize=26,weight='bold',transform=ax.transAxes)
# region truncated
ax=fig.add_axes([.05,.43,.38,.31],facecolor=bg); r=B['region']
ax.bar(r.index,r.values,color=acc,width=.6); ax.set_ylim(350000,r.max()*1.03)
ax.yaxis.set_major_formatter(FuncFormatter(k)); ax.set_title('Sales by Region',loc='left',fontsize=14,weight='bold',color=fg)
for s in ['top','right']: ax.spines[s].set_visible(False)
# dual axis
ax=fig.add_axes([.53,.43,.42,.31],facecolor=bg); m=B['m']
ax.plot(range(12),m.Sales.values,color=acc,lw=3,marker='o',label='Sales'); ax.set_xticks(range(12)); ax.set_xticklabels(months)
ax.yaxis.set_major_formatter(FuncFormatter(k))
ax2=ax.twinx(); ax2.plot(range(12),m.Profit.values,color=acc2,lw=3,marker='o',label='Profit'); ax2.yaxis.set_major_formatter(FuncFormatter(k)); ax2.set_ylim(m.Profit.min()*.9,m.Profit.max()*1.05)
ax.set_title('Monthly Sales & Profit, 2018',loc='left',fontsize=14,weight='bold',color=fg)
ax.legend(handles=[ax.lines[0],ax2.lines[0]],loc='upper left',frameon=False)
for a in (ax,ax2):
    for s in ['top']: a.spines[s].set_visible(False)
# subcat diverging centered on mean
ax=fig.add_axes([.12,.11,.83,.25],facecolor=bg); s=B['sub']
norm=TwoSlopeNorm(vcenter=s.mean(),vmin=s.min(),vmax=s.max())
ax.bar(s.index,s.values,color=plt.cm.RdYlGn(norm(s.values)))
ax.yaxis.set_major_formatter(FuncFormatter(k)); plt.setp(ax.get_xticklabels(),rotation=35,ha='right')
ax.set_title('Profit by Sub-Category',loc='left',fontsize=14,weight='bold',color=fg)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
fig.savefig('before.png',dpi=110,facecolor=bg); plt.close()

# ---------- AFTER ----------
plt.rcParams.update({'text.color':'#1f2937','axes.labelcolor':'#1f2937','xtick.color':'#374151','ytick.color':'#374151','axes.edgecolor':'#d1d5db'})
bg='#ffffff'; blue='#2563eb'; red='#dc2626'; grey='#9ca3af'
fig=plt.figure(figsize=(16,11),facecolor=bg)
fig.text(.03,.955,'Superstore Performance — corrected',fontsize=22,weight='bold')
fig.text(.03,.925,'Data: Sample Superstore, Jan 2015 – Dec 2018 (complete). Margins = SUM(Profit) / SUM(Sales).',fontsize=11,color='#6b7280')
kp=[('Total Sales, 2015–2018',k(A['region'].sum())),('Profit Margin',f"{A['true_margin']*100:.1f}%"),('Furniture Margin',f"{A['f_true']*100:.1f}%")]
for i,(t,v) in enumerate(kp):
    ax=fig.add_axes([.03+i*.32,.80,.30,.1]); ax.set_facecolor('#f3f4f6'); ax.set_xticks([]);ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.text(.05,.68,t,fontsize=11,color='#6b7280',transform=ax.transAxes); ax.text(.05,.18,v,fontsize=26,weight='bold',transform=ax.transAxes,color=red if 'Furniture' in t else '#111827')
ax=fig.add_axes([.05,.45,.38,.29]); r=A['region']
ax.barh(r.index[::-1],r.values[::-1],color=blue,height=.6); ax.set_xlim(0,r.max()*1.15)
for y,v in enumerate(r.values[::-1]): ax.text(v+8000,y,k(v),va='center',fontsize=10)
ax.xaxis.set_major_formatter(FuncFormatter(k)); ax.set_title('Sales by Region (axis starts at $0)',loc='left',fontsize=14,weight='bold')
for sp in ['top','right']: ax.spines[sp].set_visible(False)
# small multiples: sales top, margin bottom
m=A['m']; mg=m.Profit/m.Sales*100
ax=fig.add_axes([.53,.62,.42,.12]); ax.plot(range(12),m.Sales.values,color=blue,lw=2.5,marker='o'); ax.set_ylim(0,m.Sales.max()*1.15)
ax.set_xticks(range(12)); ax.set_xticklabels([]); ax.yaxis.set_major_formatter(FuncFormatter(k))
ax.set_title('2018 by month: Sales (top) vs Profit margin (bottom)',loc='left',fontsize=14,weight='bold')
for sp in ['top','right']: ax.spines[sp].set_visible(False)
ax.annotate('Nov: highest sales',(10,m.Sales[11]),xytext=(6.2,m.Sales[11]*.98),fontsize=9,arrowprops=dict(arrowstyle='->',color=grey))
ax=fig.add_axes([.53,.45,.42,.13]); ax.plot(range(12),mg.values,color='#111827',lw=2.5,marker='o'); ax.axhline(A['true_margin']*100,color=grey,ls='--',lw=1)
ax.set_ylim(0,mg.max()*1.25); ax.set_xticks(range(12)); ax.set_xticklabels(months); ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:.0f}%'))
ax.annotate(f'Nov margin only {mg[11]:.1f}%',(10,mg[11]),xytext=(6.5,mg.max()*1.05),fontsize=9,arrowprops=dict(arrowstyle='->',color=grey))
for sp in ['top','right']: ax.spines[sp].set_visible(False)
ax=fig.add_axes([.12,.11,.83,.25]); s=A['sub']
ax.bar(s.index,s.values,color=[red if v<0 else grey for v in s.values]); ax.axhline(0,color='#111827',lw=1)
ax.yaxis.set_major_formatter(FuncFormatter(k)); plt.setp(ax.get_xticklabels(),rotation=35,ha='right')
ax.set_title('Profit by Sub-Category — red = loss-making',loc='left',fontsize=14,weight='bold')
for sp in ['top','right']: ax.spines[sp].set_visible(False)
fig.savefig('after.png',dpi=110,facecolor=bg); plt.close()

print('B region',B['region'].round(0).to_dict()); print('B avg/true',B['avg_margin'],B['true_margin'],B['f_avg'],B['f_true'])
print('A avg/true',A['avg_margin'],A['true_margin'],A['f_avg'],A['f_true'])
print('B dec',B['m'].loc[12].to_dict(),'nov',B['m'].loc[11].to_dict()); print('A dec',A['m'].loc[12].to_dict())
print('margins A', (A['m'].Profit/A['m'].Sales).round(3).to_dict())
print('B sub mean',B['sub'].mean(), B['sub'].round(0).to_dict())
