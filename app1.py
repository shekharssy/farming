#Import necessary packages
import flask
from flask import render_template
import logging
import pickle
import pandas as pd
from datetime import datetime
import random
import json
import requests
from flask import request
from flask_cors import CORS
import sys

app = flask.Flask(__name__)
CORS(app)
#Setting log for flask app
logging.basicConfig(filename = 'FlaskApp.log',level = logging.INFO)
crop_name = ""

#API to return the recommended crop
@app.route('/crop_predict',methods = ['GET','POST'])
def PredictCrop():
    try:
        random.seed(datetime.now())
        global N,P,K,ph
        first = request.form["nitrogen"]
        print(first, file=sys.stderr)
        try:
            N = float(request.form["nitrogen"])
            P = float(request.form["phosphorous"])
            K = float(request.form["pottasium"])
            ph = float(request.form["ph"])
            
            rainfall = float(request.form["rainfall"])
            hum = float(request.form["humidity"])
            temp = float(request.form["temperature"])
            
            soilType=request.form["soil_type"]
            # return render_template('crop_res.html', response=soilType)
            # def switch_demo(argument):
            #     switcher = {
            #         "sandy":1,
            #         "loamy":2,
            #         "clayey":3,
            #         "red":4,
            #         "black":5
            #     }
            # val=switcher.get(soilType, "Invalid month")
                

            #temp = data['feeds'][1]["field5"]
            #hum = data['feeds'][1]["field6"]
        except:
            N,P,K,ph,temp,hum,rainfall,soilType = 2,44,60,5.5,30,22,150,"sandy"
        # Exception as e: print(e)
        # soilType="sandy"
        a = {}
        a['N'] = N
        a['P'] = P 
        a['K'] = K
        a['temperature']= temp
        a['humidity'] = hum
        a['ph'] = ph
        a['rainfall'] = rainfall

        a['red']=0
        a['sandy']=0
        a['clayey']=0
        a['black']=0
        a['loamy']=0
        if(soilType=='red'):
            a['red']=1
        elif (soilType=='sandy'):
            a['sandy']=1
        elif (soilType=='clayey'):
            a['clayey']=1
        elif (soilType=='black'):
            a['black']=1
        else:
            a['loamy']=1
        

        new_df = pd.DataFrame(a, columns = ['N','P','K','temperature','humidity','ph','rainfall','black','clayey','loamy','red','sandy'],index = [0])
        #print(new_df)
        NB_pkl_filename = 'RandForest.pkl'
        NB_pkl = open(NB_pkl_filename, 'rb')
        NB_model = pickle.load(NB_pkl)
        global crop_name
        crop_name = NB_model.predict(new_df)[0]
        df = pd.read_csv('Datasets/FertilizerData.csv')
        temp1 = df[df['Crop']==crop_name]['soil_moisture']
        soil_moisture = temp1.iloc[0]
        crop_name = crop_name.title()
        response = {'crop': str(crop_name), 'soil_moisture' :str(soil_moisture)}
        response = json.dumps(response)
        return render_template('crop_res.html', response=crop_name)
    except Exception as e:
        return "Caught err "+str(e)
        
