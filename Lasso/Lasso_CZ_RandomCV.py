# -*- coding: utf-8 -*-

import os
import scipy.io as sio
import numpy as np
import time
from sklearn import linear_model
from sklearn import preprocessing
from joblib import Parallel, delayed
  
def Lasso_KFold_RandomCV_AllSubsets(Subjects_Data_Mat_Path, Subjects_Score, SampleInfo, Fold_Quantity, CVRepeatTimes, Alpha_Range, ResultantFolder, Max_Queued, QueueOptions, Parallel_Quantity):
    
    Finish_File = []
    Times_IDRange_Todo_Size = np.int64(np.array([]))
    Times_IDRange_Todo_Size_ResampleIndex = np.int64(np.array([]))
    SampleSize_Array_Length = len(SampleInfo)
    SampleSize_Array = np.arange(SampleSize_Array_Length)
    for i in np.arange(SampleSize_Array_Length):
        SampleSize_Array[i] = SampleInfo[i][0][0][0]
    Times_SampleResample = len(SampleInfo[0][1][0])
    for i in np.arange(len(SampleSize_Array)):
        print(i)
        ResultantFolder_I = os.path.join(ResultantFolder, 'SampleSize_' + str(SampleSize_Array[i]))
        if not os.path.exists(ResultantFolder_I):
            os.mkdir(ResultantFolder_I)
        for j in np.arange(Times_SampleResample):
            if not os.path.exists(ResultantFolder_I + '/Prediction_' + str(j) + '.mat'):
                Selected_IDs = SampleInfo[i][1][0][j][0] - 1 # -1 because of difference of Maltab and Python
                Times_IDRange_Todo_Size = np.insert(Times_IDRange_Todo_Size, len(Times_IDRange_Todo_Size), i)
                Times_IDRange_Todo_Size_ResampleIndex = np.insert(Times_IDRange_Todo_Size_ResampleIndex, len(Times_IDRange_Todo_Size_ResampleIndex), j)
                Configuration_Mat = {'Subjects_Data_Mat_Path': Subjects_Data_Mat_Path, 'Subjects_Score': Subjects_Score, 'SampleSize': SampleSize_Array[i], \
                    'Fold_Quantity': Fold_Quantity, 'CVRepeatTimes': CVRepeatTimes, 'Sample_Index': j, 'Selected_IDs': Selected_IDs, 'Alpha_Range': Alpha_Range, 'ResultantFolder_I': ResultantFolder_I, 'Parallel_Quantity': Parallel_Quantity};
                sio.savemat(ResultantFolder_I + '/Configuration_' + str(j) + '.mat', Configuration_Mat)
                system_cmd = 'python3 -c ' + '\'import sys;\
                    sys.path.append("/lustre/gaolab/cuizaixu/Utilities_Zaixu/Utilities_Regression/Lasso");\
                    from Lasso_CZ_RandomCV import Lasso_KFold_RandomCV_OneSubset;\
                    import os;\
                    import scipy.io as sio;\
                    configuration = sio.loadmat("' + ResultantFolder_I + '/Configuration_' + str(j) + '.mat");\
                    Subjects_Data_Mat_Path = configuration["Subjects_Data_Mat_Path"];\
                    Subjects_Score = configuration["Subjects_Score"];\
                    SampleSize = configuration["SampleSize"];\
                    Sample_Index = configuration["Sample_Index"];\
                    Selected_IDs = configuration["Selected_IDs"];\
                    Fold_Quantity = configuration["Fold_Quantity"];\
                    CVRepeatTimes = configuration["CVRepeatTimes"];\
                    Alpha_Range = configuration["Alpha_Range"];\
                    ResultantFolder_I = configuration["ResultantFolder_I"];\
                    Parallel_Quantity = configuration["Parallel_Quantity"];\
                    Lasso_KFold_RandomCV_OneSubset(Subjects_Data_Mat_Path[0], Subjects_Score[0], Selected_IDs[0], Sample_Index[0][0], Fold_Quantity[0][0], CVRepeatTimes[0][0], Alpha_Range[0], ResultantFolder_I[0], Parallel_Quantity[0][0])\' ';
                system_cmd = system_cmd + ' > "' + ResultantFolder_I + '/Lasso_' + str(j) + '.log" 2>&1\n'
                Finish_File.append(ResultantFolder_I + '/Prediction_' + str(j) + '.mat')
                script = open(ResultantFolder_I + '/script_' + str(j) + '.sh', 'w')  
                script.write(system_cmd)
                script.close()
    
    Jobs_Quantity = len(Finish_File)

    if len(Times_IDRange_Todo_Size) > Max_Queued:
        Submit_Quantity = Max_Queued
    else:
        Submit_Quantity = len(Times_IDRange_Todo_Size)
    for i in np.arange(Submit_Quantity):
        ResultantFolder_I = ResultantFolder + '/SampleSize_' + str(SampleSize_Array[Times_IDRange_Todo_Size[i]])
        #Option = ' -V -o "' + ResultantFolder_I + '/prediction_' + str(Times_IDRange_Todo_Size_ResampleIndex[i]) + '.o" -e "' + ResultantFolder_I + '/prediction_' + str(Times_IDRange_Todo_Size_ResampleIndex[i]) + '.e"';
        #os.system('qsub ' + ResultantFolder_I + '/script_' + str(Times_IDRange_Todo_Size_ResampleIndex[i]) +'.sh ' + QueueOptions + ' -N prediction_' + str(Times_IDRange_Todo_Size[i]) + '_' + str(Times_IDRange_Todo_Size_ResampleIndex[i]) + Option)
        os.system('at -f "' + ResultantFolder_I + '/script_' + str(Times_IDRange_Todo_Size_ResampleIndex[i]) +'.sh" now');
    #if len(Times_IDRange_Todo_Size) > Max_Queued:
    Finished_Quantity = 0;
    while 1:
        for i in np.arange(len(Finish_File)):
            if os.path.exists(Finish_File[i]):
                Finished_Quantity = Finished_Quantity + 1
                print(Finish_File[i])            
                del(Finish_File[i])
                print(time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time())))
                print('Finish quantity = ' + str(Finished_Quantity))
                #time.sleep(8)
                if Submit_Quantity < len(Times_IDRange_Todo_Size):
                    ResultantFolder_I = ResultantFolder + '/SampleSize_' + str(SampleSize_Array[Times_IDRange_Todo_Size[Submit_Quantity]])
                    #Option = ' -V -o "' + ResultantFolder_I + '/prediction_' + str(Times_IDRange_Todo_Size_ResampleIndex[Submit_Quantity]) + '.o" -e "' + ResultantFolder_I + '/prediction_' + str(Times_IDRange_Todo_Size_ResampleIndex[Submit_Quantity]) + '.e"';
                    #cmd = 'qsub ' + ResultantFolder_I + '/script_' + str(Times_IDRange_Todo_Size_ResampleIndex[Submit_Quantity]) + '.sh ' + QueueOptions + ' -N prediction_' + str(Times_IDRange_Todo_Size[Submit_Quantity]) + '_' + str(Times_IDRange_Todo_Size_ResampleIndex[Submit_Quantity]) + Option
                    # print(cmd)
                    #os.system(cmd)
                    os.system('at -f "' + ResultantFolder_I + '/script_' + str(Times_IDRange_Todo_Size_ResampleIndex[Submit_Quantity]) + '.sh" now')
                    Submit_Quantity = Submit_Quantity + 1
                break
        if Finished_Quantity >= Jobs_Quantity:
            break
            
