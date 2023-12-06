from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import DBSCAN
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import pickle
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

test_ratio = 80
anomaly_type_num = 10
num_cases = 25
n_neighbors = 5

class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size) 
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)  
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

def print_result(res_list, test_list, label_map):
    cnt_num = [[0 for _ in range(3)] for i in range(anomaly_type_num)]
    cnt = 0
    for i in range(len(res_list)):
        if res_list[i]==test_list[i]:
            cnt+=1
            cnt_num[label_map[int(res_list[i])]][0] += 1
        else:
            cnt_num[label_map[int(res_list[i])]][1] += 1
            cnt_num[label_map[int(test_list[i])]][2] += 1  

    f_score_list = []
    for i in cnt_num:
        if i[0]==0:
            continue
        else:
            f_score_list.append(2*i[0] / (2*i[0] + i[1] + i[2]))

    print(cnt_num)
    print("f_score", f_score_list)
    return cnt

'''
诊断精度实验比较函数
'''
def exp_comparison(random_data = False):

    training_samples = []
    with open("training_samples.csv", "r") as f:
        for line in f.readlines():
            training_samples.append(line.strip().split(","))
            # convert into floats
            training_samples[-1] = [float(x) for x in training_samples[-1]]
       
    training_samples = np.array(training_samples)

    X = training_samples[:, :170]
    #min_val = X.min()
    #max_val = X.max()
    #X = (X - min_val) / (max_val - min_val)

    y = training_samples[:, -11:]

    testing_samples = []
    with open("testing_samples.csv", "r") as f:
        for line in f.readlines():
            testing_samples.append(line.strip().split(","))
            # convert into floats
            testing_samples[-1] = [float(x) for x in testing_samples[-1]]
       
    testing_samples = np.array(testing_samples)

    X_test = testing_samples[:, :170]
    #min_val = X_test.min()
    #max_val = X_test.max()
    #X_test = (X_test - min_val) / (max_val - min_val)

    y_test = testing_samples[:, -11:]

    # 测试普通的DNN方法
    # import pdb; pdb.set_trace()
    # Convert to PyTorch tensors
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.long) # assuming y contains class labels
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)

    # Create dataset and dataloader for training
    train_dataset = TensorDataset(X_tensor, y_tensor)
    train_loader = DataLoader(dataset=train_dataset, batch_size=64, shuffle=True)

    # For test data
    test_loader = DataLoader(dataset=X_test_tensor, batch_size=64, shuffle=False)
    
    input_size = X.shape[1]
    hidden_size = 50 # You can choose a different number
    num_classes = 11

    model = SimpleNN(input_size, hidden_size, num_classes)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    #optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)

    num_epochs = 50
    for epoch in range(num_epochs):
        for i, (inputs, labels) in enumerate(train_loader):
            # Forward pass
            outputs = model(inputs)
            labels = labels.float()
            loss = criterion(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    model.eval() # Set the model to evaluation mode
    res_nn = []

    with torch.no_grad():
        for inputs in test_loader:
            outputs = model(inputs)
            # _, predicted = torch.max(outputs.data, 1)
            probabilities = torch.sigmoid(outputs.data)
            threshold = 0.5
            binary_labels = (probabilities > threshold).int()

        for k in range(binary_labels.size(0)):
            # Get the indices of the sorted probabilities
            sorted_indices = torch.argsort(probabilities[k], descending=True)
            # Count how many probabilities are above the threshold
            count_above_threshold = torch.sum(probabilities[k] > threshold).item()

            #import pdb; pdb.set_trace()

            # Keep at most top 3 probabilities above the threshold
            # import pdb; pdb.set_trace()
            max_ones = min(count_above_threshold, 5)
            # Set the first 'max_ones' indices to 1, rest to 0
            binary_labels[k] = torch.zeros_like(binary_labels[k])
            if max_ones > 0:
                binary_labels[k][sorted_indices[:max_ones]] = 1
    
    # for binary_labels, every ten elements as a group
    for i in range(6):
        tested_labels = binary_labels[i*10:(i+1)*10]
        real_labels = y_test[i*10:(i+1)*10]

        total_label_num = 0
        right_label_num = 0
        wrong_label_num = 0

        for j,label in enumerate(real_labels):
            # count the number of 1s in label list
            label = torch.tensor(label, dtype=torch.float32)
            total_label_num += int(sum(label))
            # count the number of 1s in the same position of label and tested_labels[j]
            right_label_num += int(sum(label * tested_labels[j]))

            total_test_num = int(sum(tested_labels[j]))
            wrong_label_num += total_test_num - int(sum(label * tested_labels[j]))

        print(total_label_num, right_label_num, wrong_label_num, (right_label_num - 0.1 * wrong_label_num) / total_label_num)


    # 测试Decision Tree
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(X,y)
    res_dt = clf.predict(X_test)

    # for binary_labels, every ten elements as a group
    for i in range(6):
        tested_labels = res_dt[i*10:(i+1)*10]
        real_labels = y_test[i*10:(i+1)*10]

        total_label_num = 0
        right_label_num = 0
        wrong_label_num = 0

        for j,label in enumerate(real_labels):
            # count the number of 1s in label list
            # label = torch.tensor(label, dtype=torch.float32)
            total_label_num += int(sum(label))
            # count the number of 1s in the same position of label and tested_labels[j]
            right_label_num += int(sum(label * tested_labels[j]))

            total_test_num = int(sum(tested_labels[j]))
            wrong_label_num += total_test_num - int(sum(label * tested_labels[j]))

        print(total_label_num, right_label_num, wrong_label_num, (right_label_num - 0.1 * wrong_label_num) / total_label_num)


    return True

def data_explore():
    # type_num = test_ratio
    with open('dataset_numerical.pickle', 'rb') as f_train:
        dataset = pickle.load(f_train)
        print(dataset.shape)
        
def data_split():
    pass

def data_extract():
    pass

if __name__ == "__main__":
    # test_ratio = 80
    exp_comparison()
    
    # data_explore()
    # 0"cpu_saturation",
    # 1"io_saturation",
    # 2"database_backup",
    # 3"table_restore",
    # 4"poorly_physical_design",
    # 5"poorly_written_query",
    # 6"workload_spike",
    # 7"flush_log",
    # 8"vacuum_analyze",
    # 9"lock_contention",
    # 10"network_congestion"