@app.route('/fertilizer_predict',methods = ['GET','POST'])
def FertRecommend():
    global crop_name
    try:
        df = pd.read_csv('Datasets/FertilizerData.csv')
        fert = pd.read_csv('Datasets/Fertilizer.csv')
        cp1=request.form["crop"]
        cp=cp1.capitalize()
        # return render_template('fert_res.html', response=cp)
        N=fert.loc[fert['Crop']==cp].iloc[0][2]
        P=fert.loc[fert['Crop']==cp].iloc[0][3]
        K=fert.loc[fert['Crop']==cp].iloc[0][4]
        
        nr = float(request.form["nitrogen"])
        pr = float(request.form["phosphorous"])
        kr = float(request.form["pottasium"])       
    except:
        nr = 180
        pr = 70
        kr = 40
    # global N,P,K
    n = nr - N
    p = pr - P
    k = kr - K
    
    temp2 = {abs(n) : "N",abs(p) : "P", abs(k) :"K"}
    b={}
    b['N']=n
    b['P']=p
    b['K']=k
    new_df1 = pd.DataFrame(b, columns = ['N','P','K'], index=[0])
    NB_pk_filename = 'svm_fert.pkl'
    NB_pkl = open(NB_pk_filename, 'rb')
    svm_model = pickle.load(NB_pkl)
    global fert_name
    
    fert_name = svm_model.predict(new_df1)[0]
    # return "Super Awesome code is running in the background of fertilizer!!"
    # max_value = temp2[max(temp2.keys())]
    # if max_value == "N":
    #     if n < 0 : 
    #         key = 'NHigh'
    #     else :
    #         key = "Nlow"
    # elif max_value == "P":
    #     if p < 0 : 
    #         key = 'PHigh'
    #     else :
    #         key = "Plow"
    # else :
    #     if k < 0 : 
    #         key = 'KHigh'
    #     else :
    #         key = "Klow"

    # d = {
    # 'Nhigh':"""The N value of soil is high and might give rise to weeds. Please consider the following suggestions.<br/>1. Manure – adding manure is one of the simplest ways to amend your soil with nitrogen. Be careful as there are various types of manures with varying degrees of nitrogen.
    # <br/>2. Coffee grinds – use your morning addiction to feed your gardening habit! Coffee grinds are considered a green compost material which is rich in nitrogen. Once the grounds break down, your soil will be fed with delicious, delicious nitrogen. An added benefit to including coffee grounds to your soil is while it will compost, it will also help provide increased drainage to your soil.
    # <br/>3. Plant nitrogen fixing plants – planting vegetables that are in Fabaceae family like peas, beans and soybeans have the ability to increase nitrogen in your soil
    # <br/>4. Plant ‘green manure’ crops""",

    # 'Nlow':"""The N value of your soil is low. Please consider the following suggestions.<br/>
    # • Add sawdust or fine woodchips to your soil – the carbon in the sawdust/woodchips love nitrogen and will help absorb and soak up and excess nitrogen.
    # <br/>• Plant heavy nitrogen feeding plants – tomatoes, corn, broccoli, cabbage and spinach are examples of plants that thrive off nitrogen and will suck the nitrogen dry.
    # <br/>• Water – soaking your soil with water will help leach the nitrogen deeper into your soil, effectively leaving less for your plants to use.
    # <br/>• Sugar – In limited studies, it was shown that adding sugar to your soil can help potentially reduce the amount of nitrogen is your soil. Sugar is partially composed of carbon, an element which attracts and soaks up the nitrogen in the soil. This is similar concept to adding sawdust/woodchips which are high in carbon content.
    # <br/>• Do nothing – It may seem counter-intuitive, but if you already have plants that are producing lots of foliage, it may be best to let them continue to absorb all the nitrogen to amend the soil for your next crops.""",
   
    # 'PHigh':"""The P value of your soil is high. 
    # <br/>• Avoid adding manure – manure contains many key nutrients for your soil but typically including high levels of phosphorous. Limiting the addition of manure will help reduce phosphorus being added.
    # <br/>• Use only phosphorus-free fertilizer – if you can limit the amount of phosphorous added to your soil, you can let the plants use the existing phosphorus while still providing other key nutrients such as Nitrogen and Potassium. Find a fertilizer with numbers such as 10-0-10, where the zero represents no phosphorous.
    # <br/>• Water your soil – soaking your soil liberally will aid in driving phosphorous out of the soil. This is recommended as a last ditch effort.""",
    
    # 'Plow': """The P value of your soil is low. Please consider the following options.
    # <br/>1. Bone meal – a fast acting source that is made from ground animal bones which is rich in phosphorous.
    # <br/>2. Rock phosphate – a slower acting source where the soil needs to convert the rock phosphate into phosphorous that the plants can use.
    # <br/>3. Phosphorus Fertilizers – applying a fertilizer with a high phosphorous content in the NPK ratio (example: 10-20-10, 20 being phosphorous percentage)
    # <br/>4. Organic compost – adding quality organic compost to your soil will help increase phosphoos content
    # <br/>5. Manure – as with compost, manure can be an excellent source of phosphorous for your plants
    # <br/>6. Clay soil – introducing clay particles into your soil can help retain & fix phosphorus deficiencies.
    # <br/>7. Ensure proper soil pH – having a pH in the 6.0 to 7.0 range has been scientifically proven to have the optimal phosphorus uptake in plants""",
    
    # 'KHigh': """<br/> • Loosen the soil deeply with a shovel, and water thoroughly to dissolve water-soluble potassium. Allow the soil to fully dry, and repeat digging and watering the soil two or three more times.
    # <br/>• Sift through the soil, and remove as many rocks as possible, using a soil sifter. Minerals occurring in rocks such as mica and feldspar slowly release potassium into the soil slowly through weathering.
    # <br/>• Stop applying potassium-rich commercial fertilizer. Apply only commercial fertilizer that has a '0' in the final number field. Commercial fertilizers use a three number system for measuring levels of nitrogen, phosphorous and potassium. The last number stands for potassium. Another option is to stop using commercial fertilizers all together and to begin using only organic matter to enrich the soil.
    # <br/>• Mix crushed eggshells, crushed seashells, wood ash or soft rock phosphate to the soil to add calcium. Mix in up to 10 percent of organic compost to help amend and balance the soil.
    #  """,
    
    # 'Klow': """
    # <br/>• Mix in muricate of potash or sulphate of potash
    # <br/>• Try kelp meal or seaweed
    # <br/>• Try Sul-Po-Mag
    #   """
    # }
    # response = {'fertilizer': str(d[key]) ,'fertilizer name': str(fert_name)}  
    # response = json.dumps(response)
    #print(type(response))
    # return response
    return render_template('fert_res.html', response=fert_name)
    



@app.route('/',methods=['GET'])
def hello():
    return render_template('index.html')
    # return "Super Awesome code is running in the background!!"
@app.route('/crop')
def crop_pred():
    return render_template('crop.html')

@app.route('/fertilizer')
def fert_pred():
    return render_template('fertilizer.html')

app.run(port = 3000,host = "127.0.0.1")

