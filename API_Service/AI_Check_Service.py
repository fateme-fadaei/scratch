import os
import glob
from pathlib import Path
import torch

from torch import nn
from PIL import Image
from tqdm import tqdm
from torchvision import transforms
from torchvision.models import resnet18
from torch.utils.data import Dataset, DataLoader

from flask import Flask, jsonify
from flask import request
app = Flask(__name__)

class ScratchDataset(Dataset):
  def __init__(self, path, label, transform=None):
    self.path = path
    self.label = label
    self.transform = transform

  def __len__(self):
    return len(self.path)

  def __getitem__(self, index):
    image = Image.open(self.path).convert("RGB")

    if self.transform:
      image = self.transform(image)

    img_label = torch.tensor([self.label])

    return image, img_label


class ScratchNet(nn.Module):
    def __init__(self):
        super(ScratchNet, self).__init__()
        self.backbone = resnet18()
        # self.fc1 = nn.Linear(in_features=512, out_features=256)
        # self.fc2 = nn.Linear(in_features=256, out_features=1)
        self.fc = nn.Linear(in_features=512, out_features=1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.backbone.conv1(x)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)

        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)

        x = self.backbone.avgpool(x)

        x = x.view(x.size(0), 512)
        # x = self.fc1(x)
        # x = self.fc2(x)
        x = self.fc(x)

        return x

def load_image(image_path):

    image_size = (500, 500)
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize(size=image_size),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_path)

    image = test_transform(image)

    image = image.unsqueeze(0)

    return image

def test_model_service(test_img_path: str, label: int):
    
    # Load Test Image
    load_img = load_image(test_img_path)

    # Load Trained Model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    criterion = nn.BCEWithLogitsLoss()
    model = ScratchNet()
    state_dict = torch.load('model/scratch_net.pth', map_location=torch.device(device))
    model.load_state_dict(state_dict)

    # Evaluate Model
    model.eval()
    with torch.no_grad():
        output = model(load_image(test_img_path))

    pred = 1 if output.sigmoid() > 0.5 else 0
    loss = criterion(output, torch.tensor(label, dtype=torch.float32).reshape(1, 1))

    # return pred, loss.item()

    model_result=jsonify (
        pred= "{:.4f}".format(pred),
        loss= "{:.4f}".format(loss.item()),
        error="null"
    )
    
    return model_result


# if __name__ == "__main__":
#     print(test_model_service("./data/test/images/scratch/C35_jpg.rf.f13c5bde7aae1ec9213983253ddac761.jpg", 0))
    
@app.route('/check1',methods=['GET', 'POST'])
def check1():
    print(request) 
    apiRequest=request.get_json(silent=True)
    
    print (apiRequest)
    apiAddress=apiRequest["Address"]
    apiLabel=apiRequest["Label"]
    print (apiAddress, apiLabel)
    api_result=jsonify (
      error="totaly expected."
    )
    
    # result=test_model_service("/data/test/images/scratch/C35_jpg.rf.f13c5bde7aae1ec9213983253ddac761.jpg", 0)
    
    my_file = Path(apiAddress)
    if my_file.is_file():
     api_result=test_model_service(apiAddress,int(apiLabel))
    else:
     api_result=jsonify (
      error="file not found."
     )
      
    return api_result


# main program
app.run(host='0.0.0.0')