def Lasso_KFold_RandomCV_OneSubset(Subjects_Data_Mat_Path, Subjects_Score, SelectedIDs, SampleIndex, Fold_Quantity, CVRepeatTimes, Alpha_Range, ResultantFolder, Parallel_Quantity):
    
    if not os.path.exists(ResultantFolder):
        os.mkdir(ResultantFolder);

    data = sio.loadmat(Subjects_Data_Mat_Path)
    Subjects_Data = data['Subjects_Data']

    Data_Selected = Subjects_Data[SelectedIDs, :]
    Scores_Selected = Subjects_Score[SelectedIDs]
    ResultantFolder_SampleI = ResultantFolder + '/Prediction_' + str(SampleIndex)
    if not os.path.exists(ResultantFolder_SampleI):
        os.mkdir(ResultantFolder_SampleI);

    Corr_MTimes = np.zeros(CVRepeatTimes);
    MAE_MTimes = np.zeros(CVRepeatTimes);
    for i in np.arange(CVRepeatTimes):
        ResultantFolder_SampleI_TimeI = ResultantFolder_SampleI + '/Time_' + str(i)
        Corr_I, MAE_I = Lasso_KFold_RandomCV(Data_Selected, Scores_Selected, Fold_Quantity, Alpha_Range, CVRepeatTimes, ResultantFolder_SampleI_TimeI, Parallel_Quantity)
        Corr_MTimes[i] = Corr_I
        MAE_MTimes[i] = MAE_I
    Mean_Corr = np.mean(Corr_MTimes);
    Mean_MAE = np.mean(MAE_MTimes);
    
    Res = {'SelectedIDs':SelectedIDs, 'Mean_Corr':Mean_Corr, 'Mean_MAE':Mean_MAE, 'Corr_MTimes':Corr_MTimes, 'MAE_MTimes':MAE_MTimes}
    Res_FileName = 'Prediction_' + str(SampleIndex) + '.mat'
    ResultantFile = os.path.join(ResultantFolder, Res_FileName)
    sio.savemat(ResultantFile, Res)

