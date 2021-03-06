import numpy as np
from pprint import pprint
from scipy.special import expit as sigmoid
import pdb
import copy
import csv
import matplotlib.pyplot as plt
from multiprocessing import Process, Pool, Queue


class NN(object):

	def __init__(self, sample, result, hidden = [20], learning_rate=0.2, seed = 0, weights_m = 1):
		self.hidden_layers = 1
		if not isinstance(hidden, list): hidden = [hidden]
		self.hidden_nodes = hidden
		if seed != 0:
			np.random.seed(seed)
		if len(self.hidden_nodes) != self.hidden_layers:
			print("Hidden layers doesn't match hidden nodes array")
			return
		self.bias = 1
		self.layers = [len(sample)]
		self.layers.extend(self.hidden_nodes)
		self.layers.extend([len(result)])
		self.weights = []
		for s_in,s_out in zip(self.layers[:-1], self.layers[1:]):
			self.weights.append(weights_m*(2*np.random.random((s_in,s_out)) - 1))
		self.learning_rate = learning_rate


	def forward(self, sample):
		# forward propogation through the network
		in_data = sample
		self.nodes = []
		for i in range(len(self.layers[:-1])):
			layer_data = sigmoid(np.dot(in_data, self.weights[i]))
			self.nodes.append(copy.deepcopy(layer_data))
			in_data = copy.deepcopy(layer_data)
		return self.nodes[-1][0] #prediction after softmax -- do percentage on it somewhere?

	def backward(self, sample, result): 
		#back propogation through network
		error = self.nodes[-1] - result
		self.layer_delta = []
		for i in range(len(self.layers), 1, -1):
			if i == len(self.layers): #output layer so need to calculate loss
				delta = error * self.dsigmoid(self.nodes[-1])
			else:
				delta = np.dot(self.layer_delta[0], self.weights[i-1].T) * self.dsigmoid(self.nodes[i-2])
			self.layer_delta.insert(0,copy.deepcopy(delta))
		# layer_2_delta = error * self.dsigmoid(self.nodes[-1])
		# layer_1_delta = np.dot(layer_2_delta, self.weights[1].T) * self.dsigmoid(self.nodes[-2])
		# update weights
		#converting to matrices to make life easier
		self.nodes = map(np.asmatrix, self.nodes)
		self.layer_delta = map(np.asmatrix, self.layer_delta)
		sample = np.asmatrix(sample)
		for i in range(len(self.layers)-1, 0, -1):
			if i == 1:
				self.weights[i-1] -= self.learning_rate * np.dot(sample.T,self.layer_delta[i-1])
			else:
				self.weights[i-1] -= self.learning_rate * np.dot(self.nodes[i-2].T,self.layer_delta[i-1])

	def dsigmoid(self, sig_val): #derivative of sigmoid
		d = sig_val * (1.0 - sig_val)
		return d

	def epochs_train(self, epochs, data_x, data_y, test_x, test_y, show=False):
		acc = []
		for epoch in range(epochs):
			data_x, data_y = self.shuffle_data(data_x, data_y)
			self.train(data_x, data_y)
			test_x, test_y = self.shuffle_data(test_x, test_y)
			acc.append(self.test(test_x, test_y))
			if epoch % 100 == 0:
				print("Epoch %s: Accuracy -- %s %%" %(epoch, acc[-1]))
		if show:
			plt.plot(acc, 'rx')
			plt.show()
		return acc

	def shuffle_data(self, x, y):
		all_data = zip(x, y)
		np.random.shuffle(all_data)
		x, y = zip(*all_data)
		return x, y

	def train(self, x, y):
		for sample,result in zip(x, y):
			pred = self.forward(sample)
			self.backward(sample, result)
			# if np.round(pred) == float(result): c = 'Y'
			# else: c = 'N'
			# print("Predicted: %.2f, Actual: %s, Correct: %s" %(pred, result, c))		

	def test(self, xs, ys):
		p_good = 0.5
		accuracy = []
		preds = []
		for x,y in zip(xs, ys):
			pred = self.forward(x)
			preds.append(pred)
			if pred >= p_good and y == 1:
				accuracy.append(1)
			elif pred <= p_good and y == 0:
				accuracy.append(1)
			else:
				accuracy.append(0)
		# pdb.set_trace()
		# plt.plot(preds, 'ro')
		# plt.show()
		return sum(accuracy) / float(len(xs))



