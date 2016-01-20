import utilities
from sklearn import svm,cross_validation
from sklearn.svm import SVC
from sklearn.feature_selection import RFECV
from sklearn.svm import LinearSVC
import pandas
from sklearn.cross_validation import train_test_split
from sklearn.metrics import accuracy_score,confusion_matrix,f1_score,precision_recall_curve,classification_report
import matplotlib.pyplot as plt


class ML_classifiers:

    config = utilities.getConfigs()
    target = config.get('target')

    def featureSelction(self,frame):
        est = SVC(kernel = "linear")
        selector = RFECV(estimator=est,step=2,scoring='accuracy')
        train = frame.drop(self.target,1)
        selector = selector.fit(train, frame[self.target])
        print(selector.n_features_)
        print(selector.ranking_)
        print sorted(zip(map(lambda x: round(x, 4), selector.ranking_), train.columns))
        #X_train_reduced = selector.transform(frame)
        #X_test_reduced = feature_selector.transform(X_test)

        plt.figure()
        plt.xlabel("Number of features selected")
        plt.ylabel("Cross validation score (nb of correct classifications)")
        plt.plot(range(1, len(selector.grid_scores_) + 1), selector.grid_scores_)
        plt.show()
        return selector


    #This will be the SVM classifier where we have the option to split the input frame to training and test set and specify the %split
    # if have seperate test set then just pass it ti frame_totest
    # its returns the clasifier and prints out the various performance evaluations
    # need to add cross validation

    def SVMclassifier(self,frame,frame_totest,split = True,percent = 0.8,C = 3.0, gamma = 'auto', kernel = 'linear'):
        #Also to try :sklearn.svm.LinearSVC and sklearn.svm.SVR
        #classifier = SVC(C =C, gamma = gamma, kernel = kernel)
        classifier = LinearSVC()

        training_set = frame
        testing_set = frame_totest
        if split == True:
            training_set = frame.sample(frac=percent, random_state=1)
            testing_set = frame.loc[~frame.index.isin(training_set.index)]

        classifier.fit(training_set,training_set[self.target])
        #cross_validation.cross_val_score(classifier,training_set,training_set[self.config.get['target']],scoring = 'f1')
        predictions_training = classifier.predict(training_set)
        training_set['Predictions'] = predictions_training
        #training_set.join(predictions_training,'Predictions')
        training_true = training_set[self.target]
        predictions_testing = classifier.predict(testing_set)
        testing_set['Predictions'] =  predictions_testing
        #testing_set.join(predictions_testing,'Predictions')
        testing_true = testing_set[self.target]


        accuracy_training = accuracy_score(training_true, predictions_training)
        accuracy_testing = accuracy_score(testing_true, predictions_testing)

        confusionmatrix_training = confusion_matrix(training_true, predictions_training)
        confusionmatrix_testing = confusion_matrix(testing_true, predictions_testing)


        f1_training = f1_score(training_true, predictions_training,average='macro')
        f1_training = f1_score(training_true, predictions_training, average='micro')
        f1_training = f1_score(training_true, predictions_training, average='weighted')
        f1_testing = f1_score(testing_true, predictions_testing,average='macro')
        f1_testing = f1_score(testing_true, predictions_testing, average='micro')
        f1_testing = f1_score(testing_true, predictions_testing, average='weighted')


       # precision, recall, thresholds = precision_recall_curve(training_true, predictions_training)

        report_training = classification_report(training_true, predictions_training)
        report_testing = classification_report(testing_true, predictions_testing)



        return accuracy_testing