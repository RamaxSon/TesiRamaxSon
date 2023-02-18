import mne
from mne_connectivity import envelope_correlation
import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QDialog, QGridLayout, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QDialogButtonBox


class Function:
    """
    Funzione che .
    """

    """Definizione parametri della funzione"""

    def __init__(self):
        self.needSignal = True
        self.parameters = {"soglia": {"type": "float", "value": 0.3, "default": 0.3},
                           "distance": {"type": "float", "value": 0.05, "default": 0.6,
                                        "desc": "Esprimere la distanza in cm nella quale calcolare la correlazione con i vicini"}}

    """Imposta i parametri della funzione"""

    def new(self, args):
        for key in args.keys():
            self.parameters[key]["value"] = args[key]["value"]

    def euclideanDistance(self, vett1, vett2):
        from math import sqrt
        d = sqrt((float(vett2[0]) - float(vett1[0]))**2 + (float(vett2[1]) - float(vett1[1]))**2 + (float(vett2[1]) - float(vett1[2]))**2)
        return d

    def Correlation(self):
        from scipy.stats import pearsonr
        from statistics import mean
        correlations = {}
        means = {}
        excluded = []
        for i in range(0, len(self.signal.info["ch_names"])):
            correlations[self.signal.info["ch_names"][i]] = []
            for j in range(0, len(self.signal.info["ch_names"])):
                if i != j and self.euclideanDistance(self.signal.info["chs"][i]["loc"][:3], self.signal.info["chs"][j]["loc"][:3]) <= float(self.parameters["distance"]["value"]):
                    corr_coef = pearsonr(self.signal.get_data(self.signal.info["ch_names"][i])[0], self.signal.get_data(self.signal.info["ch_names"][j])[0])
                    correlations[self.signal.info["ch_names"][i]].append(abs(corr_coef[0]))
            try:
                means[self.signal.info["ch_names"][i]] = mean(correlations[self.signal.info["ch_names"][i]])
            except ValueError as e:
                print("Error in the channel : "+self.signal.info["ch_names"][i])
                print(e)
                print("Maybe the distance is too small, check it and remember it is in centimeters")
                print("---------------------")
        for index in means.keys():
            if means[index] <= float(self.parameters["soglia"]["value"]):
                excluded.append(index)
        self.parameters["excluded"] = {}
        self.parameters["excluded"]["value"] = excluded

    def run(self, args, signal: mne.io.read_raw):
        self.new(args)
        self.signal = signal
        try:
            self.Correlation()
            if self.parameters["excluded"]["value"] != []:
                signal.info["bads"] = self.parameters["excluded"]["value"]
            return signal
        except ValueError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Operation denied")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Warning)
            messageError = msg.exec()
            return signal
