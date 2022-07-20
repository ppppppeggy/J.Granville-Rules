PERIOD=120
delta=10
day_point=1
delta_2=10
delta_4=5
import matplotlib.pyplot as plt
import numpy
from talib.abstract import *
import datetime
import pandas as pd
 
#開檔案 
with open('roy_2.txt', 'r', encoding='utf-8') as f: 
    x=f.readlines() 

#將檔案整理乾淨 
x=[i.split('\n') for i in x] 
x=[i[0].replace(" ",'') for i in x] 
x=[i.strip("|") for i in x] 
x=[i.split("|") for i in x] 
x=[[int(i[0]),i[1],float(i[2]),float(i[3]),float(i[4]),float(i[5]),int(i[6])] for i in x] 
 
#用台積電來分析 
tsmc=[i for i in x if  i[0]==2330] 
tsmc=[[i[0],datetime.datetime.strptime(i[1],"%Y-%m-%d"),i[2],i[3],i[4],i[5],i[6]] for i in tsmc] 

#鴻海
R_O=[i for i in x if  i[0]==2317] 
R_O=[[i[0],datetime.datetime.strptime(i[1],"%Y-%m-%d"),i[2],i[3],i[4],i[5],i[6]] for i in R_O] 
 
#捷安特
GIANT=[i for i in x if  i[0]==9921] 
GIANT=[[i[0],datetime.datetime.strptime(i[1],"%Y-%m-%d"),i[2],i[3],i[4],i[5],i[6]] for i in GIANT]

#萬海
# W_H=[i for i in x if  i[0]==2615] 
# W_H=[[i[0],datetime.datetime.strptime(i[1],"%Y-%m-%d"),i[2],i[3],i[4],i[5],i[6]] for i in R_O] 

#中鋼 
IR=[i for i in x if  i[0]==2002] 
IR=[[i[0],datetime.datetime.strptime(i[1],"%Y-%m-%d"),i[2],i[3],i[4],i[5],i[6]] for i in IR] 


sid=IR
#做一個dic存取時間、開、高、低、收、量 
TAKbar={} 
TAKbar['time']=numpy.array([line[1] for line in sid]) 
TAKbar['open']=numpy.array([line[2] for line in sid]) 
TAKbar['high']=numpy.array([line[3] for line in sid]) 
TAKbar['low']=numpy.array([line[4] for line in sid]) 
TAKbar['close']=numpy.array([line[5] for line in sid]) 
TAKbar['volume']=numpy.array([line[6] for line in sid]) 
 
#移動平均線 
MA=MA(TAKbar,timeperiod=PERIOD) 
TAKbar['MA']=MA 
#RSI指標 
RSI=RSI(TAKbar,timeperiod=10,matype=1) 
TAKbar['RSI']=RSI 
#每日總報酬 
TotalProfit=[] 
#股票編號 
stock_no=str(tsmc[0][0]) 
#進場判斷 
df=pd.DataFrame(TAKbar)
index=0 
# for z in range(1,len(TAKbar['time'])):

# 1.進場：價格由下往上穿越均線突破
# 2.進場：當均線還在向上，股價拉回均線
# 3.出場：當均線向下，股價反彈到均線
# 4.出場：股價開始與均線平行，並跌破均線

# close_price_20 = df["close"].rolling(20, min_periods=1).mean()
# close_price_20.plot()

