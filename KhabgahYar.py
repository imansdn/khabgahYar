import re

import requests
from bs4 import BeautifulSoup
import mysql.connector
from sklearn import tree
from unidecode import unidecode

page = 1
counter = 1
max_result = 1000
# city = "tehran"
category = "املاک-مسکن"
subject = "خوابگاه"
x = []
y = []
your_host = 'localhost'
your_user = 'root'
your_pass = ''
db_name = "room_db"
table_name = "room_details"
mydb = mysql.connector.connect(
    host=your_host,
    user=your_user,
    passwd=your_pass,
)
mycursor = mydb.cursor()

# mycursor.execute("Drop DATABASE {};".format(db_name))

mycursor.execute("CREATE DATABASE IF NOT EXISTS {};".format(db_name))

mycursor.execute("USE {}  ; ".format(db_name))

mycursor.execute("Drop Table  {}  ;".format(table_name))

mycursor.execute(
    "CREATE TABLE IF NOT EXISTS {} (id INT( 11 ) NOT NULL  AUTO_INCREMENT PRIMARY KEY"
    ", name VARCHAR(255)"
    ", time VARCHAR(255)"
    ", loc VARCHAR(255)"
    ", page VARCHAR(255)"
    ", vadieh VARCHAR(255)"
    ",ejareh VARCHAR(255));".format(
        table_name))

print("*************************** خوابگاه یار ***************************")
print("* با سلام من ربات خوابگاه یار هستم که در این برنامه با اطلاعاتی که  *")
print("* از سایت دیوار میگیرم و با کمک  ماشین لرنینگ ، با توجه به میزان  *")
print("* ودیعه و اجاره ی ماهیانه ای که میتونید پرداخت  کنید، به شما میگم *")
print("* که کدوم محله میتونید یک خوابگاه مناسب پیدا کنید :)              *")
print("*******************************************************************")

city = input("توی کدام شهر میخواهید خوابگاه پیدا کنید؟ ( به طور مثال :tehran )؟" + "\n")

