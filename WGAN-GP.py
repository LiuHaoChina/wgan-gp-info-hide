import os
import matplotlib.pyplot as plt
from datetime import date, datetime
import logging

import torch
from torch import nn
from torchvision import datasets, transforms
from torch import optim
from torch.autograd import Variable
from torchvision.utils import make_grid
from torchvision.utils import save_image
import sys
import matplotlib.pyplot as plt

'''
# 打印原始图像
img = origin.cpu().numpy()[0]
img = img.transpose(1, 2, 0)
plt.imshow(img)
plt.title('origin img')
plt.axis('off')
plt.show()
'''

import cv2

# --------
# 定义全局参数
# --------
windows = sys.platform.startswith('win')

# 本地数据集存放路径
pic_size = 256
num_workers = 0
batch_size = 1
if windows:
    num_workers = 0
    batch_size = 1
else:
    num_workers = 0
    batch_size = 1
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# --------
# 定义网络
# --------
class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=64, kernel_size=4, stride=2, padding=1, bias=False)
        self.batchN1 = nn.BatchNorm2d(64)
        self.LeakyReLU1 = nn.LeakyReLU(0.2, inplace=True)

        self.conv2 = nn.Conv2d(in_channels=64, out_channels=64 * 2, kernel_size=4, stride=2, padding=1, bias=False)
        self.batchN2 = nn.BatchNorm2d(64 * 2)
        self.LeakyReLU2 = nn.LeakyReLU(0.2, inplace=True)

        self.conv3 = nn.Conv2d(in_channels=64 * 2, out_channels=64 * 4, kernel_size=4, stride=2, padding=1, bias=False)
        self.batchN3 = nn.BatchNorm2d(64 * 4)
        self.LeakyReLU3 = nn.LeakyReLU(0.2, inplace=True)

        self.conv4 = nn.Conv2d(in_channels=64 * 4, out_channels=64 * 8, kernel_size=4, stride=2, padding=1, bias=False)
        self.batchN4 = nn.BatchNorm2d(64 * 8)
        self.LeakyReLU4 = nn.LeakyReLU(0.2, inplace=True)

        self.conv5 = nn.Conv2d(in_channels=64 * 8, out_channels=1, kernel_size=4, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.LeakyReLU1(self.batchN1(self.conv1(x)))
        x = self.LeakyReLU2(self.batchN2(self.conv2(x)))
        x = self.LeakyReLU3(self.batchN3(self.conv3(x)))
        x = self.LeakyReLU4(self.batchN4(self.conv4(x)))
        x = self.conv5(x)
        return x


class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.ConvT1 = nn.ConvTranspose2d(in_channels=1, out_channels=16 * 16, kernel_size=4,  padding=3)
        self.batchN1 = nn.BatchNorm2d(16 * 16)
        self.relu1 = nn.ReLU()

        self.ConvT2 = nn.ConvTranspose2d(in_channels=16 * 16, out_channels=16 * 8, kernel_size=4, padding=0)
        self.batchN2 = nn.BatchNorm2d(16 * 8)
        self.relu2 = nn.ReLU()

        self.ConvT3 = nn.ConvTranspose2d(in_channels=16 * 8, out_channels=8 * 8, kernel_size=4, padding=3)
        self.batchN3 = nn.BatchNorm2d(8 * 8)
        self.relu3 = nn.ReLU()

        self.ConvT4 = nn.ConvTranspose2d(in_channels=8 * 8, out_channels=8 * 4, kernel_size=4, padding=0)
        self.batchN4 = nn.BatchNorm2d(8 * 4)
        self.relu4 = nn.ReLU()

        self.ConvT5 = nn.ConvTranspose2d(in_channels=8 * 4, out_channels=4 * 4, kernel_size=4, padding=3)
        self.batchN5 = nn.BatchNorm2d(4 * 4)
        self.relu5 = nn.ReLU()

        self.ConvT6 = nn.ConvTranspose2d(in_channels=4 * 4, out_channels=1, kernel_size=4, padding=0)
        self.tanh = nn.Tanh()  # 激活函数

    def forward(self, x):
        x = self.relu1(self.batchN1(self.ConvT1(x)))
        # print(f'第1层网络后图像shape：{x.shape} ')
        x = self.relu2(self.batchN2(self.ConvT2(x)))
        x = self.relu3(self.batchN3(self.ConvT3(x)))
        x = self.relu4(self.batchN4(self.ConvT4(x)))
        x = self.relu5(self.batchN5(self.ConvT5(x)))
        x = self.ConvT6(x)
        x = self.tanh(x)
        # print(f'最终层网络后图像shape：{x.shape} ')
        return x


# 定义辅助函数
def denorm(x):
    out = (x + 1) / 2
    return out.clamp(0, 1)

if __name__ == "__main__":
    # 将日志保存到文件
    logging.basicConfig(filename='logger.log', level=logging.INFO)
    # ----------
    # 加载 目标 数据集
    # ----------
    trans = transforms.Compose([
        transforms.Resize(pic_size),  # 设置图像大小
        transforms.Grayscale(),
        transforms.ToTensor(),  # 转换为tensor类型，且令数值处于[0,1]
        transforms.Normalize((0.1307,), (0.3081,))
        # transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # 令数值处于[0,1]之间
    ])
    dataset = datasets.ImageFolder('./data', transform=trans)  # 数据路径
    dataloader = torch.utils.data.DataLoader(dataset,
                                             batch_size=batch_size,  # 批量大小
                                             shuffle=True,  # 乱序
                                             num_workers=0  # 多进程
                                             )
    # ----------
    # 加载 伪装图像 数据集
    # ----------
    dataset_guise = datasets.ImageFolder('./data_guise', transform=trans)  # 数据路径
    dataloader_guise = torch.utils.data.DataLoader(dataset_guise,
                                             batch_size=batch_size,  # 批量大小
                                             shuffle=True,  # 乱序
                                             num_workers=0  # 多进程
                                             )

    # ----------
    # 初始化网络
    # ----------
    D = Discriminator().to(device)  # 定义分类器
    G = Generator().to(device)  # 定义生成器
    # -----------------------
    # 定义损失函数和优化器
    # -----------------------
    learning_rate = 0.001
    d_optimizer = torch.optim.Adam(D.parameters(), lr=learning_rate, betas=(0.5, 0.9))
    g_optimizer = torch.optim.Adam(G.parameters(), lr=learning_rate, betas=(0.5, 0.9))
    # 每3次降低学习率
    d_exp_lr_scheduler = torch.optim.lr_scheduler.StepLR(d_optimizer, step_size=100, gamma=0.95)
    g_exp_lr_scheduler = torch.optim.lr_scheduler.StepLR(g_optimizer, step_size=100, gamma=0.95)
    # 定义惩罚系数
    penalty_lambda = 0.1
    # --------
    # 开始训练
    # --------
    num_epochs = 50000
    sample_dir = './results/wgan'
    # 将测试使用的噪声换成伪装图像
    test_noise = Variable(torch.FloatTensor(40, 100, 1, 1).normal_(0, 1))#.to(device)  # 用于测试绘图
    for j, (guise, _) in enumerate(dataloader_guise):
        guise = guise.to(device)
        test_noise = guise

    total_step = len(dataloader)  # 依次epoch的步骤
    # ------------------
    # 一开始学习率快一些
    # ------------------
    for epoch in range(num_epochs):
        d_exp_lr_scheduler.step()
        g_exp_lr_scheduler.step()
        for i, (images, _) in enumerate(dataloader):
            batch_size = images.size(0)
            images = images.reshape(batch_size, 1, pic_size, pic_size).to(device)
            # 创造real label和fake label
            real_labels = torch.ones(batch_size, 1).to(device)  # real的pic的label都是1
            fake_labels = torch.zeros(batch_size, 1).to(device)  # fake的pic的label都是0
            # 将测试使用的噪声换成伪装图像
            noise = Variable(torch.randn(batch_size, 100, 1, 1))#.to(device)
            for j, (guise, _) in enumerate(dataloader_guise):
                guise = guise.to(device)
                noise = guise

            # ---------------------
            # 开始训练discriminator
            # ---------------------
            D.train()
            G.train()
            # 首先计算真实的图片
            outputs = D(images)
            d_loss_real = -torch.mean(outputs)

            # 接着使用生成器训练得到图片, 放入判别器
            fake_images = G(noise)
            outputs = D(fake_images)
            d_loss_fake = torch.mean(outputs)

            # 生成gradient penalty

            # 1. P_data与P_G的中间区域
            alpha = torch.rand((batch_size, 1, 1, 1)).to(device)
            x_hat = alpha * images.data + (1 - alpha) * fake_images.data
            x_hat.requires_grad = True

            # 2. 计算penalty region处的梯度
            pred_hat = D(x_hat)
            gradient = torch.autograd.grad(outputs=pred_hat, inputs=x_hat,
                                           grad_outputs=torch.ones(pred_hat.size()).to(device), create_graph=True,
                                           retain_graph=True)  # 计算梯度
            gradient_penalty = penalty_lambda * (
                        (gradient[0].view(gradient[0].size()[0], -1).norm(p=2, dim=1) - 1) ** 2).mean()

            # 三个loss相加, 反向传播进行优化
            d_loss = d_loss_real + d_loss_fake + gradient_penalty
            g_optimizer.zero_grad()  # 两个优化器梯度都要清0
            d_optimizer.zero_grad()
            d_loss.backward()
            d_optimizer.step()

            # ------------------------------------
            # 开始训练generator(本质上是要多训练几轮D, 在训练G的，这里直接改成训练一轮G一轮D了)
            # ------------------------------------
            # if (i + 1) % 2 == 0:
            if True:
                # normal_noise = Variable(torch.randn(batch_size, 100, 1, 1)).normal_(0, 1).to(device)
                fake_images = G(noise)  # 生成假的图片
                outputs = D(fake_images)  # 放入辨别器
                g_loss = -torch.mean(outputs)  # 希望生成器生成的图片判别器可以判别为真
                d_optimizer.zero_grad()
                g_optimizer.zero_grad()
                g_loss.backward()
                g_optimizer.step()

            # ----------
            # 打印结果
            # ---------
            if epoch % 200 == 0:
                t = datetime.now()  # 获取现在的时间
                logging.info(
                    'Time {}, Epoch [{}/{}], Step [{}/{}], d_loss_real:{:.4f} + d_loss_fake:{:.4f} + gradient_penalty:{:.4f} = d_loss: {:.4f}, g_loss: {:.4f}, d_lr={:.6f},g_lr={:.6f}'
                    .format(t, epoch, num_epochs, i + 1, total_step, d_loss_real.item(), d_loss_fake.item(),
                            gradient_penalty.item(), d_loss.item(), g_loss.item(),
                            d_optimizer.param_groups[0]['lr'], g_optimizer.param_groups[0]['lr']))
        # -----------
        # 结果的保存
        # ----------
        # 每一个epoch显示图片(这里切换为eval模式)
        G.eval()
        test_images = G(test_noise)
        if epoch % 10 == 0:
            print(f'当前epoh={epoch}，共计有{num_epochs}轮')
            save_image(denorm(test_images), os.path.join(sample_dir, 'fake_images-norm-{}.png'.format(epoch)))
        # Save the model checkpoints
        torch.save(G.state_dict(), './models/G.ckpt')
        torch.save(D.state_dict(), './models/D.ckpt')
