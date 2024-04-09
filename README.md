# soccernet_utils
utils for the soccernet project

## Data Analysis Instructions
### Setup
Place your prediction files named `predictions_test.json`, `predictions_train.json`, and `predictions_valid.json` in the `data/` directory.
Similarly, place the corresponding ground truth files named `gt_test.json`, `gt_train.json`, and `gt_valid.json` in the same `data/` directory.

   
### Running the Analysis
To run the analysis, use the following command:


`python data_analysis.py --type <type>`

Replace <type> with either test, train, or valid based on the dataset you wish to analyze.

Example:

`python data_analysis.py --type test`

This command analyzes the test dataset by comparing predictions_test.json with gt_test.json.


### Output
The analysis results will be generated in results/analysis_results.csv.