def Lasso_KFold_RandomCV(Subjects_Data, Subjects_Score, Fold_Quantity, Alpha_Range, CVRepeatTimes_ForInner, ResultantFolder, Parallel_Quantity):

    if not os.path.exists(ResultantFolder):
        os.mkdir(ResultantFolder)

    Subjects_Quantity = len(Subjects_Score)
    EachFold_Size = np.int(np.fix(np.divide(Subjects_Quantity, Fold_Quantity)))
    Remain = np.mod(Subjects_Quantity, Fold_Quantity)
    RandIndex = np.arange(Subjects_Quantity)
    np.random.shuffle(RandIndex)
    
    Fold_Corr = [];
    Fold_MAE = [];
    Fold_Weight = [];

    for j in np.arange(Fold_Quantity):

        Fold_J_Index = RandIndex[EachFold_Size * j + np.arange(EachFold_Size)]   
        if Remain > j:
            Fold_J_Index = np.insert(Fold_J_Index, len(Fold_J_Index), RandIndex[EachFold_Size * Fold_Quantity + j])

        Subjects_Data_test = Subjects_Data[Fold_J_Index, :]
        Subjects_Score_test = Subjects_Score[Fold_J_Index]
        Subjects_Data_train = np.delete(Subjects_Data, Fold_J_Index, axis=0)
        Subjects_Score_train = np.delete(Subjects_Score, Fold_J_Index) 

        Optimal_Alpha = Lasso_OptimalAlpha_KFold(Subjects_Data_train, Subjects_Score_train, Fold_Quantity, Alpha_Range, CVRepeatTimes_ForInner, ResultantFolder, Parallel_Quantity)

        normalize = preprocessing.MinMaxScaler()
        Subjects_Data_train = normalize.fit_transform(Subjects_Data_train)
        Subjects_Data_test = normalize.transform(Subjects_Data_test)

        clf = linear_model.Lasso(alpha = Optimal_Alpha)
        clf.fit(Subjects_Data_train, Subjects_Score_train)
        Fold_J_Score = clf.predict(Subjects_Data_test)

        Fold_J_Corr = np.corrcoef(Fold_J_Score, Subjects_Score_test)
        Fold_J_Corr = Fold_J_Corr[0,1]
        Fold_Corr.append(Fold_J_Corr)
        Fold_J_MAE = np.mean(np.abs(np.subtract(Fold_J_Score,Subjects_Score_test)))
        Fold_MAE.append(Fold_J_MAE)
    
        Fold_J_result = {'Index':Fold_J_Index, 'Test_Score':Subjects_Score_test, 'Predict_Score':Fold_J_Score, 'Corr':Fold_J_Corr, 'MAE':Fold_J_MAE}
        Fold_J_FileName = 'Fold_' + str(j) + '_Score.mat'
        ResultantFile = os.path.join(ResultantFolder, Fold_J_FileName)
        sio.savemat(ResultantFile, Fold_J_result)

    Fold_Corr = [0 if np.isnan(x) else x for x in Fold_Corr]
    Mean_Corr = np.mean(Fold_Corr)
    Mean_MAE = np.mean(Fold_MAE)
    Res_NFold = {'Mean_Corr':Mean_Corr, 'Mean_MAE':Mean_MAE};
    ResultantFile = os.path.join(ResultantFolder, 'Res_NFold.mat')
    sio.savemat(ResultantFile, Res_NFold)
    return (Mean_Corr, Mean_MAE)  

