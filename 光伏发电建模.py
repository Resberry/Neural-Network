import numpy as np
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn import ensemble
from sklearn.tree import ExtraTreeRegressor
from sklearn import neighbors
import matplotlib.pyplot as plt
import xlwt
import csv

from sklearn import neighbors
from sklearn import ensemble
from sklearn import tree

def compute_error(real,predict,no,day):
	P_dic={1:10,2:10,3:40,4:50}
	day_sum=0.
	day_list=[]
	n=0
	time=0
	if no>2:
		for i,data in enumerate(real):
			if data>=P_dic[no]*0.03:
				day_sum+=abs(real[i]-predict[i])
				n+=1
			if i==len(real)-1 or day[i+1]!=day[i]:
				if n==0:
					day_list.append(0)
				else:
					day_list.append(day_sum/P_dic[no]/n)
				n=0
				day_sum=0
	else:
		for i,data in enumerate(real):
			if data>=P_dic[no]*0.03:
				day_sum+=abs(real[i]-predict[i])
				n+=1
			time+=1
			if time==96:
				if n==0:
					day_list.append(0)
				else:
					day_list.append(day_sum/P_dic[no]/n)
				n=0
				time=0
				day_sum=0
	if no==1:
		month1=sum(day_list[:31])/31
		month2=sum(day_list[31:61])/30
		month3=sum(day_list[61:92])/31	
		month4=sum(day_list[92:])/31
		month=[month1,month2,month3,month4]
		error=sum(month)/4
	elif no==2:
		month1=sum(day_list[:31])/31
		month2=sum(day_list[31:61])/30
		month3=sum(day_list[61:92])/31	
		month4=sum(day_list[92:123])/31
		month5=sum(day_list[123:])/30
		month=[month1,month2,month3,month4,month5]
		error=sum(month)/5
	elif no==3:
		month1=sum(day_list[:31])/31
		month2=sum(day_list[31:58])/26
		month3=sum(day_list[58:])/8
		month=[month1,month2,month3]
		error=sum(month)/3
	else:
		month1=sum(day_list[:29])/28
		month2=sum(day_list[29:59])/29
		month3=sum(day_list[59:90])/31	
		month4=sum(day_list[90:121])/31
		month5=sum(day_list[121:150])/27
		#month6=sum(day_list[150:])/1
		#month=[month1,month2,month3,month4,month5,month6]
		#error=sum(month)/6
		month=[month1,month2,month3,month4,month5]
		error=sum(month)/5
	return day_list,error
#训练集=[0时间,1辐照度,2风速,3风向,4温度,5压强,6湿度,7实发辐照度,8实际功率]
#测试集=[0时间,1辐照度,2风速,3风向,4温度,5压强,6湿度,7实际功率,8实发辐照度]


