import pandas as pd
import pybedtools
import sys

# input: methylation beta table from BSMAP methratio.py
i = sys.argv[1]

tss = pd.read_csv('./GRCh38_hg38_UCSC_RefSeq.TSSes.bed', index_col=0).\
sort_values(['seqnames','start','name'])['seqnames	start	end	name'.split('\t')].drop_duplicates(subset='name')
tss['start'] -= 1000
tss['end'] += 1000
tss.index = range(len(tss.index))

df_ratio = tss[[]]
df_ratio.index = tss['name']

df_mC = tss[[]]
df_mC.index = tss['name']

df_uC = tss[[]]
df_uC.index = tss['name']

df_avg = {}

df_dist = pd.DataFrame()

# position table of promoter
a = pybedtools.BedTool.from_dataframe(tss)

mdf = pd.read_table('../methratio/'+i)
mdf = mdf.loc[mdf['total_C']>=10,:]
mdf['count'] = 1

# global methylation levels
df_avg[i] = mdf['ratio'].mean()

# map methylation beta values to promoter regions
b = pybedtools.BedTool.from_dataframe(mdf[['chr','pos','pos','methy_C','total_C','ratio','count']])
c = pybedtools.BedTool.map(a,b,c=[4,5,6,7],F=1,o='sum')
cc = c.to_dataframe()
cc.index = cc['name']
cc['mC'] = cc['score'].replace('.','0').astype(int)
cc['uC'] = cc['strand'].replace('.','0').astype(int)
cc['ratio'] = cc['thickStart'].replace('.','0').astype(float)/cc['thickEnd'].replace('.','0').astype(float)
df_ratio[i] = df_ratio.index.map(cc['ratio'])
df_mC[i] = df_mC.index.map(cc['mC'])
df_uC[i] = df_uC.index.map(cc['uC'])
print('Done: '+i)

df_ratio.to_csv('../WGBS/beta/'+i+'.promoters.beta.csv')
df_mC.to_csv('../WGBS/beta/'+i+'.promoters.mC.csv')
df_uC.to_csv('../WGBS/beta/'+i+'.promoters.uC.csv')
pd.DataFrame(pd.Series(df_avg)).to_csv('../WGBS/beta/'+i+'.global.beta.csv')