profit=[]
TradingCost=[]
compare_profit=[]
compare=[]
compare_index=0#定期定額index
# index=0
for i in range(1,len(TAKbar['time'])): 
    price=TAKbar['close'][i] 
    lastprice=TAKbar['close'][i-1] 
    ma=TAKbar['MA'][i] 
    lastma=TAKbar['MA'][i-1] 
    # ma_last_reg_up=linregress(x=df.index[i+1:i+5],y=df.MA[i:i+4]).slope
    # ma_reg_up=linregress(x=df.index[i+2:i+6],y=df.MA[i+1:i+5]).slope
    ma_slope=(TAKbar['MA'][i]-TAKbar['MA'][i-delta])/delta  #delta=10
    ma_last_slope=(TAKbar['MA'][i-day_point]-TAKbar['MA'][i-delta-day_point])/delta
    
    price=TAKbar['close'][i] 
    lastprice=TAKbar['close'][i-1] 
    ma=TAKbar['MA'][i] 
    lastma=TAKbar['MA'][i-1] 
    ten_ma_slope=TAKbar['MA'][i]-TAKbar['MA'][i-10]/delta_4 #delta_2=10
    ten_ma=TAKbar['MA'][i-10]
    ten_price=TAKbar['close'][i-10]
    price_slope=(TAKbar['close'][i]-TAKbar['close'][i-delta_4])/delta_4 #delta=10
    price_last_slope=(TAKbar['close'][i-day_point]-TAKbar['close'][i-delta_4-day_point])/delta_4
    third_rule_list=[]
    third_rule_list.clear()
    forth_index=0
    
    #定期定額
    compare_index+=1
    if compare_index==30:
        OrderPrice = price
        compare.append(OrderPrice)
        compare_index=0
        for j in range(i+1,len(TAKbar['time'])):
            price=TAKbar['close'][j-1] 
                #強制賣出
            if j==len(TAKbar['time'])-1: 
                CoverPrice=price 
                CompareProfit=CoverPrice-OrderPrice
                CompareProfit=(1-0.001425)*CompareProfit #手續費=0.14254
                CompareProfit=(1-0.003)*CompareProfit #交易稅=0.003
                compare_profit.append(CompareProfit)
        #葛蘭必第一法則 買
    if ma_last_slope < 0 and ma_slope >= 0 and lastprice<lastma and price>ma:
        OrderTime = TAKbar['time'][i]
        OrderPrice = price
        TradingCost.append(OrderPrice)
        print("1 Order Time: ",OrderTime)
        print("1 Order Price:",OrderPrice)

        for j in range(i+1,len(TAKbar['time'])):
            price=TAKbar['close'][j-1] 
            ma=TAKbar['MA'][j] 
            lastma=TAKbar['MA'][j-1] 
            #格蘭必第一法則 賣
            if ma_last_slope>0 and ma_slope<=0 and price<ma: 
                CoverTime=TAKbar['time'][j] 
                CoverPrice=price
                Profit=CoverPrice-OrderPrice
                print("1 Cover Time: ",CoverTime)
                print("1 Cover Price:",CoverPrice)
                print("1 Profit: ",Profit)
                Profit=(1-0.001425)*Profit #手續費=0.14254
                Profit=(1-0.003)*Profit #交易稅=0.003
                profit.append(Profit)
                break 
            #格蘭必第二法則 賣
            elif ten_ma_slope<0 and ten_price>ten_ma:
                for z in range(10):
                    if TAKbar['close'][j-10+z]<TAKbar['MA'][j-10+z]:
                        CoverTime=TAKbar['time'][j] 
                        CoverPrice=price
                        Profit=CoverPrice-OrderPrice
                        print("2 Cover Time: ",CoverTime)
                        print("2 Cover Price:",CoverPrice)
                        print("2 Profit: ",Profit)
                        Profit=(1-0.001425)*Profit #手續費=0.14254
                        Profit=(1-0.003)*Profit #交易稅=0.003
                        profit.append(Profit)
                        break
                # 葛蘭必第三法則 賣
                for z1 in range(10):
                    if price>ma:
                        break
                    else:
                        third_index+=1
                        third_rule_list.append(price)
                        if third_index==10 and price_last_slope<=0 and price_slope>0:
                            CoverTime = TAKbar['time'][i]
                            CoverPrice = price
                            Profit=CoverPrice-OrderPrice
                            Profit=(1-0.001425)*Profit #手續費=0.14254
                            Profit=(1-0.003)*Profit #交易稅=0.003
                            profit.append(Profit)
                            print("3 Cover Time: ",CoverTime)
                            print("3 Cover Price:",CoverPrice)
                     
                #第四法則 賣  
                for z2 in range(5):
                    if price<lastprice:
                        forth_index=0
                        break
                    else:
                        forth_index+=1
                        if forth_index==5 and price_last_slope>0 and price_slope<0 and price<=ma:
                            CoverTime = TAKbar['time'][i]
                            CoverPrice = price
                            Profit=CoverPrice-OrderPrice
                            Profit=(1-0.001425)*Profit #手續費=0.14254
                            Profit=(1-0.003)*Profit #交易稅=0.003
                            profit.append(Profit)
                            print("4 Cover Time: ",CoverTime)
                            print("4 Cover Price:",CoverPrice)
                #強制賣出
            if j==len(TAKbar['time'])-1: 
                CoverTime=TAKbar['time'][j] 
                CoverPrice=price 
                Profit=CoverPrice-OrderPrice
                Profit=(1-0.001425)*Profit #手續費=0.14254
                Profit=(1-0.003)*Profit #交易稅=0.003
                print("Cover Time: ",CoverTime)
                print("Cover Price:",CoverPrice)
                print("Profit: ",Profit)
                profit.append(Profit)
                
                
        #葛蘭必第二法則
    price=TAKbar['close'][i] 
    lastprice=TAKbar['close'][i-1] 
    ma=TAKbar['MA'][i] 
    lastma=TAKbar['MA'][i-1] 
    ten_ma_slope=TAKbar['MA'][i]-TAKbar['MA'][i-10]/delta_2 #delta_2=10
    ten_ma=TAKbar['MA'][i-10]
    ten_price=TAKbar['close'][i-10]
    
        #格蘭必賣的時候用的變數
    price=TAKbar['close'][i] 
    lastprice=TAKbar['close'][i-1] 
    ma=TAKbar['MA'][i] 
    lastma=TAKbar['MA'][i-1] 
    ten_ma_slope=TAKbar['MA'][i]-TAKbar['MA'][i-10]/delta_2 #delta_2=10
    ten_ma=TAKbar['MA'][i-10]
    ten_price=TAKbar['close'][i-10]
    price_slope=(TAKbar['close'][i]-TAKbar['close'][i-delta])/delta  #delta=10
    price_last_slope=(TAKbar['close'][i-day_point]-TAKbar['close'][i-delta-day_point])/delta
    third_rule_list=[]
    third_rule_list.clear()
    third_index=0
    if ten_ma_slope>0 and ten_price<ten_ma:
        for z in range(10):
            if TAKbar['close'][i-10+z]<TAKbar['MA'][i-10+z]:
                OrderTime = TAKbar['time'][i-10+z]
                OrderPrice = TAKbar['close'][i-10+z]
                TradingCost.append(OrderPrice)
                print("2 Order Time: ",OrderTime)
                print("2 Order Price:",OrderPrice)

                for j in range(i+1,len(TAKbar['time'])):
                    price=TAKbar['close'][j] 
                    lastprice=TAKbar['close'][j-1] 
                    ma=TAKbar['MA'][j] 
                    lastma=TAKbar['MA'][j-1] 
                    ten_ma_slope=TAKbar['MA'][j]-TAKbar['MA'][j-10]/delta_2 #delta_2=10
                    ten_ma=TAKbar['MA'][j-10]
                    ten_price=TAKbar['close'][j-10]
                    price=TAKbar['close'][j-1] 
                    ma=TAKbar['MA'][j] 
                    lastma=TAKbar['MA'][j-1] 
                    #格蘭必第一法則 賣
                    if ma_last_slope>0 and ma_slope<=0 and price<ma: 
                        CoverTime=TAKbar['time'][j] 
                        CoverPrice=price
                        Profit=CoverPrice-OrderPrice
                        print("1 Cover Time: ",CoverTime)
                        print("1 Cover Price:",CoverPrice)
                        print("1 Profit: ",Profit)
                        Profit=(1-0.001425)*Profit #手續費=0.14254
                        Profit=(1-0.003)*Profit #交易稅=0.003
                        profit.append(Profit)
                        break
                    
                    #格蘭必第二法則 賣
                    elif ten_ma_slope<0 and ten_price>ten_ma:
                        for z in range(10):
                            if TAKbar['close'][j-10+z]<TAKbar['MA'][j-10+z]:
                                CoverTime=TAKbar['time'][j] 
                                CoverPrice=price
                                Profit=CoverPrice-OrderPrice
                                print("2 Cover Time: ",CoverTime)
                                print("2 Cover Price:",CoverPrice)
                                print("2 Profit: ",Profit)
                                Profit=(1-0.001425)*Profit #手續費=0.14254
                                Profit=(1-0.003)*Profit #交易稅=0.003
                                profit.append(Profit)
                                break
                    # 葛蘭必第三法則 賣
                    for z1 in range(10):
                        if price>ma:
                           break
                        else:
                            third_index+=1
                            third_rule_list.append(price)
                            if third_index==10 and price_last_slope<=0 and price_slope>0:
                                CoverTime = TAKbar['time'][i]
                                CoverPrice = price
                                Profit=CoverPrice-OrderPrice
                                Profit=(1-0.001425)*Profit #手續費=0.14254
                                Profit=(1-0.003)*Profit #交易稅=0.003
                                profit.append(Profit)
                                print("3 Cover Time: ",CoverTime)
                                print("3 Cover Price:",CoverPrice)
                     
                     #蘭必第四法則 賣  
                    for z2 in range(5):
                        if price<lastprice:
                            forth_index=0
                        break
                    else:
                        forth_index+=1
                        if forth_index==5 and price_last_slope>0 and price_slope<0 and price<=ma:
                            CoverTime = TAKbar['time'][i]
                            CoverPrice = price
                            Profit=CoverPrice-OrderPrice
                            Profit=(1-0.001425)*Profit #手續費=0.14254
                            Profit=(1-0.003)*Profit #交易稅=0.003
                            profit.append(Profit)
                            print("4 Cover Time: ",CoverTime)
                            print("4 Cover Price:",CoverPrice)
                    #強制賣出
                if j==len(TAKbar['time'])-1: 
                    CoverTime=TAKbar['time'][j] 
                    CoverPrice=price 
                    Profit=CoverPrice-OrderPrice
                    Profit=(1-0.001425)*Profit #手續費=0.14254
                    Profit=(1-0.003)*Profit #交易稅=0.003
                    profit.append(Profit)
                    print("Cover Time: ",CoverTime)
                    print("Cover Price:",CoverPrice)
                    print("Profit: ",Profit)
                        

    
    #葛蘭必第三法則
        price=TAKbar['close'][i] 
        lastprice=TAKbar['close'][i-1] 
        ma=TAKbar['MA'][i] 
        lastma=TAKbar['MA'][i-1] 
        ten_ma_slope=TAKbar['MA'][i]-TAKbar['MA'][i-10]/delta_2 #delta_2=10
        ten_ma=TAKbar['MA'][i-10]
        ten_price=TAKbar['close'][i-10]
        price_slope=(TAKbar['close'][i]-TAKbar['close'][i-delta])/delta  #delta=10
        price_last_slope=(TAKbar['close'][i-day_point]-TAKbar['close'][i-delta-day_point])/delta
        third_rule_list=[]
        third_rule_list.clear()

        if ten_ma_slope>=0 :
            for z1 in range(10):
                if price<=ma:
                    break
                else:
                    third_index+=1
                    third_rule_list.append(price)
                    if third_index==10 and price_last_slope<=0 and price_slope>0:
                        OrderTime = TAKbar['time'][i]
                        OrderPrice = price
                        third_index=0
                        TradingCost.append(OrderPrice)
                        print("3 Order Time: ",OrderTime)
                        print("3 Order Price:",OrderPrice)
                        
                        for j in range(i+1,len(TAKbar['time'])):
                            price=TAKbar['close'][j] 
                            lastprice=TAKbar['close'][j-1] 
                            ma=TAKbar['MA'][j] 
                            lastma=TAKbar['MA'][j-1] 
                            ten_ma_slope=TAKbar['MA'][j]-TAKbar['MA'][j-10]/delta_2 #delta_2=10
                            ten_ma=TAKbar['MA'][j-10]
                            ten_price=TAKbar['close'][j-10]
                            price=TAKbar['close'][j-1] 
                            ma=TAKbar['MA'][j] 
                            lastma=TAKbar['MA'][j-1] 
                            #格蘭必第一法則 賣
                            if ma_last_slope>0 and ma_slope<=0 and price<ma: 
                                CoverTime=TAKbar['time'][j] 
                                CoverPrice=price
                                Profit=CoverPrice-OrderPrice
                                Profit=(1-0.001425)*Profit #手續費=0.14254
                                Profit=(1-0.003)*Profit #交易稅=0.003
                                print("1 Cover Time: ",CoverTime)
                                print("1 Cover Price:",CoverPrice)
                                print("1 Profit: ",Profit)
                                profit.append(Profit)
                                break
                            
                            #格蘭必第二法則 賣
                            elif ten_ma_slope<0 and ten_price>ten_ma:
                                for z in range(10):
                                    if TAKbar['close'][j-10+z]<TAKbar['MA'][j-10+z]:
                                        CoverTime=TAKbar['time'][j] 
                                        CoverPrice=price
                                        Profit=CoverPrice-OrderPrice
                                        Profit=(1-0.001425)*Profit #手續費=0.14254
                                        Profit=(1-0.003)*Profit #交易稅=0.003
                                        print("2 Cover Time: ",CoverTime)
                                        print("2 Cover Price:",CoverPrice)
                                        print("2 Profit: ",Profit)
                                        profit.append(Profit)
                                        break
                            # 葛蘭必第三法則 賣
                            for z1 in range(10):
                                     if price>ma:
                                         third_index=0
                                         break
                                     else:
                                         third_index+=1
                                         third_rule_list.append(price)
                                         if third_index==10 and price_last_slope<=0 and price_slope>0:
                                             CoverTime = TAKbar['time'][i]
                                             CoverPrice = price
                                             Profit=CoverPrice-OrderPrice
                                             Profit=(1-0.001425)*Profit #手續費=0.14254
                                             Profit=(1-0.003)*Profit #交易稅=0.003
                                             profit.append(Profit)
                                             print("3 Cover Time: ",CoverTime)
                                             print("3 Cover Price:",CoverPrice)
                      
                             #第四法則 賣  
                            for z2 in range(5):
                                if price<lastprice:
                                    forth_index=0
                                    break
                                else:
                                    forth_index+=1
                                    if forth_index==5 and price_last_slope>0 and price_slope<0 and price<=ma:
                                        CoverTime = TAKbar['time'][i]
                                        CoverPrice = price
                                        Profit=CoverPrice-OrderPrice
                                        Profit=(1-0.001425)*Profit #手續費=0.14254
                                        Profit=(1-0.003)*Profit #交易稅=0.003
                                        profit.append(Profit)
                                        print("4 Cover Time: ",CoverTime)
                                        print("4 Cover Price:",CoverPrice)
                            #強制賣出
                        if j==len(TAKbar['time'])-1: 
                            CoverTime=TAKbar['time'][j] 
                            CoverPrice=price 
                            Profit=CoverPrice-OrderPrice
                            Profit=(1-0.001425)*Profit #手續費=0.14254
                            Profit=(1-0.003)*Profit #交易稅=0.003
                            print("Cover Time: ",CoverTime)
                            print("Cover Price:",CoverPrice)
                            print("Profit: ",Profit)
                            profit.append(Profit)
                                

    #葛蘭必第四法則
        price=TAKbar['close'][i] 
        lastprice=TAKbar['close'][i-1] 
        ma=TAKbar['MA'][i] 
        lastma=TAKbar['MA'][i-1] 
        ten_ma_slope=TAKbar['MA'][i]-TAKbar['MA'][i-10]/delta_4 #delta_2=10
        ten_ma=TAKbar['MA'][i-10]
        ten_price=TAKbar['close'][i-10]
        price_slope=(TAKbar['close'][i]-TAKbar['close'][i-delta_4])/delta_4 #delta=10
        price_last_slope=(TAKbar['close'][i-day_point]-TAKbar['close'][i-delta_4-day_point])/delta_4
        third_rule_list=[]
        third_rule_list.clear()
        forth_index=0
        for z2 in range(5):
            if price>lastprice:
                break
            else:
                forth_index+=1
                if forth_index==5 and price_last_slope<0 and price_slope>0 and price>=ma:
                    OrderTime = TAKbar['time'][i]
                    OrderPrice = price
                    forth_index=0
                    TradingCost.append(OrderPrice)
                    print("4 Order Time: ",OrderTime)
                    print("4 Order Price:",OrderPrice)
                        
                    for j in range(i+1,len(TAKbar['time'])):
                        price=TAKbar['close'][j] 
                        lastprice=TAKbar['close'][j-1] 
                        ma=TAKbar['MA'][j] 
                        lastma=TAKbar['MA'][j-1] 
                        ten_ma_slope=TAKbar['MA'][j]-TAKbar['MA'][j-10]/delta_2 #delta_2=10
                        ten_ma=TAKbar['MA'][j-10]
                        ten_price=TAKbar['close'][j-10]
                        price=TAKbar['close'][j-1] 
                        ma=TAKbar['MA'][j] 
                        lastma=TAKbar['MA'][j-1] 
                        #格蘭必第一法則 賣
                        if ma_last_slope>0 and ma_slope<=0 and price<ma: 
                            CoverTime=TAKbar['time'][j] 
                            CoverPrice=price
                            Profit=CoverPrice-OrderPrice
                            Profit=(1-0.001425)*Profit #手續費=0.14254
                            Profit=(1-0.003)*Profit #交易稅=0.003
                            print("1 Cover Time: ",CoverTime)
                            print("1 Cover Price:",CoverPrice)
                            print("1 Profit: ",Profit)
                            profit.append(Profit)
                            break
                        
                        #格蘭必第二法則 賣
                        elif ten_ma_slope<0 and ten_price>ten_ma:
                            for z in range(10):
                                if TAKbar['close'][j-10+z]<TAKbar['MA'][j-10+z]:
                                    CoverTime=TAKbar['time'][j] 
                                    CoverPrice=price
                                    Profit=CoverPrice-OrderPrice
                                    Profit=(1-0.001425)*Profit #手續費=0.14254
                                    Profit=(1-0.003)*Profit #交易稅=0.003
                                    print("2 Cover Time: ",CoverTime)
                                    print("2 Cover Price:",CoverPrice)
                                    print("2 Profit: ",Profit)
                                    profit.append(Profit)
                                    break
                        # 葛蘭必第三法則 賣
                        for z1 in range(10):
                            if price>ma:
                                break
                            else:
                                third_index+=1
                                third_rule_list.append(price)
                                if third_index==10 and price_last_slope<=0 and price_slope>0:
                                    CoverTime = TAKbar['time'][i]
                                    CoverPrice = price
                                    Profit=CoverPrice-OrderPrice
                                    Profit=(1-0.001425)*Profit #手續費=0.14254
                                    Profit=(1-0.003)*Profit #交易稅=0.003
                                    profit.append(Profit)
                                    print("3 Cover Time: ",CoverTime)
                                    print("3 Cover Price:",CoverPrice)
                        #第四法則賣  
                        for z2 in range(5):
                            if price<lastprice:
                                forth_index=0
                                break
                            else:
                                forth_index+=1
                                if forth_index==5 and price_last_slope>0 and price_slope<0 and price<=ma:
                                    CoverTime = TAKbar['time'][i]
                                    CoverPrice = price
                                    Profit=CoverPrice-OrderPrice
                                    Profit=(1-0.001425)*Profit #手續費=0.14254
                                    Profit=(1-0.003)*Profit #交易稅=0.003
                                    profit.append(Profit)
                                    print("4 Cover Time: ",CoverTime)
                                    print("4 Cover Price:",CoverPrice)
                        #強制賣出
                    if j==len(TAKbar['time'])-1: 
                        CoverTime=TAKbar['time'][j] 
                        CoverPrice=price 
                        Profit=CoverPrice-OrderPrice
                        Profit=(1-0.001425)*Profit #手續費=0.14254
                        Profit=(1-0.003)*Profit #交易稅=0.003
                        print("Cover Time: ",CoverTime)
                        print("Cover Price:",CoverPrice)
                        print("Profit: ",Profit)
                        profit.append(Profit)
                        

#定期定額
TotalCompareCost=sum([i for i in compare])
TotalComepareProfit=sum([i for i in compare_profit])
Comparerate=round(TotalComepareProfit/TotalCompareCost,2)
                        


TotalTradingCost=sum([i for i in TradingCost])
TotalProfit=sum([i for i in profit])
rate=round(TotalProfit/TotalTradingCost,2)
TotalNum=len(profit)
avgProfit=round(TotalProfit/TotalNum,2)

WinNum=len([i for i in profit if i>0])
WinRate=round(WinNum/TotalNum,2)

MaxConLoss=0
dropdown=0

for profit_1 in profit:
    if profit_1<=0:
        dropdown+=profit_1
        if dropdown<MaxConLoss:
            MaxConLoss=dropdown
    else:
        dropdown=0
        
        
print("\n\n")       
print("TotalCompareCost:",TotalCompareCost)
print("TotalComepareProfit:",TotalComepareProfit)
print("Comparerate:",Comparerate)
print("\n\n")

print("TotalTradingCost:",TotalTradingCost)
print("TotalProfit:",TotalProfit)
print("rate:",rate)

print("MaxConLoss:",MaxConLoss)