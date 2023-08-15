#import all the necessary libraries 
import torch  
import torch.nn  
import torch.optim  
import torch.profiler  
import torch.utils.data  
import torchvision.datasets  
import torchvision.models  
import torchvision.transforms as T    
#prepare input data and transform it 
transform = T.Compose(  
    [T.Resize(224),  
     T.ToTensor(),  
     T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])  
train_set = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)  
# use dataloader to launch each batch 
train_loader = torch.utils.data.DataLoader(train_set, batch_size=1, shuffle=True, num_workers=4)  
# Create a Resnet model, loss function, and optimizer objects. To run on GPU, move model and loss to a GPU device 
device = torch.device("cuda:0")  
model = torchvision.models.resnet18(pretrained=True).cuda(device) 
criterion = torch.nn.CrossEntropyLoss().cuda(device)  
optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)  
model.train()    
# define the training step for each batch of input data 
def train(data):  
    inputs, labels = data[0].to(device=device), data[1].to(device=device)  
    outputs = model(inputs)  
    loss = criterion(outputs, labels)  
    optimizer.zero_grad()  
    loss.backward()  
    optimizer.step()
with torch.profiler.profile(
        schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=2),
        on_trace_ready=torch.profiler.tensorboard_trace_handler('./log/resnet18_batchsize1'),  
        record_shapes=True,
        profile_memory=True,
        with_stack=True
) as prof:
    for step, batch_data in enumerate(train_loader):
        if step >= (1 + 1 + 3) * 2:
            break
        train(batch_data)
        prof.step()  # Need call this at the end of each step to notify profiler of steps' boundary.