class AND_data(object):
	def __init__(self, data_points):
		self.count = data_points
		self.data = np.random.choice([0,1], (data_points, 2))
		self.y = (np.sum(self.data, axis = 1) > 1).reshape(-1,1)

	def print_data(self):
		for i in range(self.count):
			pprint('Sample: [%s, %s]    Y: %s' %(self.data[i,0], self.data[i,1], self.y[i]))

class XOR_data(AND_data):
	def __init__(self, data_points):
		self.count = data_points
		self.data = np.random.choice([0,1], (data_points, 2))
		self.y = (np.sum(self.data, axis = 1) == 1).reshape(-1,1)

class load_data(AND_data):
	def __init__(self, fn):
		with open(fn, 'rb') as csvfile:
			reader = csv.reader(csvfile)
			self.data = []
			self.y = []
			for row in reader:
				sample = np.array(row[:5]).astype(float)
				self.data.append(sample)
				result = int(float(row[-2]))
				self.y.append(result)
			self.y = np.array(self.y).reshape(-1,1)
		all_data = zip(self.data, self.y)
		np.random.shuffle(all_data)
		self.data, self.y = zip(*all_data) #post shuffled ordering!


class makePlots(object):
	def __init__(self, fn):
		self.data = load_data(fn)
		self.test_datas = map(load_data, ['test%s.csv' %i for i in range(1,4)])
		self.TRIALS = 10
		self.SEEDS = np.arange(self.TRIALS) * 1000
		self.EPOCH = 2000
		self.HIDDEN = 20
		self.LEARNING_RATE = 0.2
		self.hidden_units = [5, 20, 100]
		# self.epochs = [1, 10, 50]
		self.epochs = [200, 2000, 4000]
		self.learning_rates = [0.001, 0.2, 10]
		self.weights_range = [0.01, 1, 100]
		self.markers = ['ro', 'bx', 'g*']

	def recordData(self, save_dir):
		# each column is a trial
		# each row is a single epoch
		self.save_dir = save_dir
		self.partA()
		self.partB()
		self.partC()
		self.partE()

	def recordDataMultiP(self, save_dir):
		# each column is a trial
		# each row is a single epoch
		self.save_dir = save_dir
		self.partA_multiP()
		self.partB_multiP()
		self.partC_multiP()
		self.partE_multiP()

	def NN_all(self):
		nn = NN(self.data.data[0], self.data.y[0], hidden=hidden)
		acc = nn.epochs_train(self.EPOCH, self.data.data, self.data.y, self.test_datas[0].data, self.test_datas[0].y)

	def NN_multi(self, hidden, epoch, lr, seed, train_x, train_y, test_x, test_y, q, w_m = 1):
		# function specific for multiprocess
		nn = NN(train_x[0], train_y[0], hidden=hidden, learning_rate = lr, seed = seed, weights_m = w_m)
		acc = nn.epochs_train(epoch, train_x, train_y, test_x, test_y)
		q.put(acc)
				
	def partA_multiP(self):
		# runs with multiple threads
		for hidden in self.hidden_units:
			q = Queue()
			ps = [Process(target = self.NN_multi, args=(hidden, self.EPOCH, self.LEARNING_RATE, seed, self.data.data, self.data.y, self.test_datas[0].data, self.test_datas[0].y, q)) for i,seed in zip(range(self.TRIALS),self.SEEDS)]
			[p.start() for p in ps]
			print("Processes Started")
			acc_all = [q.get() for i in range(self.TRIALS)]
			print("All Data Retrieved")
			[p.join() for p in ps]
			print("All Proceses Stopped")
			with open(self.save_dir+'/hidden_%s.csv' %hidden, 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_all).T)

	def partA(self):
		# for part A - change hidden units
		for hidden in self.hidden_units:
			acc_hidden = []
			for t in range(self.TRIALS):
				nn = NN(self.data.data[0], self.data.y[0], hidden=hidden)
				acc = nn.epochs_train(self.EPOCH, self.data.data, self.data.y, self.test_datas[0].data, self.test_datas[0].y)
				acc_hidden.append(copy.deepcopy(acc))
			with open(self.save_dir+'/hidden_%s.csv' %hidden, 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_hidden).T)

	def partB_multiP(self):
		# runs with multiple threads
		for epoch in self.epochs:
			q = Queue()
			ps = [Process(target = self.NN_multi, args=(self.HIDDEN, epoch, self.LEARNING_RATE, seed, self.data.data, self.data.y, self.test_datas[0].data, self.test_datas[0].y, q)) for i,seed in zip(range(self.TRIALS),self.SEEDS)]
			[p.start() for p in ps]
			print("Processes Started")
			acc_all = [q.get() for i in range(self.TRIALS)]
			print("All Data Retrieved")
			[p.join() for p in ps]
			print("All Proceses Stopped")
			with open(self.save_dir+'/epoch_%s.csv' %epoch, 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_all).T)

	def partB(self):
		# for part B - change training time (epochs)
		for epoch in self.epochs:
			acc_hidden = []
			for t in range(self.TRIALS):
				nn = NN(self.data.data[0], self.data.y[0], hidden=20)
				acc = nn.epochs_train(epoch, self.data.data, self.data.y, self.test_datas[0].data, self.test_datas[0].y)
				acc_hidden.append(copy.deepcopy(acc))
			with open(self.save_dir+'/epoch_%s.csv' %epoch, 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_hidden).T)

	def partC_multiP(self):
		# runs with multiple threads
		for learning_rate in self.learning_rates:
			q = Queue()
			ps = [Process(target = self.NN_multi, args=(self.HIDDEN, self.EPOCH, learning_rate, seed, self.data.data, self.data.y, self.test_datas[0].data, self.test_datas[0].y, q)) for i,seed in zip(range(self.TRIALS),self.SEEDS)]
			[p.start() for p in ps]
			print("Processes Started")
			acc_all = [q.get() for i in range(self.TRIALS)]
			print("All Data Retrieved")
			[p.join() for p in ps]
			print("All Proceses Stopped")
			with open(self.save_dir+'/learningrate_%s.csv' %learning_rate, 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_all).T)

	def partC(self):
		# for part C - change learning rate
		for learning_rate in self.learning_rates:
			acc_hidden = []
			for t in range(self.TRIALS):
				nn = NN(self.data.data[0], self.data.y[0], hidden=20, learning_rate = learning_rate)
				acc = nn.epochs_train(self.EPOCH, self.data.data, self.data.y, self.test_datas[0].data, self.test_datas[0].y)
				acc_hidden.append(copy.deepcopy(acc))
			with open(self.save_dir+'/learningrate_%s.csv' %learning_rate, 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_hidden).T)

	def partD_multiP(self):
		# initialization of values
		for w in self.weights_range:
			q = Queue()
			ps = [Process(target = self.NN_multi, args=(self.HIDDEN, self.EPOCH, self.LEARNING_RATE, seed, self.data.data, self.data.y, self.test_datas[0].data, self.test_datas[0].y, q, w)) for i,seed in zip(range(self.TRIALS),self.SEEDS)]
			[p.start() for p in ps]
			print("Processes Started")
			acc_all = [q.get() for i in range(self.TRIALS)]
			print("All Data Retrieved")
			[p.join() for p in ps]
			print("All Proceses Stopped")
			with open(self.save_dir+'/weights_%s.csv' %(w), 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_all).T)

	def partE_multiP(self):
		# runs with multiple threads
		for i_t,test in enumerate(self.test_datas):
			q = Queue()
			ps = [Process(target = self.NN_multi, args=(self.HIDDEN, self.EPOCH, self.LEARNING_RATE, seed, self.data.data, self.data.y, test.data, test.y, q)) for i,seed in zip(range(self.TRIALS),self.SEEDS)]
			[p.start() for p in ps]
			print("Processes Started")
			acc_all = [q.get() for i in range(self.TRIALS)]
			print("All Data Retrieved")
			[p.join() for p in ps]
			print("All Proceses Stopped")
			with open(self.save_dir+'/testset_%s.csv' %(i_t+1), 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_all).T)

	def partE(self):
		# for part E - performance of different data sets
		for i_t,test in enumerate(self.test_datas):
			acc_hidden = []
			for t in range(self.TRIALS):
				nn = NN(self.data.data[0], self.data.y[0], hidden=20)
				acc = nn.epochs_train(self.EPOCH, self.data.data, self.data.y, test.data, test.y)
				acc_hidden.append(copy.deepcopy(acc))
			with open(self.save_dir+'/testset_%s.csv' %(i_t+1), 'wb') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerows(np.array(acc_hidden).T)


	def plotData(self, save_dir):
		self.save_dir = save_dir
		self.plotA()
		self.plotB()
		self.plotC()
		self.plotE()

	def plotA(self):
		fns = [self.save_dir+'/hidden_%s.csv' %h for h in self.hidden_units]
		plt.figure()
		plt.title('Effect of Change in Number of Hidden Units')
		for fn,m,h in zip(fns,self.markers,self.hidden_units):
			mean  = []
			stdev = []
			with open(fn, 'rb') as csvfile:
				reader = csv.reader(csvfile)
				for row in reader:
					mean.append(np.mean(np.array(row).astype(float)))
					stdev.append(np.std(np.array(row).astype(float)))
			# plot_pts_freq = 20
			# plot_mean = mean[::plot_pts_freq]
			# plot_stdev = stdev[::plot_pts_freq]
			# plt.errorbar(range(0,len(mean),plot_pts_freq), plot_mean, yerr=plot_stdev,label=h,fmt=m[-1])
			plot_first_pts = 30
			plt.errorbar(range(0,plot_first_pts), mean[:plot_first_pts], yerr=stdev[:plot_first_pts],label=h,fmt='--'+m[-1])

		plt.legend()
		plt.xlabel('Epochs')
		plt.ylabel('Accuracy')
		plt.savefig(self.save_dir+'/hidden_units.png')
		plt.close()

	def plotB(self):
		fns = [self.save_dir+'/epoch_%s.csv' %h for h in self.epochs]
		plt.figure()
		plt.title('Effect of Change in Training Time')
		for fn,m,e in zip(fns,self.markers,self.epochs):
			mean  = []
			stdev = []
			with open(fn, 'rb') as csvfile:
				reader = csv.reader(csvfile)
				for row in reader:
					mean.append(np.mean(np.array(row).astype(float)))
					stdev.append(np.std(np.array(row).astype(float)))
			pts = 25
			plot_pts = np.linspace(0, len(mean)-1, pts).astype(int)
			plot_pts = np.unique(np.logspace(0, np.log10(len(mean)-1), pts).astype(int))
			plot_mean = [mean[i] for i in plot_pts]
			plot_stdev = [stdev[i] for i in plot_pts]
			plt.errorbar(plot_pts, plot_mean, yerr=plot_stdev,label=e,fmt='--'+m[-1])
		plt.legend()
		plt.xlabel('Epochs')
		plt.ylabel('Accuracy')
		plt.gca().set_xscale("log", nonposx='clip')
		plt.savefig(self.save_dir+'/epochs.png')
		plt.close()

	def plotC(self):
		fns = [self.save_dir+'/learningrate_%s.csv' %h for h in self.learning_rates]
		plt.figure()
		plt.title('Effect of Change in Learning Rate')
		for fn,m,lr in zip(fns,self.markers,self.learning_rates):
			mean  = []
			stdev = []
			with open(fn, 'rb') as csvfile:
				reader = csv.reader(csvfile)
				for row in reader:
					mean.append(np.mean(np.array(row).astype(float)))
					stdev.append(np.std(np.array(row).astype(float)))
			plot_first_pts = 15
			plt.errorbar(range(0,plot_first_pts), mean[:plot_first_pts], yerr=stdev[:plot_first_pts],label=lr,fmt='--'+m[-1])
		plt.legend()
		plt.xlabel('Epochs')
		plt.ylabel('Accuracy')
		plt.savefig(self.save_dir+'/learning_rate.png')
		plt.close()

	def plotD(self):
		fns = [self.save_dir+'/weights_%s.csv' %h for h in self.weights_range]
		plt.figure()
		plt.title('Effect of Change in Weight Initialization')
		for fn,m,w in zip(fns,self.markers,self.weights_range):
			mean  = []
			stdev = []
			with open(fn, 'rb') as csvfile:
				reader = csv.reader(csvfile)
				for row in reader:
					mean.append(np.mean(np.array(row).astype(float)))
					stdev.append(np.std(np.array(row).astype(float)))
			plot_first_pts = 15
			plt.errorbar(range(0,plot_first_pts), mean[:plot_first_pts], yerr=stdev[:plot_first_pts],label=w,fmt='--'+m[-1])
		plt.legend()
		plt.xlabel('Epochs')
		plt.ylabel('Accuracy')
		plt.savefig(self.save_dir+'/weights.png')
		plt.close()

	def plotE(self):
		fns = [self.save_dir+'/testset_%s.csv' %h for h in range(1,4)]
		plt.figure()
		plt.title('Accuracy Over Different Training Sets')
		for fn,m,d in zip(fns,self.markers,range(1,4)):
			mean  = []
			stdev = []
			with open(fn, 'rb') as csvfile:
				reader = csv.reader(csvfile)
				for row in reader:
					mean.append(np.mean(np.array(row).astype(float)))
					stdev.append(np.std(np.array(row).astype(float)))
			plot_pts = np.arange(0,100,5)
			plot_mean = [mean[i] for i in plot_pts]
			plot_stdev = [stdev[i] for i in plot_pts]
			plt.errorbar(plot_pts, plot_mean, yerr=plot_stdev,label=d,fmt='--'+m[-1])
		plt.legend()
		plt.xlabel('Epochs')
		plt.ylabel('Accuracy')
		plt.savefig(self.save_dir+'/data_sets.png')
		plt.close()
			

