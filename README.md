# wgan-gp-info-hide
 对论文《A coverless steganography method based on generative adversarial network》进行的代码复现

# 环境说明
python3.6

pytorch

# 论文地址
[原地址](https://jivp-eurasipjournals.springeropen.com/articles/10.1186/s13640-020-00506-6#Ack1)

[论文翻译地址](https://blog.csdn.net/liu428hao/article/details/111900985)

# 网络结构
判别器D使用5层卷积层，每层之间使用ReLu激活函数
生成器G使用6层反卷积层，每层之间使用ReLu激活函数，最后一层使用tan激活函数
区别于WGAN-GP的传统做法(训练很多轮D再训练G)，本次实验是D与G每次都训练一轮

# 测试数据
+ 伪装图像在本工程目录 ./data_guise/img/ 下
+ 目标图像在本工程目录 ./data/img/ 下

# 实验结果
基本复现，生成对图像与原图像存在着一些对比度差异，这种差异可能由以下方式解决
- 进行适当调参
- 加深网络结构

详细的论文复现结果分析请见文档