def Lasso_OptimalAlpha_KFold(Training_Data, Training_Score, Fold_Quantity, Alpha_Range, CVRepeatTimes, ResultantFolder, Parallel_Quantity):

    if not os.path.exists(ResultantFolder):
        os.mkdir(ResultantFolder);
    
    Subjects_Quantity = len(Training_Score)
    Inner_EachFold_Size = np.int(np.fix(np.divide(Subjects_Quantity, Fold_Quantity)))
    Remain = np.mod(Subjects_Quantity, Fold_Quantity)

    Inner_Corr_Mean = np.zeros((CVRepeatTimes, len(Alpha_Range)))
    Inner_MAE_inv_Mean = np.zeros((CVRepeatTimes, len(Alpha_Range)))
    for i in np.arange(CVRepeatTimes):

        RandIndex = np.arange(Subjects_Quantity)
        np.random.shuffle(RandIndex)
    
        Inner_Corr = np.zeros((Fold_Quantity, len(Alpha_Range)))
        Inner_MAE_inv = np.zeros((Fold_Quantity, len(Alpha_Range)))
        Alpha_Quantity = len(Alpha_Range)

        for k in np.arange(Fold_Quantity):
        
            Inner_Fold_K_Index = RandIndex[Inner_EachFold_Size * k + np.arange(Inner_EachFold_Size)]
            if Remain > k:
                Inner_Fold_K_Index = np.insert(Inner_Fold_K_Index, len(Inner_Fold_K_Index), RandIndex[Inner_EachFold_Size * Fold_Quantity + k])

            Inner_Fold_K_Data_test = Training_Data[Inner_Fold_K_Index, :]
            Inner_Fold_K_Score_test = Training_Score[Inner_Fold_K_Index]
            Inner_Fold_K_Data_train = np.delete(Training_Data, Inner_Fold_K_Index, axis=0)
            Inner_Fold_K_Score_train = np.delete(Training_Score, Inner_Fold_K_Index)
        
            Scale = preprocessing.MinMaxScaler()
            Inner_Fold_K_Data_train = Scale.fit_transform(Inner_Fold_K_Data_train)
            Inner_Fold_K_Data_test = Scale.transform(Inner_Fold_K_Data_test)    
        
            Parallel(n_jobs=Parallel_Quantity,backend="threading")(delayed(Lasso_SubAlpha)(Inner_Fold_K_Data_train, Inner_Fold_K_Score_train, Inner_Fold_K_Data_test, Inner_Fold_K_Score_test, Alpha_Range[l], l, ResultantFolder) for l in np.arange(len(Alpha_Range)))        
        
            for l in np.arange(Alpha_Quantity):
                print(l)
                Fold_l_Mat_Path = ResultantFolder + '/Fold_' + str(l) + '.mat';
                Fold_l_Mat = sio.loadmat(Fold_l_Mat_Path)
                Inner_Corr[k, l] = Fold_l_Mat['Fold_Corr'][0][0]
                Inner_MAE_inv[k, l] = Fold_l_Mat['Fold_MAE_inv']
                os.remove(Fold_l_Mat_Path)
            
            Inner_Corr = np.nan_to_num(Inner_Corr)
        Inner_Corr_Mean[i, :] = np.mean(Inner_Corr, axis=0)
        Inner_MAE_inv_Mean[i, :] = np.mean(Inner_MAE_inv, axis=0)
    Inner_Corr_CVMean = np.mean(Inner_Corr_Mean, axis=0);
    Inner_MAE_inv_CVMean = np.mean(Inner_MAE_inv_Mean, axis=0)
    Inner_Corr_CVMean = (Inner_Corr_CVMean - np.mean(Inner_Corr_CVMean)) / np.std(Inner_Corr_CVMean)
    Inner_MAE_inv_CVMean = (Inner_MAE_inv_CVMean - np.mean(Inner_MAE_inv_CVMean)) / np.std(Inner_MAE_inv_CVMean)
    Inner_Evaluation = Inner_Corr_CVMean + Inner_MAE_inv_CVMean
    
    Inner_Evaluation_Mat = {'Inner_Corr':Inner_Corr, 'Inner_MAE_inv':Inner_MAE_inv, 'Inner_Corr_CVMean':Inner_Corr_CVMean, 'Inner_MAE_inv_CVMean':Inner_MAE_inv_CVMean, 'Inner_Evaluation':Inner_Evaluation}
    sio.savemat(ResultantFolder + '/Inner_Evaluation.mat', Inner_Evaluation_Mat)
    
    Optimal_Alpha_Index = np.argmax(Inner_Evaluation) 
    Optimal_Alpha = Alpha_Range[Optimal_Alpha_Index]
    return (Optimal_Alpha)

