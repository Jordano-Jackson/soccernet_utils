import argparse
import json
import os
import csv

parser = argparse.ArgumentParser(description = 'file type checker')

parser.add_argument('--type', type=str, choices=['test', 'train', 'valid'], required =True, help='filetype; test, train, valid')
args = parser.parse_args()

action_class = ['Standing tackling', 'Tackling', 'High leg', 'Pushing', 'Holding', 'Elbowing', 'Challenge', 'Dive']
offense_class = ['Offence', 'Between', 'No offence']
severity_class = ['1.0', '2.0', '3.0', '4.0', '5.0']

pred_path = None;
gt_path = None;
csv_path = 'results/analysis_results.csv'

if args.type == 'test':
    pred_path = 'predictions_test.json'
    gt_path = 'gt_test.json'
elif args.type == 'train':
    pred_path = 'predictions_train.json'
    gt_path = 'dataset','gt_train.json'
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
    err = []
    action_results = {cls:{'TP':0,'FP':0,'FN':0,'TN':0, 'cnt_pred':0, 'cnt_gt':0} for cls in action_class}
    misclassified_matrix = [[0 for _ in range(len(action_class))] for _ in range(len(action_class))] # matrix to store the number of misclassified classes

    for key in pred_dict:
        pred_value = pred_dict[key]['Action class']
        gt_value = gt_dict[key]['Action class']
        pred_index = action_class.index(pred_value)
        gt_index = action_class.index(gt_value)
        action_results[pred_value]['cnt_gt']+=1
        action_results[gt_value]['cnt_pred']+=1

        if(pred_value == gt_value):
            action_results[pred_value]['TP'] +=1

        if(pred_value != gt_value):
            action_results[pred_value]['FP'] += 1
            action_results[gt_value]['FN'] += 1
            err.append(key)
            misclassified_matrix[gt_index][pred_index]+=1

    for cls, metrics in action_results.items():
        precision = metrics['TP'] / (metrics['TP'] + metrics['FP']) if metrics['TP'] + metrics['FP'] > 0 else 0
        recall = metrics['TP'] / (metrics['TP'] + metrics['FN']) if metrics['TP'] + metrics['FN'] > 0 else 0
    


    ## Output Section
    writer = csv.writer(csv_file)

    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Accuracy', 1 - len(err)/len(pred_dict)])
    writer.writerow(['Total video', len(pred_dict)])
    writer.writerow(['Total errors', len(err)])

    writer.writerow([])
    writer.writerow(['Class', 'Precision', 'Recall', 'Pred count', 'GT count'])

    
    for cls, metrics in action_results.items():
        writer.writerow([cls, precision, recall, metrics['cnt_pred'], metrics['cnt_gt']])
        #print(f"{cls}: Precision: {precision:.2f}, Recall: {recall:.2f}, Pred cnt: {metrics['cnt_pred']}, GT cnt: {metrics['cnt_gt']}")
    
    writer.writerow(['GT Class/Pred Class'] + action_class)
    for gt_index, gt_name in enumerate(action_class):
        row = [gt_name]
        for pred_index in range(len(action_class)):
            row.append(misclassified_matrix[gt_index][pred_index])
        writer.writerow(row)

    writer.writerow([])
    writer.writerow(['Error video numbers'])
    writer.writerow(err)

    """
    print(args.type,'Analysis Results')
    print('Accuracy: ', 1- len(err)/len(pred_dict))
    print('Total video: ', len(pred_dict))
    print('Total errors: ', len(err))
    print('Error video numbers: ', err)
    """


