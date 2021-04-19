# S3 bucket: arn:aws:s3:::mdcvsvaccine
# get https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.json?vaccineinf
# https://covidinfo.reportsonline.com/covidinfo/GiantFood.html
# convert to dictionary
# check tat it works using "HI"
# find "MD"
# loop over for available
# if available send using SNS
# Import requests (to download the page)
import requests
# Import BeautifulSoup (to parse what we download)
# Import Time (to add a delay between the times the scape runs)
import time
# Import smtplib (to allow us to email)
import json
import os.path
from os import path
import boto3


def lambda_handler(event=0, context=0):
    url = "https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.json?vaccineinf"
    # https://www.cvs.com/vaccine/intake/store/covid-screener/covid-qns
    # set the headers like we are a browser,
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    # download the homepage
    response = requests.get(url, headers=headers)
    # print(response.text)
    openlist = json.loads(response.text)
    # print(json.dumps(openlist["responsePayloadData"]["data"]["MD"], sort_keys=True, indent=4))
    # print(json.dumps(openlist["responsePayloadData"]["data"]["HI"], sort_keys=True, indent=4))
    Sitelist = []
    MDlist = openlist["responsePayloadData"]["data"]["MD"]
    VAlist = openlist["responsePayloadData"]["data"]["VA"]
    # print(type(MDlist)) list
    # print(json.dumps(MDlist, sort_keys=True, indent=4))
    for site in MDlist:
        if site["city"] in ["BETHESDA", "CHEVY CHASE", "ROCKVILLE", "SILVER SPRING"]:
            Sitelist.append(site)
    for site in VAlist:
        if site["city"] in ["ALEXANDRIA", "ARLINGTON", "FAIRFAX", "ROSSLYN"]:
            Sitelist.append(site)
    print("SITELIST: " + json.dumps(Sitelist, sort_keys=True, indent=4))
    # print(openlist)
    # "Fully Booked"
    # "Available"
    Notifylist = []
    UpdateList = []
    jsonfile = "/tmp/sitelist.json"
    checkfile = os.path.exists(jsonfile)
    print("file exists?: " + str(checkfile))
    # s3 = boto3.resource("s3").Bucket("mdcvsvaccine")
    # json.load_s3 = lambda f: json.load(s3.Object(key=f).get()["Body"])
    # json.dump_s3 = lambda obj, f: s3.Object(key=f).put(Body=json.dumps(obj))
    # data = {"test":0}
    # json.dump_s3(data, "key") # saves json to s3://bucket/key
    # data = json.load_s3("key") # read json from s3://bucket/key
    # json.dump_s3(Sitelist, "Sitelist") # saves json to s3://bucket/key
    if not checkfile:
        with open(jsonfile, 'w') as json_data:
            json_data.write(json.dumps(Sitelist))
            json_data.close()
            print("writing new sitelist file")
    json_cvs_data = open(jsonfile, 'r')
    current_data = json.load(json_cvs_data)
    json_cvs_data.close()

    # fileopen("sitelist.json")
    for Newsite in Sitelist:
        # get site status from sitelist.json
        # if site not found, add it, print site not found, print adding sites
        # if site found, check site status against current status
        # if different and new status = "Available", add to notification list
        # update sitelist.json
        print("Site:" + json.dumps(Newsite))
        OldStatus = next((item for item in current_data if item["city"] == Newsite["city"]), 'None')
        print("oldstatus:" + json.dumps(OldStatus))
        if Newsite["status"] == "Available":
            if OldStatus == "None" and Newsite["status"] == "Available":
                Notifylist.append(Newsite)
                print('Appointments Available!: ' + Newsite['city'] + ', ' + Newsite['state'])
            if OldStatus != "None" and OldStatus["status"] == "Fully Booked":
                Notifylist.append(Newsite)
                print('Appointments Available!: ' + Newsite['city'] + ', ' + Newsite['state'])
        if Newsite["status"] == "Fully Booked":
            print('Appointments not available: ' + Newsite['city'] + ', ' + Newsite['state'])
    if os.path.exists(jsonfile) and Notifylist:
        os.remove(jsonfile)
        print("Removed the file %s" % jsonfile)
        with open(jsonfile, 'w') as new_json_data:
            new_json_data.write(json.dumps(Sitelist))
            new_json_data.close()
            print("wrote new file %s" % jsonfile)
    print(Notifylist)

    if Notifylist:
        s3_client = boto3.resource("s3").Bucket("mdcvsvaccine")
        sns_client = boto3.client('sns')
        # mdcvsvaccine
        response = sns_client.publish(
            Message='Appointment available! ' + str(Notifylist)
            , TopicArn='arn:aws:sns:us-east-1:213442566731:AlertCVS'
            # ,TargetArn='string', (Optional - can't be used with PhoneNumer)
            # ,Subject='string', (Optional - not used with PhoneNumer)
            # ,MessageStructure='string' (Optional)
            )

# print(openlist['data'])
# write sitelist.json
# if notifylist is not empty, email it

# def writeToS3(json_data):
#    s3 = boto3.resource('s3')
#    s3object = s3.Object('your-bucket-name', 'your_file.json')
#    diskey = "xxxx"
#    s3object.put(
#        Body=(bytes(json.dumps(json_data).encode('UTF-8'))
#        # , Key = dstKey
#        #, ContentType='application/json')
#        )


# if __name__ == "__main__":
#    lambda_handler()
