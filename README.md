# CZ4042-Neural Network and Deep Learning
Social Networking has taken over the globe with almost every person having access to internet connection being on at least one of the social media platforms whether it's Whatsapp, Instagram or Snapchat. These platforms are a great way to keep up to date on our close ones. Twitter is one such social media platform that has over 200 million users  interacting with each other through short textual messages called ‘tweets’. These tweets are primarily a way to express the user's opinions about a range of topics whether it's about politics or sports, product reviews or philosophical thoughts. One similarity amongst these ocean of tweets is that they more often than not express user emotions/sentiment such as angry, sad, happy etc. This motivated our team to try and identify the sentiment of a tweet in order to assist users in identifying the type of content they are exposed to on a daily basis. In order to classify these tweets we decided to employ various Deep Learning Neural Networks like Long Short Term Memory (LSTM), Recurrent Neural Networks, Convolutional Neural Networks along with enhancements such as Attention layers and Hyperparameter Tuning.

The original data can be found in `/data/Original Data`. To follow along in the training process, please follow the following order:
- `/Source-codes/Data-Cleaning.ipynb`
- `/Source-codes/Exploratory-Data-Analysis.ipynb`
- `/Source-codes/Feature-Engineering.ipynb`
- `/Source-codes/LSTM-Vanilla-First-Trial.ipynb`
- Following the above Jupyter Notebook, please execute the following files for model construction, training and tuning.
```bash 
python lstm_trial_architecture.py       # Train different model architectures to see model progression
python lstm_final.py                     # Train the final model architectures ( with 9 and 3 labels )
python hyperparameter_tuning.py          # Identify the best Hyperparameters for the final model
```
- For post - processing, execute `/Source-codes/Postprocessing.ipynb`