def Lasso_SubAlpha(Training_Data, Training_Score, Testing_Data, Testing_Score, Alpha, Alpha_ID, ResultantFolder):
    clf = linear_model.Lasso(alpha=Alpha)
    clf.fit(Training_Data, Training_Score)
    Predict_Score = clf.predict(Testing_Data)
    Fold_Corr = np.corrcoef(Predict_Score, Testing_Score)
    Fold_Corr = Fold_Corr[0,1]
    Fold_MAE_inv = np.divide(1, np.mean(np.abs(Predict_Score - Testing_Score)))
    Fold_result = {'Fold_Corr': Fold_Corr, 'Fold_MAE_inv':Fold_MAE_inv}
    ResultantFile = ResultantFolder + '/Fold_' + str(Alpha_ID) + '.mat'
    sio.savemat(ResultantFile, Fold_result)
    
def Lasso_Weight(Subjects_Data, Subjects_Score, Alpha_Range, Nested_Fold_Quantity, ResultantFolder, Parallel_Quantity):

    if not os.path.exists(ResultantFolder):
        os.mkdir(ResultantFolder)

    # Select optimal alpha using inner fold cross validation
    Optimal_Alpha, Inner_Corr, Inner_MAE_inv = Lasso_OptimalAlpha_KFold(Subjects_Data, Subjects_Score, Nested_Fold_Quantity, Alpha_Range, ResultantFolder, Parallel_Quantity)

    Scale = preprocessing.MinMaxScaler()
    Subjects_Data = Scale.fit_transform(Subjects_Data)
    clf = linear_model.Lasso(alpha=Optimal_Alpha)
    clf.fit(Subjects_Data, Subjects_Score)
    Weight = clf.coef_ / np.sqrt(np.sum(clf.coef_ **2))
    Weight_result = {'w_Brain':Weight, 'alpha':Optimal_Alpha}
    sio.savemat(ResultantFolder + '/w_Brain.mat', Weight_result)
    return;
