import pandas as pd
from os.path import join,dirname

df = pd.read_csv(join(dirname(__file__), './data/raw/pitchdata.csv'))

result=[]
result_bak=[]

def readCombination():
    with open(join(dirname(__file__), './data/reference/combinations.txt')) as f:
        content = f.readlines();
    content = [x.strip() for x in content]
    combinations=[]
    for x in content:
        combinations.append(x.split(','))

    # remove subject titles
    combinations = combinations[1:len(combinations)]
    return combinations

# group the data
def groupData(groupID, PitorHit, side):
    g = df[df[PitorHit]==side].groupby(groupID)
    filtered = g.filter(lambda t:t.sum()['PA']>=25)
    sorted = filtered.sort_values(groupID)
    grouped = sorted.groupby(groupID)
    return grouped

#calculate AVG of each group in gourped data. Input is one group of grouped data
def get_AVG(gr):
    return round(float((gr['H'].sum()))/(gr['AB'].sum()),3)

# (H+B+HBP)/(AB+BB+HBP+SF)
def get_OBP(gr):
    return round(float(gr['H'].sum()+gr['BB'].sum()+gr['HBP'].sum())/float(gr['AB'].sum()+gr['BB'].sum()+gr['HBP'].sum()+gr['SF'].sum()),3)

# (H+2B+3B*2+HR*3)/AB
def get_SLG(gr):
    return round(float(gr['H'].sum()+gr['2B'].sum()+gr['3B'].sum()*2+gr['HR'].sum()*3)/float(gr['AB'].sum()),3)

# OPS = OBP+SLG
def get_OPS(gr):
    return round(float(gr['H'].sum()+gr['BB'].sum()+gr['HBP'].sum())/float(gr['AB'].sum()+gr['BB'].sum()+gr['HBP'].sum()+gr['SF'].sum()) + float(gr['H'].sum()+gr['2B'].sum()+gr['3B'].sum()*2+gr['HR'].sum()*3)/float(gr['AB'].sum()),3)

# combination of calcuation functions
def calculate(gr, stats):
    if stats=='AVG':
        return get_AVG(gr)
    elif stats=='OBP':
        return get_OBP(gr)
    elif stats=='SLG':
        return get_SLG(gr)
    elif stats=='OPS':
        return get_OPS(gr)

# add result data to result list line by line
def addToResult(grouped, combination, calculate,result):
    for name, group in grouped:
        Stats = combination[0]
        ID = combination[2]
        vs_= combination[1]
        result.append([name, Stats, ID, vs_, calculate(group, Stats)])

def solve(readCombination, groupData, addToResult):
    result_bak = result
    combinations = readCombination()
    for comb in combinations:
        groupID = comb[1]
        PitorHit = 'PitcherSide' if comb[2][5]=='P' else 'HitterSide'
        side = comb[2][3]
        stats = comb[0]
        gr = groupData(groupID, PitorHit, side)
        addToResult(gr, comb, calculate, result)
    output_csv(result)

def output_csv(result):
    rs_df = pd.DataFrame(result, columns=['SubjectId', 'Stat', 'Split', 'Subject', 'Value'])
    rs_df = rs_df.sort_values(['SubjectId', 'Stat', 'Split', 'Subject'], ascending=[True,True,True,True])
    rs_df.to_csv(join(dirname(__file__), './data/processed/output.csv'), index=False)

solve(readCombination, groupData, addToResult)
