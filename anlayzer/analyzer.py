import argparse
import json
import os
import csv

parser = argparse.ArgumentParser(description = 'file type checker')

parser.add_argument('--type', type=str, choices=['test', 'train', 'valid'], required =True, help='filetype; test, train, valid')
args = parser.parse_args()

action_class = ['Standing tackling', 'Tackling', 'High leg', 'Pushing', 'Holding', 'Elbowing', 'Challenge', 'Dive']
offense_class = ['Offence', 'Between', 'No offence']
severity_class = ['0.0', '1.0', '2.0', '3.0', '4.0', '5.0']

pred_path = None;
gt_path = None;
csv_path = f'results/analysis_results_{args.type}.csv'

if args.type == 'test':
    pred_path = 'predictions_test.json'
    gt_path = 'gt_test.json'
elif args.type == 'train':
    pred_path = 'predictions_train.json'
    gt_path = 'gt_train.json'
elif args.type == 'valid':
    pred_path = 'predictions_valid.json'
    gt_path = 'gt_valid.json'

pred_path = os.path.join('data',pred_path)
gt_path = os.path.join('data', gt_path)

for path in [gt_path, pred_path]:
    if not os.path.exists(path):
        raise Exception(f"The path '{path}' does not exist.")

with open(pred_path, 'r') as pred_file, open(gt_path, 'r') as gt_file, open(csv_path, mode='w', newline='',encoding='utf-8') as csv_file:

    # Analyze action classification results, comparing predictions to ground truths. 
    # Calculates metrics (TP, FP, FN, TN), misclassification matrix, and logs errors.
    pred_dict = json.load(pred_file)["Actions"]
    gt_dict = json.load(gt_file)["Actions"]
    action_error = []
    action_results = {cls:{'TP':0,'FP':0,'FN':0,'TN':0, 'cnt_pred':0, 'cnt_gt':0} for cls in action_class}
    action_confusion_matrix = [[0 for _ in range(len(action_class))] for _ in range(len(action_class))] # matrix to store the number of misclassified classes
    action_precision, action_recall = [0] * len(action_class), [0] * len(action_class)

    for key in pred_dict:
        pred_value = pred_dict[key]['Action class']
        gt_value = gt_dict[key]['Action class']
        pred_index = action_class.index(pred_value)
        gt_index = action_class.index(gt_value)
        action_results[pred_value]['cnt_pred']+=1
        action_results[gt_value]['cnt_gt']+=1
        if gt_value == 'Dive':
            print ("Dive video num: ",key)

        action_confusion_matrix[gt_index][pred_index]+=1

        if(pred_value == gt_value):
            action_results[pred_value]['TP'] +=1

        if(pred_value != gt_value):
            action_results[pred_value]['FP'] += 1
            action_results[gt_value]['FN'] += 1
            action_error.append(key)

    for cls, metrics in action_results.items():
        action_precision[action_class.index(cls)] = metrics['TP'] / (metrics['TP'] + metrics['FP']) if metrics['TP'] + metrics['FP'] > 0 else 0
        action_recall[action_class.index(cls)] = metrics['TP'] / (metrics['TP'] + metrics['FN']) if metrics['TP'] + metrics['FN'] > 0 else 0
    
    
    ## Analyze Severity
    pred_severity_count = [0] * len(severity_class)
    gt_severity_count = [0] * len(severity_class)
    severity_accuracy_per_class = [[0] * 2 for _ in range(len(action_class) )] # 0: correct count, 1: error count
    severity_error = []
    severity_confusion_matrix = [[0] * len(severity_class) for _ in range(len(severity_class))] 

    for key in pred_dict:
        pred_action = pred_dict[key]['Action class']
        gt_action = gt_dict[key]['Action class']
        pred_severity = pred_dict[key]['Severity']
        gt_severity = gt_dict[key]['Severity']
        if len(pred_severity) == 0: # if the case is "No offence"
            pred_severity = '0.0'
        if len(gt_severity) == 0:
            gt_severity = '0.0'
        pred_index = severity_class.index(pred_severity)
        gt_index = severity_class.index(gt_severity)

        severity_confusion_matrix[gt_index][pred_index]+=1

        if pred_severity != gt_severity:
            severity_error.append(key)
            severity_accuracy_per_class[action_class.index(gt_action)][1] += 1

        elif pred_severity == gt_severity:
            severity_accuracy_per_class[action_class.index(gt_action)][0] += 1


        pred_severity_count[severity_class.index(pred_severity)]+=1
        gt_severity_count[severity_class.index(gt_severity)]+=1



    ## Output Section
    writer = csv.writer(csv_file)
    writer.writerow(['# Action Classification'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Accuracy', 1 - len(action_error)/len(pred_dict)])
    writer.writerow(['Total video', len(pred_dict)])
    writer.writerow(['Total errors', len(action_error)])

    writer.writerow(['# Action Classification metrics per class'])
    writer.writerow(['Class', 'Precision', 'Recall', 'Pred count', 'GT count'])

    for cls_index in range(len(action_class)):
        writer.writerow([action_class[cls_index], f"{action_precision[cls_index]:.2f}", f"{action_recall[cls_index]:.2f}", action_results[action_class[cls_index]]['cnt_pred'], action_results[action_class[cls_index]]['cnt_gt']])   

    writer.writerow(['# Action Classification Confusion Matrix'])
    writer.writerow(['GT Class/Pred Class'] + action_class)
    for gt_index, gt_name in enumerate(action_class):
        row = [gt_name]
        for pred_index in range(len(action_class)):
            row.append(action_confusion_matrix[gt_index][pred_index])
        writer.writerow(row)

    writer.writerow(['# Error Video Numbers'])
    writer.writerow(['Error video numbers'] + action_error)

    # Severity output 
    writer.writerow(['# Severity Distribution'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Accuracy', 1 - len(severity_error)/len(pred_dict)])
    writer.writerow(['Total video', len(pred_dict)])
    writer.writerow(['Total errors', len(severity_error)])

    writer.writerow(['Severity'] + [gt_name for gt_name in severity_class])
    writer.writerow(['GT'] + [gt_val for gt_val in gt_severity_count])
    writer.writerow(['Pred'] + [pred_val for pred_val in pred_severity_count])

    writer.writerow(['# Severity Classification Confusion Matrix'])
    writer.writerow(['GT Class/Pred Class'] + severity_class)
    for gt_index, gt_name in enumerate(severity_class):
        row = [gt_name]
        for pred_index in range(len(severity_class)):
            row.append(severity_confusion_matrix[gt_index][pred_index])
        writer.writerow(row)

    writer.writerow(['# Severity Accuracy per Action Class'])
    writer.writerow(['Action class', 'Accuracy'])
    for gt_index, gt_name in enumerate(action_class):
        correct = severity_accuracy_per_class[gt_index][0]
        wrong = severity_accuracy_per_class[gt_index][1]
        accuracy = correct / (correct+wrong)
        writer.writerow([gt_name, f"{accuracy:.2f}"])

    writer.writerow(['# Error Video Numbers'])
    writer.writerow(['Error video numbers'] + severity_error)
    

    """
    print(args.type,'Analysis Results')
    print('Accuracy: ', 1- len(err)/len(pred_dict))
    print('Total video: ', len(pred_dict))
    print('Total errors: ', len(err))
    print('Error video numbers: ', err)
    """


