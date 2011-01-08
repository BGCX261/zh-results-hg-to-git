#!/usr/bin/env python
#
# ZH eredmenyellenorzo - Copyright 2010 Istvan Gazsi
#
# -----
#
# Tetszolegesen megvaltoztathato a varakozasi ido, a linkek listaja es a ZH neve igy mas ZH-nal is hasznalhato.
# Ekezetes betuk hasznalata hibat okoz, egyelore...
#
# Javaslatokkal es hibajelentesekkel ezen a cimen kereshettek: < theag3nt at gmail dot com >
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

import sys, urllib2, hashlib, time#, optparse, base64


# ----- BEALLITASOK -----
# (Hibas vagy nem megadott ertekek eseten a program futas kozben keri be az adatokat)
#
# Varakozasi ido ket frissites kozott masodpercben. Ne legyen tul alacsony, mert akkor a gyakori frissitesek miatt tilthatjak a hozzaferest.
sleep = 0
sleep = int(sleep)
# A figyelt ZH neve (ha tobb peldany is fut a programbol akkor hasznos).
name = ""
# Az eredmenyeket tartalmazo fajlok elnevezese es URL-je.
results = (
    # ("Pelda fajl", "http://pelda.bme.hu/~nev/eredmenyek.pdf"),
    )
#hashes = []
#
# ----- BEALLITASOK VEGE -----


class zh_results:
    
    def __init__(self, name=None, results=[], hashes=[], sleep=600):
        self.initialize(name, results, hashes, sleep)

    def initialize(self, name=None, results=[], hashes=[], sleep=600):
        self.name = name
        self.results = tuple(results)
        self.hashes = hashes
        self.sleep = sleep
        self.maxlen = 0
        for title, url in self.results:
            if len(title) > self.maxlen:
                self.maxlen = len(title)

    def interactive_input(self):
        try:
            results = []
            self.print_header("Adatok bekerese...", False, False, False)
            name = raw_input("ZH neve: ")
            sleep = int(raw_input("Frissitesi gyakorisag (masodpercben): "))
            if not sleep > 0:
                raise ValueError
            print "\nEllenorizendo eredmenyek (Ctrl+C-vel befejezheti a hozzaadast):"
            while True:
                results.append((raw_input("\nCimke: "), raw_input("URL (webcim): ")))
        except KeyboardInterrupt:
            if results:
                self.initialize(name, results, sleep=sleep)
                return True
            else:
                print "Hiba: Nem adott meg ellenorizendo eredmenyeket"
                return False
        except ValueError, e:
            print "Hiba: Ervenytelen frissitesi gyakorisag"
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

    def print_header(self, status=None, show_sleep=True, show_name=False, can_quit=True):
        print 100 * "\n"
        print "ZH eredmenyellenorzo\n--------------------\n"
        if status:
            print status, "\n"
        if show_sleep:
            print "Frissites {0}.".format(self.format_sleep()),
        if can_quit:
            print "Kilepes a Ctrl+C billentyukombinacioval...\n"
        else:
            print "Befejezes a Ctrl+C billentyukombinacioval...\n"
        if show_name:
            print self.name, "eredmenyei\n"

    def print_results(self, statuses=[]):
        if len(statuses) == len(self.results):
            self.print_header(show_name=True)
            for i in xrange(len(statuses)):
                print "{0:{1}} -".format(self.results[i][0], self.maxlen),
                if not statuses[i]:
                    print "Valtozatlan"
                else:
                    print " FRISSITVE! <-"

    def check(self, interactive=False):
        try:
            if not (name and results and sleep > 0):
                if not self.interactive_input():
                    return False
            if self.sleep > 0:
                if self.results:
                    statuses = []
                    while True:
                        if len(self.hashes) == 0:
                            self.print_header("Kezdeti allapotok tarolasa...")
                            for title, url in self.results:
                                file = urllib2.urlopen(url)
                                md5 = hashlib.md5()
                                md5.update(file.read())
                                self.hashes.append(md5.hexdigest())
                                statuses.append(False)
                        elif len(self.hashes) == len(self.results):
                            self.print_header("Eredmenyek ellenorzese...")
                            for i in xrange(len(self.hashes)):
                                file = urllib2.urlopen(self.results[i][1])
                                md5 = hashlib.md5()
                                md5.update(file.read())
                                if (md5.hexdigest() == self.hashes[i]):
                                    statuses[i] = False
                                else:
                                    statuses[i] = True
                        self.print_results(statuses)
                        time.sleep(self.sleep)
                else:
                    print "Hiba: Nincsenek ellenorizendo eredmenyek"
                    return False
            else:
                print "Hiba: Nincs megadva ervenyes frissitesi gyakorisag"
                return False
        except KeyboardInterrupt:
            print "\n\nKilepes..."
            time.sleep(1)
            return True
        except urllib2.URLError, e:
            print "Hiba:", str(e.reason)
            return False
        except Exception, e:
            print "Ismeretlen hiba:", str(e)
            return False


if __name__ == "__main__":
    result = zh_results(name, results, sleep=sleep)
    if not result.check():
        raw_input("Nyomjon <Enter>-t a kilepeshez...")
        sys.exit(1)
