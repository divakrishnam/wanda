from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from oauth2client.service_account import ServiceAccountCredentials
from dateutil.parser import parse
import datetime
import face_recognition
import cv2
import numpy as np
import gspread
import os
import dawet
from time import sleep

class Chatbot(object):
    # def __init__(self, filename):
    #     self.filename = filename
    #     self.openDb()
    #
    # def openDb(self):
    #     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    #     creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    #     client = gspread.authorize(creds)
    #     self.sheet = client.open(self.filename)
    #
    # def getData(self, rowname, colname, sheetnum):
    #     self.dataError = True
    #     while self.dataError:
    #         try:
    #             ambilData = self.sheet.get_worksheet(sheetnum).cell(
    #                 self.sheet.get_worksheet(sheetnum).find(rowname).row,
    #                 self.sheet.get_worksheet(sheetnum).find(colname).col).value
    #             return ambilData
    #         except Exception as e:
    #             if str(e).find("RESOURCE_EXHAUSTED"):
    #                 print("wait ...")
    #                 sleep(100)
    #                 self.dataError = True

    def getNilaiMahasiswa(self, npm, pertemuan):
        if npm[:3] == "118":
            db = dawet.Dawet("BukuProyek2")
        elif npm[:3] == "117":
            db = dawet.Dawet("BukuProyek3")
        else:
            db = dawet.Dawet("BukuInternship1")

        nilai = db.getData(npm, pertemuan, 0)

        if nilai == "not_found":
            return "invalid"
        elif nilai == "pertemuan_not_found":
            return "pertemuan_invalid"
        else:
            nama_mahasiswa = db.getData(npm, "nama", 0)
            nilai_rata = db.getData(npm, "rata_rata", 0)

            hasil = []
            hasil.append(nilai)
            hasil.append(nama_mahasiswa)
            hasil.append(nilai_rata)

            return hasil

    def cekJadwalSidang(self, pilihan):
        db = dawet.Dawet("Jadwal_Sidang_Proyek_2")

        allData = db.getAllData(1)

        sekarang = datetime.datetime.now().date()
        besok = sekarang + datetime.timedelta(days=1)
        kemaren = sekarang - datetime.timedelta(days=1)
        lusa = sekarang + datetime.timedelta(days=2)

        if pilihan == "sekarang":
            self.pilihanTanggal = sekarang
            runnerVariable = 1
        if pilihan == "besok":
            self.pilihanTanggal = besok
            runnerVariable = 1
        if pilihan == "kemarin":
            self.pilihanTanggal = kemaren
            runnerVariable = 1
        if pilihan == "lusa":
            self.pilihanTanggal = lusa
            runnerVariable = 1

        if runnerVariable == 1:
            for data in allData:
                try:
                    tanggal = parse(data[0]).date()
                    print(self.pilihanTanggal)

                    print(tanggal)

                    if self.pilihanTanggal == tanggal:
                        getIndex = allData.index(data)

                        nextData = allData[getIndex:]

                        for nextdata in nextData:
                            if nextdata[0] == '':
                                getIndexNull = nextData.index(nextdata)

                        result = nextData[:getIndexNull]

                        return result

                except:
                    print("beda")
        else:
            return "no_pilihan"


    def saveProfile(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--user-data-dir=./user_data')
        self.driver = webdriver.Chrome(chrome_options=self.options)

    def splitString(self, string):
        li = list(string.split(" "))
        return li

    def waitLogin(self):
        self.target = '"_3RWII"'
        self.x_arg = '//div[contains(@class, ' + self.target + ')]'
        self.wait = WebDriverWait(self.driver, 600)
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.x_arg)))

    def typeAndSendMessage(self, message):
        self.message_target = self.driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')[0]
        self.message_target.send_keys(message)
        self.sendbutton = self.driver.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button')[0]
        self.sendbutton.click()

    def deleteMessage(self):
        self.driver.find_elements_by_class_name('_3j8Pd')[-1].click()
        sleep(1)

        value_name = self.driver.find_elements_by_class_name('_3zy-4')
        sleep(1)

        if 'Exit group' in value_name[4].text:
            print('group')
            value_name[3].click()
            self.driver.find_elements_by_class_name('_2eK7W')[1].click()
        else:
            print('personal')
            value_name[4].click()
            self.driver.find_elements_by_class_name('_2eK7W')[1].click()

    def cekAndSendMessage(self):
        try:
            try:
                self.chat = self.driver.find_elements_by_class_name("P6z4j")[0]
                self.chat.click()
                self.chat.click()
                self.chat.click()
            except:
                print('skip data')

            sleep(0.5)

            self.span = self.driver.find_elements_by_xpath('(.//span)')[-11].text

            self.spanLower = self.span.lower()

            self.message = self.splitString(self.spanLower)

            if "wanda" in self.message:
                self.typeAndSendMessage("iya crot, aya naon?")

            if "sidang" in self.message:
                try:
                    jadwal = self.cekJadwalSidang(self.message[1])
                    jadwal.pop(0)
                    jadwal.pop(0)

                    if jadwal == "no_pilihan":
                        self.typeAndSendMessage("pilihan salah")
                    else:
                        for i in jadwal:
                            self.typeAndSendMessage("NPM: "+i[0]+", Nama: "+i[1]+", Penguji utama: "+i[2]+", Penguji pendamping: "+i[3]+", Jam: "+i[5]+", Lokasi: "+i[6])
                except:
                    self.typeAndSendMessage("jadwal sidang "+self.message[1]+" tidak ada")

            if "nilai" in self.message:
                npm = self.message[1]
                pertemuan = self.message[2]
                hasil = self.getNilaiMahasiswa(npm, pertemuan)

                if hasil == "invalid":
                    self.typeAndSendMessage("npm saha ieu crot?")
                elif hasil == "pertemuan_invalid":
                    self.typeAndSendMessage("format salah, contoh: nilai 1184047 pertemuan1")
                else:
                    self.typeAndSendMessage("NPM: "+npm+", Nama: "+hasil[1]+", Nilai: "+hasil[0]+", Nilai rata-rata: "+hasil[2])


            if "love" in self.message:
                self.typeAndSendMessage("love you too <3")

            if "bioskop" in self.message:
                self.movieSchedule(self.message)

            if "perhutani" in self.message:
                self.perhutani()

            if "gmaps" in self.message:
                self.message.pop(0)
                desti2 = self.listToString(self.message)
                self.gmaps(desti2)

            if "foto" in self.message:
                sleep(1)
                name = self.getName()
                sleep(1)
                self.retrievePicture()
                sleep(1)
                self.renamePicture(name)
                sleep(1)
                self.sendPicture(self.message[1], name)
                sleep(1)
                self.deletePicture()
                sleep(1)

            if "gambar" in self.message:
                sleep(1)
                name = self.getName()
                sleep(1)
                self.retrievePicture()
                sleep(1)
                self.renamePicture(name)
                sleep(1)
                objectnames = self.listToString(self.loadYolo(self.cocoNamesLoad(), name))
                sleep(1)
                self.deletePicture()
                sleep(1)
                self.typeAndSendMessage("Difoto terakhir yang dikirim ada object: " + objectnames)

            if "face" in self.message:
                sleep(1)
                name = self.getName()
                sleep(1)
                self.retrievePicture()
                sleep(1)
                self.renamePicture(name)
                sleep(1)
                faceNames = self.listToString(self.faceRecognition(name))
                sleep(1)
                self.deletePicture()
                sleep(1)
                self.typeAndSendMessage("Difoto terakhir yang dikirim orangnya ada: " + faceNames)
                sleep(1)

        except Exception as e:
            print(e)
            print("No Message..")

    def listToString(self, message):
        pesan = " "

        return (pesan.join(message))

    def movieSchedule(self, message):
        keyWatch = ["bioskop", "film", "pilem"]
        cityName = ["jakarta", "bandung"]
        locationName = ["braga", "btc"]
        cinemaName = ["xxi"]

        for i in message:
            if i in keyWatch:
                for j in message:
                    if j in cityName:
                        self.namkot = j
                    if j in cinemaName:
                        self.nambios = j
                    if j in locationName:
                        self.namlok = j

        sleep(1)

        self.driver.execute_script("window.open('https://jadwalnonton.com/bioskop/di-" + self.namkot + '/' + self.namlok + '-' + self.nambios + '-' + self.namkot + ".html');")

        self.driver.switch_to_window(self.driver.window_handles[1])
        try:
            error = self.driver.find_element_by_xpath("//div[contains(@class, 'caution')]").text
            if "404" in error:
                self.driver.close()
                sleep(1)
                self.driver.switch_to_window(self.driver.window_handles[0])
                sleep(1)
                self.typeAndSendMessage("Data not found")
        except:
            jumlah = self.driver.find_elements_by_xpath("//div[contains(@class, 'col-sm-10 sched_desc')]")
            jadwal = ""
            for i in jumlah:
                jadwal = i.text + jadwal
            self.driver.close()
            sleep(1)
            self.driver.switch_to_window(self.driver.window_handles[0])
            sleep(1)
            jadwalFix = jadwal.replace("LIHAT DI BIOSKOP LAIN", "")
            sleep(1)
            self.typeAndSendMessage(jadwalFix)

    def perhutani(self):
        usEmail = "email"
        usPass = "password"

        self.driver.execute_script("window.open('https://www.tokoperhutani.com/beranda/searchFromRecap/4140100/4141100/4141102/010')")
        sleep(.5)

        self.driver.switch_to_window(self.driver.window_handles[1])
        sleep(2)

        self.driver.find_element_by_link_text("Login").click()
        sleep(.5)

        self.driver.find_element_by_id("email").send_keys(usEmail)
        self.driver.find_element_by_id("password").send_keys(usPass)

        self.driver.find_elements_by_class_name("le-button")[0].click()
        sleep(60)

        wekser = ['193150214695', '193150214696', '193150214751', '193150215151', '193150215166', '193150215173',
                  '193150215178', '193150215190', '193150215192', '193150215398', '193150215511', '193150215524',
                  '193150214698', '193150215373']

        cariData = True

        forCounting = []

        self.driver.find_elements_by_class_name("paginate_button")[6].click()

        tableDataofOrder = self.driver.find_elements_by_xpath("//table[@id='example' and @class='display select nowrap dataTable no-footer']/tbody/tr")

        for i in tableDataofOrder:
            getNumberofOrder = i.text[9:22]
            splitting = getNumberofOrder.splitlines()
            forCounting.append(splitting)

        count = 10 - len(forCounting)

        while cariData:
            asd = self.driver.find_elements_by_xpath("//table[@id='example' and @class='display select nowrap dataTable no-footer']/tbody/tr")

            for i in asd:
                count += 1
                getNumberofOrder = i.text[9:22]
                splitting = getNumberofOrder.splitlines()

                if splitting[0] in wekser:
                    i.click()
                    wektow = wekser.index(splitting[0])
                    wekser.pop(wektow)

                if len(wekser) == 0:
                    cariData = False
                    self.driver.find_elements_by_class_name("le-button")[1].click()
                if count == 10 and len(wekser) >= 1:
                    print("There still another order, still working..")
                    count = 0
                    self.driver.find_element_by_id("example_previous").click()

    def gmaps(self, destination):
        self.driver.find_elements_by_class_name("_15Rkh")[-1].click()
        sleep(1)

        self.driver.switch_to_window(self.driver.window_handles[1])
        sleep(1)

        self.destination = destination
        sleep(1)

        self.coordinate = self.driver.find_element_by_id("searchboxinput").get_attribute("value")
        sleep(1)

        self.driver.find_element_by_id("sb_cb50").click()
        sleep(1)

        self.driver.find_element_by_id("searchboxinput").send_keys(self.destination + Keys.ENTER)
        sleep(4)

        try:
            self.driver.find_elements_by_class_name("iRxY3GoUYUY__taparea")[0].click()
            sleep(1)
        except Exception as e:
            print(e)
            print("There are 2 object or more destination!")

            cekButton = self.driver.find_elements_by_class_name("section-result-action-text")[0].text

            if cekButton == "Website":
                print("Websites")
                self.driver.find_elements_by_class_name("section-result-action-text")[1].click()
                sleep(2)
            else:
                self.driver.find_elements_by_class_name("section-result-action-text")[0].click()
                sleep(2)

        self.driver.find_elements_by_class_name("tactile-searchbox-input")[2].click()
        sleep(1)

        self.driver.find_elements_by_class_name("tactile-searchbox-input")[2].send_keys(Keys.BACKSPACE)
        sleep(1)

        self.driver.find_elements_by_class_name("tactile-searchbox-input")[2].send_keys(self.coordinate + Keys.ENTER)
        sleep(1)

        currentUrl = self.driver.current_url
        sleep(1)

        self.driver.close()
        sleep(1)

        self.driver.switch_to_window(self.driver.window_handles[0])
        sleep(1)

        self.typeAndSendMessage(currentUrl)
        sleep(1)

    def sendPicture(self, phoneNumber, filePath):
        self.driver.get("https://web.whatsapp.com/send?phone=" + phoneNumber)

        self.waitLogin()
        sleep(3)

        self.driver.find_element_by_css_selector("span[data-icon='clip']").click()
        sleep(2)

        path = r"C:\Users\rolly\Downloads"
        nameFile = filePath + ".jpeg"

        result = os.path.join(path, nameFile)

        self.driver.find_element_by_css_selector("input[type='file']").send_keys(result)
        sleep(1)

        self.driver.find_element_by_css_selector("span[data-icon='send-light").click()
        sleep(1)

    def retrievePicture(self):
        self.driver.find_elements_by_class_name("_18vxA")[-1].click()
        sleep(1)

        self.driver.find_element_by_css_selector("span[data-icon='download']").click()
        sleep(1)

        self.driver.find_element_by_css_selector("span[data-icon='x-viewer']").click()
        sleep(1)

    def deletePicture(self):
        dir_name = "/Users/rolly/Downloads/"
        list = os.listdir(dir_name)

        for item in list:
            if item.endswith(".jpeg"):
                os.remove(os.path.join(dir_name, item))

    def getName(self):
        try:
            self.driver.find_element_by_class_name("_3fs0K").click()
            sleep(1)

            self.driver.find_element_by_class_name("_2vJOg").click()
            sleep(1)

            name = self.driver.find_elements_by_class_name("_F7Vk")[1].text
            sleep(1)

            self.driver.find_element_by_css_selector("span[data-icon='x-viewer']").click()
            sleep(1)
        except Exception as e:
            print(e)
            print("Grup")

            name = self.driver.find_elements_by_class_name("_3u328")[0].text
            sleep(1)

        return name

    def renamePicture(self, fileName):
        dir_name = "/Users/rolly/Downloads/"
        list = os.listdir(dir_name)

        print(list)

        for item in list:
            if item.endswith(".jpeg"):
                os.rename(os.path.join(dir_name, item), os.path.join(dir_name, fileName + ".jpeg"))

    def cocoNamesLoad(self):
        listClass = []

        with open("coco.names", "r") as daftarNama:
            for i in daftarNama.readlines():
                cocoNames = i.strip()
                listClass.append(cocoNames)

        return listClass

    def loadYolo(self, coconames, fileName):
        model = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")

        layerNames = model.getLayerNames()

        outputLayer = []

        for i in model.getUnconnectedOutLayers():
            outputLayer.append(layerNames[i[0] - 1])

        path = r"C:\Users\rolly\Downloads"
        nameFile = fileName + ".jpeg"

        result = os.path.join(path, nameFile)

        img = cv2.imread(result)

        width, height, channels = img.shape

        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        model.setInput(blob)
        outs = model.forward(outputLayer)

        boxes = []
        class_ids = []
        confidences = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)

                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    class_ids.append(class_id)
                    confidences.append(float(confidence))

        objectNames = []
        for i in range(len(boxes)):
            label = coconames[class_ids[i]]

            if label in objectNames:
                print("The object exist of list")
            else:
                objectNames.append(label)

        return objectNames

    def faceRecognition(self, fileName):

        rolly_picture = face_recognition.load_image_file("rolly.jpg")
        rolly_encoding = face_recognition.face_encodings(rolly_picture)[0]

        angga_picture = face_recognition.load_image_file("angga.jpg")
        angga_encoding = face_recognition.face_encodings(angga_picture)[0]

        known_face_encodings = [
            rolly_encoding,
            angga_encoding
        ]

        known_face_names = [
            "Rolly M.A.",
            "Tri Angga D.S"
        ]

        path = r"C:\Users\rolly\Downloads"
        nameFile = fileName + ".jpeg"

        result = os.path.join(path, nameFile)

        test_image = face_recognition.load_image_file(result)

        face_locations = face_recognition.face_locations(test_image)
        face_encodings = face_recognition.face_encodings(test_image, face_locations)

        name = []

        for face_encoding in face_encodings:
            results = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.45)

            if True in results:
                match_index = results.index(True)
                name.append(known_face_names[match_index])

        return name

    def openBrowser(self):
        self.saveProfile()
        self.driver.get("https://web.whatsapp.com/")
        self.waitLogin()