class photovoltaic():
	def __init__(self,file_num,file_tag='',index=[7,8,7,8]):
		self.file_num=file_num
		self.file_tag=file_tag
		self.index=index
		self.open_data()
	def open_data(self):
		train_data=[]
		test_data=[]
		train_path='电站'+str(self.file_num)+'train'+str(self.file_tag)+'.csv'
		test_path='电站'+str(self.file_num)+'test'+'.csv'
		with open(train_path,"r") as csvfile:
			csv_reader = csv.reader(csvfile)
			for row in csv_reader:
				train_data.append(row)
		with open(test_path,"r") as csvfile:
			csv_reader = csv.reader(csvfile)
			for row in csv_reader:
				test_data.append(row)
		train_data=np.array(train_data)
		test_data=np.array(test_data)
		x_train=train_data[1:,1:self.index[0]]
		y_train=train_data[1:,self.index[1]]
		x_test=test_data[1:,1:self.index[2]]
		y_test=test_data[1:,self.index[3]]
		self.x_train=x_train.astype('float')
		self.y_train=y_train.astype('float')
		self.x_test=x_test.astype('float')
		self.y_test=y_test.astype('float')
		day=[i[:9].split('/')[2] for i in list(test_data[1:,0])]
		self.day=day
	def add_time(self):
		train_time=np.array([int(i[-5:-3])*4+int(i[-2:])/15 for i in list(train_data[1:,0])]).reshape(-1,1)
		test_time=np.array([int(i[-5:-3])*4+int(i[-2:])/15 for i in list(test_data[1:,0])]).reshape(-1,1)
		self.x_train=np.c_[train_time,self.x_train]
		self.x_test=np.c_[test_time,self.x_test]	
	def add_feature(self):
		f1=4
		f2=5
		train_ws=np.array([self.x_train[i,3]*self.x_train[i,4] for i in range(len(self.x_train))]).reshape(-1,1)
		test_ws=np.array([self.x_test[i,3]*self.x_test[i,4] for i in range(len(self.x_test))]).reshape(-1,1)
		train_ws2=np.array([self.x_train[i,3]*self.x_train[i,5] for i in range(len(self.x_train))]).reshape(-1,1)
		test_ws2=np.array([self.x_test[i,3]*self.x_test[i,5] for i in range(len(self.x_test))]).reshape(-1,1)
		train_ws3=np.array([self.x_train[i,4]*self.x_train[i,5] for i in range(len(self.x_train))]).reshape(-1,1)
		test_ws3=np.array([self.x_test[i,4]*self.x_test[i,5] for i in range(len(self.x_test))]).reshape(-1,1)
		self.x_train=np.c_[self.x_train,train_ws,train_ws2,train_ws3]
		self.x_test=np.c_[self.x_test,test_ws,test_ws2,test_ws3]
		
		




	
		
	def model_train(self,model_tag):
		if model_tag=='svr':
			regr=SVR(kernel='rbf',gamma=0.0001)
		elif model_tag=='linear':
			regr=linear_model.LinearRegression()
		elif model_tag=='poly':
			poly_reg=PolynomialFeatures(degree=3)
			self.x_train=poly_reg.fit_transform(self.x_train)
			self.x_test=poly_reg.fit_transform(self.x_test)
			regr=Ridge(alpha=100)
		elif model_tag=='ridge':
			regr=Ridge(alpha=310)
		elif model_tag=='k':
			regr=ensemble.RandomForestRegressor(n_estimators=100)
		regr.fit(self.x_train,self.y_train)
		self.y_predict=regr.predict(self.x_test)
		if model_tag=='linear':
			self.coef=regr.coef_
			self.intercept=regr.intercept_
			print(self.coef)
			print(self.intercept)

		D,S=compute_error(self.y_test,self.y_predict,self.file_num,self.day)		
		print(D,S)
		#print([i+1 for i in range(len(D)) if D[i]>=0.2])
	def model_ensemble(self,model_tag=None):
		regr=SVR(kernel='rbf',gamma=0.004)
		regr.fit(self.x_train,self.y_train)
		self.y_predict1=regr.predict(self.x_test)
		regr=linear_model.LinearRegression()
		regr.fit(self.x_train,self.y_train)
		self.y_predict2=regr.predict(self.x_test)
		
		D,S=compute_error(self.y_test,(self.y_predict1+self.y_predict2)/2,self.file_num,self.day)		
		print(D,S)
	def coef_back(self):
		self.coef=[4.945,1.2e-01,-9.1e-04,0.6e-01,3.4e-01,3.1e-01]
		self.intercept=4.55
		s=0
		y_compute=[]
		for i in range(len(self.x_test)):
			for j in range(len(self.coef)):
				s+=self.coef[j]*self.x_test[i,j]
			s+=self.intercept
			y_compute.append(s)
			s=0


		D,S=compute_error(self.y_test,y_compute,self.file_num,self.day)		
		print(D,S)


	def save_data(self):
		workbook=xlwt.Workbook(encoding='utf-8')
		worksheet=workbook.add_sheet('sheet1')
		for i in range(len(self.y_predict)):
			if self.y_test[i]>=0.3:
				worksheet.write(i,0,self.y_predict[i]-self.y_test[i])

		workbook.save('compare3.xls')
#for i in range(len(y_test)):
#	worksheet.write(i,0,list(y_test)[i])
#	worksheet.write(i,1,list(y_tree)[i])
#	worksheet.write(i,2,list(y_predict)[i])
#	worksheet.write(i,3,list(y_predict2)[i])

energy=photovoltaic(1)
energy.add_feature()

energy.model_train('linear') 
#energy.coef_back()
#energy.save_data()
#energy.model_ensemble()