print("در حال بررسی اطلاعات هستم لطفا کمی صبر کنید ..."+"\n")
while counter <= max_result:
    r = requests.get(
        "https://divar.ir/" + city + "/browse/" + category + "/?query=0," + subject + "&page=" + str(page))
    # print("page ==== {}".format(page))
    # print(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    rooms = soup.find_all("div", attrs={'class': 'ui internally celled grid'})
    if len(rooms) == 0:
        break
    # print(len(rooms))
    # print(rooms)
    for room in rooms:
        if counter > max_result:
            break
        if room is not None:
            content = room.find("div", {"class": "column content"})
            price = room.find("div", {"class": "column price"})
            if content is not None:
                name = content.find("h2").text
                desc = content.find("div", {"class": "description"})
                if desc is not None:
                    room_location = desc.find("label")
                    time_added = desc.find("div", {"class": "meta"})
                    if time_added is None:
                        urgent = desc.find("span", {"class": "urgent"})
                        if urgent.text.strip() == "فوری":
                            time_added = "urgent"
                            room_location = desc.find("label").text
                            if price is not None:
                                price = price.find_all("label", {"class": "item"})
                                if len(price) >= 2:
                                    ejareh = price[0].text.strip()
                                    vadieh = price[1].text.strip()
                                    ejareh = ejareh.split(":")[1].strip().split(" ")[0]
                                    vadieh = vadieh.split(":")[1].strip().split(" ")[0]
                                    if ejareh != "توافقی" and vadieh != "توافقی":
                                        vadieh = 0 if vadieh == "رایگان" else unidecode(vadieh)
                                        ejareh = 0 if ejareh == "رایگان" else unidecode(ejareh)
                                        ejareh = str(ejareh).replace(".", "")
                                        vadieh = str(ejareh).replace(".", "")
                                        if int(vadieh) != 0 or int(ejareh) != 0:
                                            ejareh = int(ejareh) * 1000 if int(ejareh) <= 1000 else ejareh
                                            vadieh = int(vadieh) * 1000 if int(vadieh) <= 1000 else vadieh
                                            sql = "INSERT INTO {} (name, time , loc , page , vadieh , ejareh) VALUES (%s, %s,%s, %s,%s, %s)".format(
                                                table_name)
                                            val = (name, time_added, room_location, page, vadieh, ejareh)
                                            mycursor.execute(sql, val)
                                            mydb.commit()
                                            # print("-----" + str(counter) + "-------")
                                            # print(ejareh)
                                            # print(vadieh)
                                            # print(name)
                                            # print(room_location)
                                            # print(time_added)
                                            counter += 1



                    else:
                        room_location = desc.find("label").text
                        time_added = desc.find("div", {"class": "meta"}).text
                        if price is not None:
                            price = price.find_all("label", {"class": "item"})
                            if len(price) >= 2:
                                ejareh = price[0].text.strip()
                                vadieh = price[1].text.strip()
                                ejareh = ejareh.split(":")[1].strip().split(" ")[0].strip()
                                vadieh = vadieh.split(":")[1].strip().split(" ")[0].strip()
                                if ejareh != "توافقی" and vadieh != "توافقی":
                                    vadieh = 0 if vadieh == "رایگان" else unidecode(vadieh)
                                    ejareh = 0 if ejareh == "رایگان" else unidecode(ejareh)
                                    ejareh = str(ejareh).replace(".", "")
                                    vadieh = str(ejareh).replace(".", "")
                                    if int(vadieh) != 0 or int(ejareh) != 0:
                                        ejareh = int(ejareh) * 1000 if int(ejareh) <= 1000 else ejareh
                                        vadieh = int(vadieh) * 1000 if int(vadieh) <= 1000 else vadieh
                                        sql = "INSERT INTO {} (name, time , loc , page , vadieh , ejareh) VALUES (%s, %s,%s, %s,%s, %s)".format(
                                            table_name)
                                        val = (name, time_added, room_location, page, vadieh, ejareh)
                                        mycursor.execute(sql, val)
                                        mydb.commit()
                                        x.append((str(vadieh), str(ejareh)))
                                        y.append((str(room_location)))
                                        # print("-----" + str(counter) + "(" + str(page) + ")" "-------")
                                        # print(ejareh)
                                        # print(vadieh)
                                        # print(name)
                                        # print(room_location)
                                        # print(time_added)
                                        counter += 1

    page += 1

clf = tree.DecisionTreeClassifier()
# clf = clf.fit(x, y)
clf.fit(x, y)
print(" خب من تونستم {} مورد رو بررسی کنم! فقط به دو سوال دیگه پاسخ بده و دقت کن که تمامی واحدها به تومان هست و همچنین "
      "میتونی برای حالت بدون ودیعه یا بدون اجاره از 0 استفاده کنی...".format(counter)+"\n")

mablagh = True
while mablagh :
    nVadieh = int(input("* چه میزان ودیعه می توانید پرداخت کنید؟" + "\n"))
    nEjaareh = int(input("* ماهیانه چه میزان اجاره میتوانید پرداخت کنید؟" + "\n"))
    if nVadieh <30000 and nEjaareh <30000:
        print("مبلغ ودیعه و اجاره حداقل  30 هزاتومان باید باشه!"+ "\n")
    else:
        mablagh = False
        break

answer = clf.predict([[nVadieh, nEjaareh]])

print("******************************************************************************************************************")
print("شما به احتمال زیاد در منطقه ی \"{}\" میتوانید یک اتاق داشته باشید!".format(answer[0]) )
print("******************************************************************************************************************")

print("\n"+
    "این لینکها رو هم نگاه کنید خوابگاه های {} هست با حدود قیمتی که گفتید پیدا کردم واستون :".format(answer[0]) + "\n")

sql = "select name from {} where loc = \"{}\" ;".format(table_name, answer[0])
mycursor.execute(sql)
for r in mycursor:
    r = r[0].strip()
    r = r.replace(" ", "%20")
    # r = r.encode("UTF-8")
    print("\" https://divar.ir/{}/browse/?query=0,{} \"".format(city, r))
