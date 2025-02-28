import abc
from Model.Palettes import Category20_9 as cols
import os
import matplotlib as mpl
import PyQt5
import seaborn as sb
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
import future.utils
import past
import six

class InitializationException(Exception):
    """Initialization Exception"""


@six.add_metaclass(abc.ABCMeta)
class ComparisonPlot(object):
    # __metaclass__ = abc.ABCMeta

    def __init__(self, models, trends, plt, statuses=["Infected"]):
        self.models = models
        self.trends = trends
        if plt != None:
            self.plt = plt
            self.headmap = False
        else:
            self.headmap = True
        if len(models) != len(trends):
            raise InitializationException({"message": "The number of models does not match the number of trends"})

        sts = [model.available_statuses for model in models]
        self.mnames = ["%s_%s" % (models[i].name, i) for i in past.builtins.xrange(0, len(models))]
        self.srev = {}
        i = 0

        available_classes = {}
        for model in models:
            srev = {v: k for k, v in future.utils.iteritems(sts[i])}
            self.nnodes = model.graph.number_of_nodes()
            for cl in list(srev.values()):
                available_classes[cl] = None

            self.srev["%s_%s" % (model.name, i)] = srev
            i += 1

        if type(statuses) == list:
            cls = set(statuses) & set(available_classes.keys())
        else:
            cls = set([statuses]) & set(available_classes.keys())
        if len(cls) > 0:
            self.classes = cls
        else:
            raise InitializationException({"message": "Statuses specified not available for the model (or missing)"})

        self.ylabel = ""
        self.title = ""
        self.normalized = False


    @abc.abstractmethod
    def iteration_series(self, percentile):
        """
        Prepare the data to be visualized

        :param percentile: The percentile for the trend variance area
        :return: a dictionary where iteration ids are keys and the associated values are the computed measures.
        """
        pass

    def plot(self, filename=None, percentile=90):
        """
        Plot the comparison on file.

        :param filename: the output filename
        :param percentile: The percentile for the trend variance area. Default 90.

        """
        pres = self.iteration_series(percentile)
        mpl.use('Qt5Agg')
        mx = 0
        i, h = 0, 0
        lol = []
        for k, l in future.utils.iteritems(pres):
            j = 0
            cont = 0
            for st in l:
                mx = len(l[st][0])
                cont += 1
                if self.normalized == True and self.headmap != True:
                    self.plt.plot(list(range(0, mx)), l[st][1]/self.nnodes, lw=2,
                             label="%s - %s" % (k.split("_")[0], st), alpha=0.9, color=cols[h+j])
                    self.plt.fill_between(list(range(0,  mx)), l[st][0]/self.nnodes,
                                     l[st][2]/self.nnodes, alpha=0.2, color=cols[h+j])
                elif self.headmap != True:
                    self.plt.plot(list(range(0, mx)), l[st][1], lw=2,
                             label="%s - %s" % (k.split("_")[0], st), alpha=0.9, color=cols[h + j])
                    self.plt.fill_between(list(range(0, mx)), l[st][0],
                                     l[st][2], alpha=0.2, color=cols[h + j])
                j += 1
                if cont == len(l):
                    lol = l[st][1] / self.nnodes
                    print(lol)
            i += 1
            h += 2
        if self.headmap != True:
            self.plt.grid(axis="y")
            self.plt.set_xlabel("Iteraciones", fontsize=15)
            self.plt.set_ylabel("Nodos infectados", fontsize=15)
            self.plt.legend(loc="best", fontsize=10)
            self.plt.set_xlim(0,mx)
            if self.normalized:
                self.plt.set_ylim((0, 1))
            self.plt.figure.tight_layout()
            if filename is not None:
                self.plt.figure.savefig(filename)  
                # plt.clf()
            #self.plt.figure.show()
        return lol