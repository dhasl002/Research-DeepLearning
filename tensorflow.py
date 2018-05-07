import tensorflow as tf
import numpy as np
from tensorflow.python import debug as tf_debug
from tf_model import model
from tensorflow.python import debug as tf_debug
sess = tf.InteractiveSession()


def printEpoch(curEpoch):
  print('epoch Number: ' + str(curEpoch))
  fStat.write('epoch Number: ' + str(curEpoch) + '\n')

def printBatchStats(train_accuracy, CurCross):
  fStat.write('training accuracy %g' % (train_accuracy))
  fStat.write('\n')
  fStat.write('Loss %g' % (CurCross))
  fStat.write('\n')
  print('training accuracy %g' % (train_accuracy))
  print('Loss %g' % (CurCross))

def train(trainingListLocation, batch_Size):
  #open list that contains information about training (protein name and number of files)
  with open(trainingListLocation) as trainingList:
    next(trainingList)
	#extract protein name and number of files
    for newLine in trainingList:
      proteinName, numFiles = newLine.strip().split(",")
      path = "/home/dhaslam/New_test_samples2/RotatedSet/" + proteinName + "/" + proteinName + "-"
      trainProtein(path, numFiles, batch_Size)

def trainProtein(path, numFiles, batch_Size):
  for currFileNum in range(0, int(numFiles)):
    it = 0
    if (int(currFileNum)%batch_Size == 0):
      a = np.zeros((batch_Size,N,P,M,3),dtype = float)
      b = np.zeros((batch_Size,N*M*P,3), dtype = float)
    with open(path + str(currFileNum) + ".txt") as inf:
      for line in inf:
        xCoord, yCoord, zCoord, thresh, label = line.strip().split(",")
        xCoord = int(xCoord)
        yCoord = int(yCoord)
        zCoord = int(zCoord)
        thresh = float(thresh)
        label = int(label)	
        a[int(currFileNum)%batch_Size][int(it/(32*7))][int(it/32)%7][int(it%32)][0] = thresh
        a[int(currFileNum)%batch_Size][int(it/(32*7))][int(it/32)%7][int(it%32)][1] = thresh	
        a[int(currFileNum)%batch_Size][int(it/(32*7))][int(it/32)%7][int(it%32)][2] = thresh  
        b[int(currFileNum)%batch_Size][it][label] = 1
        it = it + 1		  
    if(int(currFileNum)%batch_Size == (batch_Size)-1):
      runTrainingBatch(a, b)

def runTrainingBatch(a, b):
  keep_prob = tf.placeholder(tf.float32)
  CurCross = cross_entropy.eval(feed_dict={x_image: a, y_: b})
  train_accuracy = accuracy.eval(feed_dict={x_image: a, y_: b, keep_prob: .5})
  train_step.run(feed_dict={x_image: a, y_: b, keep_prob: .5})
  temp = sess.run(modelResult, feed_dict={x_image: a})
  f5 = open("/home/dhaslam/New_test_samples2/RotatedSet/labels/results3.txt","w+")  
  for i in range(0, 7167):
    if(temp[i][0] > temp[i][1] and temp[i][0] > temp[i][2]):
      f5.write(str(int(i/(32*7))) + " " + str(int(i/7)%32) + " " + str(int(i%7)) + " 0\r\n")
    if(temp[i][1] > temp[i][0] and temp[i][1] > temp[i][2]):
      f5.write(str(int(i/(32*7))) + " " + str(int(i/7)%32) + " " + str(int(i%7)) + " 1\r\n")
    if(temp[i][2] > temp[i][0] and temp[i][2] > temp[i][1]):
      f5.write(str(int(i/(32*7))) + " " + str(int(i/7)%32) + " " + str(int(i%7)) + " 2\r\n")
  f5.close()
  printBatchStats(train_accuracy, CurCross)

def getMRCDimensions(fileToOpen):
  xMin = 100000000
  xMax = -1
  yMin = 100000000
  yMax = -1
  zMin = 100000000
  zMax = -1
  with open(fileToOpen) as inf3:
    for line4 in inf3:
      xCoord, yCoord, zCoord, thresh, label = line4.strip().split(",")
      xCoord = int(xCoord)
      yCoord = int(yCoord)
      zCoord = int(zCoord)
      if xCoord < xMin:
        xMin = xCoord
      if yCoord < yMin:
        yMin = yCoord
      if zCoord < zMin:
        zMin = zCoord
      if xCoord > xMax:
        xMax = xCoord
      if yCoord > yMax:
        yMax = yCoord
      if zCoord > zMax:
        zMax = zCoord
  return xMax, xMin, yMax, yMin, zMax, zMin

