#!/usr/bin/env python
#
# exaMiner - Copyright 2011 Istvan Gazsi
#
# -----
#
# Tetszolegesen megvaltoztathato a varakozasi ido, a linkek listaja es a ZH neve
# igy mas ZH-nal is hasznalhato.
# Ekezetes betuk hasznalata hibat okoz, egyelore...
#
# Javaslatokkal es hibajelentesekkel ezen a cimen kereshettek:
# < theag3nt at gmail dot com >
#
# -----
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys, numbers, urllib2, hashlib, datetime, time#, optparse, base64


# ----- BEALLITASOK -----
# (Hibas vagy nem megadott ertekek eseten a program futas kozben keri be az
#  adatokat)
#
# Varakozasi ido ket frissites kozott masodpercben. Ne legyen tul alacsony, mert
# akkor a gyakori frissitesek miatt tilthatjak a hozzaferest. 0 eseten a program
# megkerdezi indulaskor.
sleep = 0
# A figyelt ZH neve (ha tobb peldany is fut a programbol akkor hasznos).
name = "" # Nincs hasznalva!
# Az eredmenyeket tartalmazo fajlok elnevezese es URL-je.
results = (
    # ("Pelda fajl", "http://pelda.bme.hu/~nev/eredmenyek.pdf"),
    )
# Utolso frissites idejenek formatuma
datimeformat = "%Y.%m.%d - %H:%M:%S"
# 
#
# ----- BEALLITASOK VEGE -----


class Result:
    
    def __init__(self, url, title=None, hash=None, info=""):
        self.url = url
        self.title = title
        self.info = info
        self.status = 0
        self.statusinfo = ""
        self.hash = hash

    def setinfo(self, info=None):
        if info:
            self.info = info
    
    def check(self):
        try:
            file = urllib2.urlopen(self.url)
            md5 = hashlib.md5()
            md5.update(file.read())
            if self.hash:
                if (md5.hexdigest() == self.hash):
                    self.status = 1
                else:
                    self.status = 2
            else:
                self.hash = md5.hexdigest()
                self.status = 1
            file.close()
            statusinfo = ""
        except urllib2.HTTPError, e:
            if e.code == 404:
                self.status = -1
                self.hash = "HTTP404"
            else:
                self.status = -2
                self.statusinfo = str(e.code)
                self.hash = "HTTP{0}".format(e.code)
        except urllib2.URLError, e:
            self.status = -3
            self.statusinfo = str(e.reason)
            self.hash = "URLError"


class ResultSet:
    
    def __init__(self):
        self.results = []

    def __len__(self):
        return len(self.results)

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            if key < len(self.results) and key >= 0:
                return self.results[key]
            else:
                raise IndexError
        else:
            raise TypeError

    def append(self, result=None):
        if isinstance(result, Result):
            self.results.append(result)
    
    def populate(self, results=None):
        for res in results:
            if len(res) > 2:
                self.results.append(Result(res[1], res[0], res[2]))
            elif len(res) > 1:
                self.results.append(Result(res[1], res[0]))


