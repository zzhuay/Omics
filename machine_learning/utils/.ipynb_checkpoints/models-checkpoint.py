import xgboost as xgb
import lightgbm as lgb
import gseapy as gp
import numpy as np
import scipy.stats as st
import pandas as pd

gene_sets="./sources/msigdb.hallmark.mini.gmt"

def ssgsea(tpm):
    df = tpm[tpm.columns.dropna()].apply(st.zscore).T
    print('normalization done.')
    gpres = gp.ssgsea(data=df,
                   gene_sets=gene_sets,
                   outdir='tmp',
                   min_size=1, max_size=1000,
                   sample_norm_method='rank',
                   permutation_num=0,
                   no_plot=True,
                   processes=2, format='png', seed=11)
    return gpres.res2d.T


def pd_read(path):
    if path is not None:
        return pd.read_csv(path['props']['children'][0]['props']['children'], index_col=0)
    else:
        return pd.DataFrame()

def predict(her2, er, file_clin, file_meth, file_rna, file_prot, file_pp):
    df_clin = pd_read(file_clin)
    
    if file_meth is not None:
        try:
            df_meth = pd.read_csv(file_meth['props']['children'][0]['props']['children']+'.2f.csv', index_col=0)
        except:
            df_meth = pd.read_csv(file_meth['props']['children'][0]['props']['children'], index_col=0)[['global','GeneA']]
            df_meth.to_csv(file_meth['props']['children'][0]['props']['children']+'.2f.csv')
    
    if file_rna is not None:
        try:
            df_rna = pd.read_csv(file_rna['props']['children'][0]['props']['children']+'.log2.csv', index_col=0)
            df_ssrna = pd.read_csv(file_rna['props']['children'][0]['props']['children']+'.ssgsea.csv', index_col=0)
        except:
            df_rna = pd.read_csv(file_rna['props']['children'][0]['props']['children'], index_col=0)
            df_rna = (df_rna+0.01).apply(np.log2)
            for gene in ['GeneA','GeneB','GeneC']:
                if gene not in set(df_rna.columns):
                    df_rna[gene] = np.NaN
            df_rna[['GeneA','GeneB','GeneC']].to_csv(file_rna['props']['children'][0]['props']['children']+'.log2.csv')
            df_ssrna = ssgsea(df_rna)
            df_ssrna.to_csv(file_rna['props']['children'][0]['props']['children']+'.ssgsea.csv')
    else:
        df_rna = pd.DataFrame()
        df_ssrna = pd.DataFrame()
    
    df_prot = pd_read(file_prot)
    df_pp = pd_read(file_pp)
    
    try:
        df_pred = df_clin[['DFS_MONTHS','DFS_STATUS']]
    except:
        df_pred = df_clin[[]]
        
    df_pred['Pr'] = model.predict(df_pred['Feature0	Feature1	Feature2	GeneA_meth	GeneB_tpm	GeneC_prot'.split('\t')])
        
 
    
    file_pred = file_clin['props']['children'][0]['props']['children']+'.prediction.csv'
    
    df_pred.to_csv(file_pred)
    
    return df_pred