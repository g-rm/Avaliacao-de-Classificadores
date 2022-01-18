def pre_tratamento(df):

    #renomeia colunas
    colNames       = list(df.columns)
    colNames[-2]   = 'gostou'
    colNames[-3]   = 'n_reproducao'

    df = df.reindex(columns=colNames)


    #Cria Ouvintes
    ouvintes = []
    for idNum in set(df.id_cliente):
        ouvinte = df[df.id_cliente == idNum]
        ouvintes.append(ouvinte.drop(columns='id_cliente'))
        
    return df, ouvintes
    
    
def inconsistencia(df):
    
    #lista sets e/ou bordas de variaveis
    for i in range(len(df.columns)):

        if type(df[df.columns[i]][0]) != bool:
            print(df.columns[i], ':', max(df[df.columns[i]]), min(df[df.columns[i]]))
        else:
            print(df.columns[i], ':',  set(df[df.columns[i]][:5]))
      
            
def variavel_categorica(df):
    
    from unidecode import unidecode as decode
    
    #valores da variavel 'bateria'
    bateria = ['Eletrônica', 'Acústica', 'Nenhuma']

    #discretiza
    for tipo in bateria:
        
        df[decode(tipo)] = (df['bateria'] == tipo)

    return df
    
   
def normaliza(df):
    
    #normaliza df
    df_min   = df.min().astype(np.float32)
    df_max   = df.max().astype(np.float32)
    df_range = df_max - df_min

    df_scaled = (df - df_min) / df_range
    
    return df_scaled
    
    
########
# MAIN #
########

#geral
import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt

#aprendizado
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate
from sklearn import svm

df = pd.read_csv('../JacquelineVictal_dados_treino.csv')

df, ouvintes = pre_tratamento(df)

df = inconsistencia(df)

#ajusta variavel
for i in range(len(ouvintes)):
    ouvinte = variavel_categorica(ouvintes[i])
    ouvintes[i].drop(['bateria'], axis=1, inplace=True)
    
#normaliza
ouvintes[0] = normaliza(ouvintes[0])
ouvintes[1] = normaliza(ouvintes[1])

#Separa dados de treino/teste
X = ouvintes[0].drop(['gostou'], axis=1)
y = ouvintes[0]['gostou']

#Lista modelos e métricas
kernels  = ['linear', 'poly', 'rbf', 'sigmoid']
metricas = ['precision', 'accuracy']

#Métricas de cada modelo
modelos = [pd.DataFrame(columns=[metricas], index=list(range(1,20))) for i in kernels] 

#Roda SVC
for idx in range(len(kernels)):
    for C in range(1,20):
    
        #Cria classificador
        clf = svm.SVC(C=C, kernel=kernels[idx], gamma='scale', random_state=42) 
        
        #Realiza validacao cruzada
        scores = cross_validate(clf, X, y, cv=4, scoring=metricas, error_score=0)

        #Armazena acurácia
        modelos[idx].loc[C, 'accuracy'] = scores['test_accuracy'].mean()

        #Armazena precisão
        modelos[idx].loc[C, 'precision'] = scores['test_precision'].mean()

########
# POLY #
########

poly_score = pd.DataFrame(columns=['C', 'n_coef', 'Acuracia', 'Precisao'])

n_coef = range(1,10)
for C in range(1,20):
    for coef in n_coef:
        #Create a svm Classifier
        clf = svm.SVC(C=C, kernel='poly', degree=coef, gamma='scale', random_state=42) 

        #realiza cross-validation
        sc = cross_validate(clf, X, y, cv=4, scoring=metricas, error_score=0)
        
        result = pd.DataFrame([[C, coef, sc['test_accuracy'].mean(), sc['test_precision'].mean()]],
                              columns=['C', 'n_coef', 'Acuracia', 'Precisao'])
        
        poly_score = poly_score.append(result, ignore_index=True)
        
print(poly_score[(poly_score.Acuracia > .79) & (poly_score.Precisao > .6)])


#Plot
plt.figure(1, figsize=(12,8))

for modelo in modelos:
    
    plt.subplot(2,2,1)
    modelo.plot(kind='line',y=metricas[0], use_index=True, ax=plt.gca())
    plt.legend(kernels)
    plt.xlabel('C')
    plt.ylabel('Precisão')

    plt.subplot(2,2,2)
    modelo.plot(kind='line',y=metricas[1], use_index=True, ax=plt.gca())
    plt.ylim((.575, .8))
    plt.legend(kernels)
    plt.xlabel('C')
    plt.ylabel('Acurácia')


plt.suptitle('Scores em validaçao cruzada para diferentes Kernels (gamma = 1/(n * var(X))', fontsize=14)
plt.tight_layout(pad=2.0)