if __name__ == '__main__':
	mp1 = makePlots(fn='train1.csv')
	mp2 = makePlots(fn='train2.csv')
	# mp1.recordData('train1')
	# mp2.recordData('train2')
	# mp1.plotData('train1')
	# mp2.plotData('train2')
	mp1.save_dir = 'train1'
	# mp1.partA_multiP()
	# mp1.partB_multiP()
	# mp1.partC_multiP()
	# mp1.partD_multiP()
	# mp1.partE_multiP()
	mp2.save_dir = 'train2'
	# mp2.partA_multiP()
	# mp2.partB_multiP()
	# mp2.partC_multiP()
	# mp2.partD_multiP()
	# mp2.partE_multiP()
	
	mp1.plotA()
	mp1.plotB()
	mp1.plotC()
	mp1.plotD()
	mp1.plotE()

	mp2.plotA()
	mp2.plotB()
	mp2.plotC()
	mp2.plotD()
	mp2.plotE()



	'''
	# data = AND_data(100)
	# data = XOR_data(100)
	data = load_data('train1.csv')
	test_data = load_data('test1.csv')
	# data.print_data()
	nn = NN(data.data[0], data.y[0])
	# nn.forward(data.data[0])
	# nn.backward(data.data[0], data.y[0])
	for i in range(1):
		nn = NN(data.data[0], data.y[0])
		nn.epochs_train(1000, data.data, data.y, test_data.data, test_data.y)
		'''