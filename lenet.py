import tqt
import torch.nn as nn
import torch


class lenet(nn.Module):
    def __init__(self, quant=False):
        super().__init__()
        self.proc = nn.ModuleList()
        dic = tqt.wrapper.OFUNCTION if quant is False else tqt.wrapper.QFUNCTION
        self.proc.append(dic['Conv2d'](1, 6, 5, 1, 2))
        self.proc.append(dic['MaxPool2d']((2, 2)))
        self.proc.append(dic['Conv2d'](6, 16, 5))
        self.proc.append(dic['MaxPool2d']((2, 2)))
        self.proc.append(dic['Conv2d'](16, 120, 5))
        self.proc.append(dic['Linear'](120, 84))
        self.proc.append(dic['Linear'](84, 10))

    def forward(self, x):
        for idx, p in enumerate(self.proc):
            x = p(x)
            if (idx == 4):
                x = x.reshape(x.shape[0], -1)
        return x


net = lenet(quant=False)
qnet = lenet(quant=True)
x = torch.rand(50, 1, 28, 28)
handler = tqt.threshold.hook_handler
tqt.threshold.add_hook(qnet.proc, handler)
qnet(x)
for idx, p in enumerate(qnet.proc):
    if hasattr(p, 'acti_log2_t'):
        tqt.threshold.kl.entropy_calibration(p)
    if hasattr(p, 'weight_log2_t'):
        tqt.threshold.max.threshold_weight_max(p)
    if hasattr(p, 'bias_log2_t'):
        tqt.threshold.max.threshold_bias_max(p)