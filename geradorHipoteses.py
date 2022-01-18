def criaClasses(df_slice):

    _ , edges = np.histogram(df_slice)

    #cria nova lista
    temp = df_slice.copy()

    #cria classes
    nbins   = len(edges)-1
    classes = list(map(chr, range(65, 65+nbins)))

    for i in range(nbins):

        idx = df_slice.index[(df_slice >= edges[i]) & (df_slice < edges[i+1])]
        temp[idx] = classes[i]


    return temp
    

def Gpositivo(g, values, size):

    #n hipoteses g
    gHip  = len(g)
    index = []

    #percorre hipoteses
    for i in range(gHip):

        #percorre atributos
        for j in range(size):

            #valida
            if g[i][j] != '?' and g[i][j] != values[j]:
                index.append(i)
                break

    #remove inconsistencias
    for idx in index:
        g.pop(idx)
    
    return g


def Spositivo(s, values):
    
    temp = s.copy()
    for i in range(len(s)):

        #generaliza atributo
        if s[i] == '-0-':
            temp[i] = values[i]

        elif s[i] != values[i]:
            temp[i] = '?'

    #verifica generalizade de h
    counth = sum([1 for i in temp if i=='?'])

    #verifica generalidade das g
    for gHip in g: 
        countg = sum([1 for i in gHip if i=='?'])

        #atualiza    
        if countg > counth:
            s = temp
            break
    
    return s


def Snegativo(s, values):
    
    #percorre hipoteses
    for i in range(len(s)):

        #elimina s
        count=0
        if s[i] == values[i] or s[i] == '?':
                count+=1

    if count == len(s):
        s = ["-0-" for i in range(size)]

    return s
    
    
def Gnegativo(g, values, lista, size):

    ##Elimina g##

    #n hipoteses g
    gHip = len(g)

    #percorre hipoteses
    for i in range(gHip):

        #percorre atributos
        for j in range(size):

            #valida
            if g[i][j] == '?' or g[i][j] != values[j]:
                g.pop(i)
                break


    ##Adiciona g##

    #gera minimos
    size = len(lista)

    #percorre atributos
    for i in range(size):

        #percorre elementos
        for j in range(len(lista[i])):

            #valida com h
            if lista[i][j] != values[i]:

                if lista[i][j] == s[i]:
                    #cria novas hipoteses g
                    aux = ["?" for i in range(size)]
                    aux[i] = lista[i][j]
                    #atualiza g
                    g.append(aux.copy())

    return g
    
########
# MAIN #
########

#Discretiza variáveis contínuas
colunasAjuste = ['BPM', 'VolMedio', 'PctCantada', 'PctRap', 'ano_lancamento', 'n_reproducao']

for coluna in colunasAjuste:
    ouvinte1[coluna] = criaClasses(ouvinte1[coluna])
    ouvinte2[coluna] = criaClasses(ouvinte2[coluna])

ouvinte1.head(3)

#Cria lista total de atributos
colunas = ouvinte1.columns[:-1]

lista = []
for coluna in colunas:
    lista.append(list(set(ouvinte1[coluna])))


#Ordena objetos positivos
ouvinte1['ordena'] = (ouvinte1['gostou'] == 0) + 1
ouvinte1 = ouvinte1.sort_values('ordena')
ouvinte1.drop(columns=['ordena'], inplace=True)

ouvinte2['ordena'] = (ouvinte2['gostou'] == 0) + 1
ouvinte2 = ouvinte2.sort_values('ordena')
ouvinte2.drop(columns=['ordena'], inplace=True)

#Main
dft   = ouvinte1
size = len(dft.iloc[0]) - 1

g = [["?" for i in range(size)]]
s = ["-0-" for i in range(size)]


for i in range(len(dft)):
    
    #pega valores
    values = dft.iloc[i].values

    
    #Exemplo POSITIVO
    #----------------
    if (values[-1] == True):
        
        values = values[:-1]
        
        #Atualiza G
        g = Gpositivo(g, values, size)
            
        #Atualiza S
        s = Spositivo(s, values)

                          
    #Exemplo NEGATIVO
    #----------------
    else:
        
        values = values[:-1]
        
        #Atualiza S
        s = Snegativo(s, values)
       
        #Atualiza G
        g = Gnegativo(g, values, lista, size) 
        
print(g)
print(s)

############
# METRICAS #
############

#Predictions
TP = ouvinte1[(ouvinte1.Tem_Instr_Cordas == False) & (ouvinte1.gostou == True) ]
FP = ouvinte1[(ouvinte1.Tem_Instr_Cordas == False) & (ouvinte1.gostou == False)]
FN = ouvinte1[(ouvinte1.Tem_Instr_Cordas == True)  & (ouvinte1.gostou == True) ]
TN = ouvinte1[(ouvinte1.Tem_Instr_Cordas == True)  & (ouvinte1.gostou == False)]

precisao = len(TP) / (len(TP) + len(FP))
accuracy = (len(TP) + len(TN)) / (len(TP) + len(FP) + len(FN) + len(TN))
print(precisao, accuracy)