class zh_results:
    
    statusset = {-3:"Hiba", -2:"HTTP{0}", -1:"HTTP404", 0:"Ismeretlen", 1:"Valtozatlan", 2:"Frissitve!"}
    infoset = {-3:"{0} - {1}", -2:"{0} - {1} szamu HTTP hiba", -1:"{0} - Nem talalhato", 0:"{0} - Nincs ellenorizve", 1:"{0} - Ellenorizve", 2:"{0} - Inditas ota frissult"}
    datetimeformat = "%H:%M:%S"
    
    def __init__(self, name=None, results=[], sleep=600):
        #self.name = name
        self.results = ResultSet()
        self.results.populate(tuple(results))
        self.sleep = sleep
        self.maxlen = 3
        self.maxstatuslen = 7
        for status in self.statusset.values():
            if len(status) > self.maxstatuslen:
                self.maxstatuslen = len(status)

    def interactive_input(self):
        try:
            results = []
            self.print_header("Adatok bekerese...", False, False, False)
            #while not self.name:
            #    self.name = raw_input("ZH neve: ")
            while self.sleep <= 0:
                self.sleep = int(raw_input("Frissitesi gyakorisag (masodpercben): "))
            print "\nEllenorizendo eredmenyek (Ctrl+C-vel befejezheti a hozzaadast):"
            while True:
                self.results.append(Result(raw_input("\nURL (webcim): "), raw_input("Nev: ")))
        except KeyboardInterrupt:
            if self.results:
                return True
            else:
                print "\nHiba: Nem adott meg ellenorizendo eredmenyeket"
                return False
        except ValueError, e:
            print "\nHiba: Ervenytelen frissitesi gyakorisag"
            return False

    def format_sleep(self):
        if self.sleep >= 3600:
            if self.sleep % 3600 == 0:
                return "{0:d} orankent".format(self.sleep / 3600)
            else:
                return "{0:.1f} orankent".format(self.sleep / 3600.0)
        elif self.sleep >= 60:
            if self.sleep % 60 == 0:
                return "{0:d} percenkent".format(self.sleep / 60)
            else:
                return "{0:.1f} percenkent".format(self.sleep / 60.0)
        elif self.sleep > 0:
            return "{0} masodpercenkent".format(self.sleep)
        else:
            return None
    
    def format_time(self):
        if self.datetimeformat:
            return datetime.datetime.now().strftime(self.datetimeformat)
        else:
            return datetime.datetime.now().strftime("%Y.%m.%d. %H:%M:%S")

    def print_header(self, status=None, show_sleep=True, show_name=False, can_quit=True):
        print 100 * "\n"
        print "exaMiner - ZH eredmenyellenorzo\n-------------------------------\n"
        if status:
            print status, "\n"
        if show_sleep:
            print "Frissites {0}.".format(self.format_sleep()),
        if can_quit:
            print "Kilepes a Ctrl+C billentyukombinacioval...\n"
        else:
            print "Befejezes a Ctrl+C billentyukombinacioval...\n"
        #if show_name:
        #    print self.name, "eredmenyei\n"

    def print_results(self):
        if len(self.results):
            self.print_header(show_name=True)
            print "{0:{width}} | {1:{statuswidth}} | {2}".format("Nev", "Statusz", "Info", width=self.maxlen, statuswidth=self.maxstatuslen)
            print "{0:-<{width}} | {1:-<{statuswidth}} | {2}".format("", "", "--------------------", width=self.maxlen, statuswidth=self.maxstatuslen)
            for res in self.results:
                print "{0:{width}} | {1:{statuswidth}} | {2}".format(res.title, self.statusset[res.status].format(res.statusinfo), res.info, width=self.maxlen, statuswidth=self.maxstatuslen)

    def check(self, interactive=False):
        try:
            #if not (self.name and self.results and self.sleep > 0):
            if not (self.results and self.sleep > 0):
                if not self.interactive_input():
                    return False
            if self.sleep > 0:
                if self.results:
                    first_run = True
                    while True:
                        if first_run:
                            self.print_header("Kezdeti allapotok tarolasa...")
                            first_run = False
                            for res in self.results:
                                if len(res.title) > self.maxlen:
                                    self.maxlen = len(res.title)
                                res.check()
                        self.print_header("Eredmenyek ellenorzese...")
                        for res in self.results:
                            res.check()
                            res.setinfo(self.infoset[res.status].format(self.format_time(), res.statusinfo))
                        self.print_results()
                        time.sleep(self.sleep)
                else:
                    print "\nHiba: Nincsenek ellenorizendo eredmenyek"
                    return False
            else:
                print "\nHiba: Nincs megadva ervenyes frissitesi gyakorisag"
                return False
        except KeyboardInterrupt:
            print "\n\nKilepes..."
            time.sleep(1)
            return True
        except Exception, e:
            ecls, eprm = sys.exc_info()[:2]
            print "Ismeretlen hiba:", str(e)
            print "Exception:", ecls, "\nParameter:", eprm, "\n"
            return False


if __name__ == "__main__":
    result = zh_results(name, results, sleep)
    if not result.check():
        raw_input("Nyomjon <Enter>-t a kilepeshez...")
        sys.exit(1)
