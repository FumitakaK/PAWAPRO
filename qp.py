import numpy as np
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

#st.set_page_config(layout="wide")
now = datetime.datetime.now()
datestr = '{}{}{}_{}{}'.format(now.year,now.month,now.day,now.hour,now.minute)
#st.write(datestr[2:])
np.random.seed(0)
st.sidebar.subheader('パワプロボーダー')
hwd = os.path.expanduser('~').replace('\\','/')
csvf = 'QP.csv'
df_qp = pd.read_csv(csvf,index_col=0,header=0)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")



std = st.sidebar.slider('標準偏差',1,50,20)
num = st.sidebar.slider('反復回数',50,2000,300)
num_people = st.sidebar.slider('プレイヤー人数',50,2000,150) # プレイヤー人数
if std*3+50>num_people:
    st.warning('プレイヤー人数が少ないです。推奨{}人以上'.format(int(std*3+50)))

co = st.empty()
col = st.empty()
col1,col2 = st.columns(2)

co.write('条件設定した後、計算実行をクリック')

if st.sidebar.button('計算実行'):
    df_qp_new = pd.DataFrame(index = [i for i in range (51,num_people+1)])
    df_qp_new['QP'] = 0
    df_qp = pd.concat([df_qp,df_qp_new],axis=0)
    mask = np.zeros((2,num))


    for n in range(num):
        prog = n/num
        co.write('計算実行中　現在{}%'.format(round(prog*100,1)))
        col.progress(prog)
        if n == num-1:
            col.info('正常終了')
            co.write('計算完了　現在100%')
        df = pd.DataFrame()
        df['People_ID'] = [m for m in range (1,num_people+1)]
        df['1w_rank'] = [m for m in range (1,num_people+1)]
        df = df.set_index('People_ID',drop=True)
        a = np.random.normal(loc=0,scale=std,size=num_people*3)
        a = a.reshape(3,num_people)

        for j in range(3):
            val_name = '1w_rank'
            if j == 0:
                df['1w_QP'] = df_qp['QP']
            new_val_name = '{}w_rank'.format(j+2)
            new_QPval_name = '{}w_QP'.format(j+2)
            Se = df[val_name] + a[j,:]
            Se_sort = Se.sort_values()
            #st.write(Se_sort.index)
            for i,id in enumerate(Se_sort.index):
                df.loc[id,new_val_name] = i+1
                df.loc[id,new_QPval_name] = df_qp.loc[i+1,'QP']
        
        ## 累計QPを算出する
        qp_col = df.columns[df.columns.str.contains('QP')]
        df['QP_SUM'] = df[qp_col].sum(axis=1)
        df = df.sort_values(by='QP_SUM',ascending=False)
        df = df.reset_index(drop=False)
        mask[0,n] = df.loc[15,'QP_SUM']
        mask[1,n] = df.loc[49,'QP_SUM']

    df_result = pd.DataFrame(mask.T,columns=['Rank16_QP','Rank50_QP'],index=[m for m in range(num)])
    fig = plt.figure()
    #sns.displot(data=df_result,x='Rank16_QP')
    plt.hist(df_result['Rank16_QP'],bins=int(num/10),color='red',density=True)
    plt.title('Rank16_QP_dist')
    plt.xlabel('QP')
    #sns.displot(data=df_result,x='50位QP')
    col1.pyplot(fig)

    fig2 = plt.figure()
    #sns.displot(data=df_result,x='Rank16_QP')
    plt.hist(df_result['Rank50_QP'],bins=int(num/10),color='blue',density=True)
    plt.title('Rank50_QP_dist')
    plt.xlabel('QP')
    col2.pyplot(fig2)

    csv = convert_df(df_result)
    st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name="{}PAWAPURO.csv".format(datestr[2:]),
    mime="text/csv",
)
    st.write(df_result.describe())
    #st.write(a)