def test(batch_Size):
  keep_prob = tf.placeholder(tf.float32)
  xMax, xMin, yMax, yMin, zMax, zMin = getMRCDimensions(path2)
  xLength = xMax-xMin+1
  yLength = yMax-yMin+1
  zLength = zMax-zMin+1
  numLines = (xLength)*(yLength)*(zLength)
  with open(path2) as inf2:
    a = np.zeros((1,xLength, yLength, zLength, 3),dtype = float)
    b = np.zeros((1,numLines, 3), dtype = float)
    axisZ = np.zeros((1,numLines),dtype = float)
    axisY = np.zeros((1,numLines),dtype = float)
    axisX = np.zeros((1,numLines),dtype = float)
    for x in range(0, xLength):
      for y in range(0, yLength):
        for z in range(0, zLength):
          curPos = (x)*yLength*zLength+(y)*zLength+(z)
          axisX[0][curPos] = x+xMin
          axisY[0][curPos] = y+yMin
          axisZ[0][curPos] = z+zMin
    next(inf2)
    for line3 in inf2:
      xCoord, yCoord, zCoord, thresh, label = line3.strip().split(",")
      xCoord = int(xCoord)
      yCoord = int(yCoord)
      zCoord = int(zCoord) 
      thresh = float(thresh)
      label = int(label)
      curPos = (xCoord-xMin)*yLength*zLength+(yCoord-yMin)*zLength+(zCoord-zMin)
      #print(curPos)
      #print(str(xCoord-xMin) + " " + str(yCoord-yMin) + " " + str(zCoord-zMin))
      a[0][xCoord-xMin][yCoord-yMin][zCoord-zMin][0]  = thresh
      a[0][xCoord-xMin][yCoord-yMin][zCoord-zMin][1]  = thresh
      a[0][xCoord-xMin][yCoord-yMin][zCoord-zMin][2]  = thresh
      b[0][curPos][label] = 1
  print(sess.run(accuracy, feed_dict={x_image: a, y_: b, keep_prob: 1.0}))
  predictedLabels = sess.run(tf.argmax(modelResult,1), feed_dict={x_image: a})
  writePredictionsToFile(predictedLabels, numLines, axisX, axisY, axisZ, b)

def writePredictionsToFile(predictedLabels, numLines, axisX, axisY, axisZ, b):
  f1 = open(tempPath,"w+")
  for i in range(0, numLines):
    f1.write(str(int(axisX[0][i])) + " " + str(int(axisY[0][i])) + " " + str(int(axisZ[0][i])) + " " + str(predictedLabels[i]) + "\r\n")


N = 32 #x dimension of training patch size
M = 32 #y dimension of training patch size
P = 7 #z dimension of training patch size
batch_Size = 30
epochs = 10000
outputStats = "/home/dhaslam/New_test_samples2/RotatedSet/labels/Statistics.txt"
trainingListLocation = "/home/dhaslam/New_test_samples2/RotatedSet/list.txt"
path2 = "/home/dhaslam/New_test_samples2/RotatedSet/4XDA/4XDA_label.txt"
tempPath = "/home/dhaslam/New_test_samples2/RotatedSet/labels/results.txt"
f5 = open("/home/dhaslam/New_test_samples2/RotatedSet/labels/results3.txt","w+")  

x_image = tf.placeholder(tf.float32, shape=[None, None, None, None, 3])
y_ = tf.placeholder(tf.float32, shape=[None, None, 3])

modelResult = model(x_image) #sets modelResults to the final result of the model 

#train model
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=modelResult, labels=y_))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(modelResult, 1), tf.argmax(tf.reshape(y_, [-1, 3]), 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

#run
with tf.Session() as sess:
   fStat = open(outputStats,"w+")
   sess.run(tf.global_variables_initializer())
   #sess = tf_debug.LocalCLIDebugWrapperSession(sess)
   for curEpoch in range(1, epochs):
     printEpoch(curEpoch) 
     train(trainingListLocation, batch_Size)
     test(batch_Size)
   fStat.close()
