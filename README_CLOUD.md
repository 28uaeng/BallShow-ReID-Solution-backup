# TransReID 云端训练指南 (AutoDL/恒源云)

本指南将指导您如何在云服务器（如 AutoDL、恒源云）上部署并运行全量训练。

## 1. 准备工作

### 1.1 租用服务器
*   **推荐显卡**: RTX 3090 (24GB) 或 RTX 4090 (24GB)
*   **推荐镜像**:
    *   **PyTorch**: 1.12.1 / 1.13.1 / 2.0.0
    *   **Python**: 3.8 / 3.9
    *   **CUDA**: 11.3 / 11.6 / 11.8

### 1.2 准备数据
请在本地准备好以下文件，以便上传：
1.  **数据集**: 将您的 `BallShow-ReID` 文件夹打包为 `BallShow-ReID.zip`。
2.  **权重文件**: `jx_vit_base_p16_224-80ecf9dd.pth`。

## 2. 部署步骤 (在云端终端操作)

### 2.1 拉取代码
在终端中进入数据盘目录（AutoDL 为 `/root/autodl-tmp`）：

```bash
cd /root/autodl-tmp
git clone https://github.com/28uaeng/BallShow-ReID-Solution.git
```

### 2.2 上传并解压数据
使用 FileZilla 或平台提供的网盘工具，将 `BallShow-ReID.zip` 和权重文件上传到 `/root/autodl-tmp`。

```bash
# 解压数据集
unzip BallShow-ReID.zip

# 移动权重文件到指定目录
mkdir -p BallShow-ReID-Solution/weights
mv jx_vit_base_p16_224-80ecf9dd.pth BallShow-ReID-Solution/weights/
```

### 2.3 安装依赖
```bash
cd BallShow-ReID-Solution
pip install -r requirements.txt
pip install opencv-python-headless
```

## 3. 开始训练

一切准备就绪，直接运行以下命令：

```bash
python train.py --config_file configs/BallShow/vit_transreid_stride.yml
```

### 训练参数说明
*   **Batch Size**: 默认设为 64 (适配 24GB 显存)。如果显存不足，请在命令后加 `SOLVER.IMS_PER_BATCH 32`。
*   **Epochs**: 默认 120 轮。
*   **日志**: 训练日志会保存在 `logs/BallShow_vit_transreid_stride` 目录下。

## 4. 测试与导出

训练完成后，模型文件会保存在 `logs/BallShow_vit_transreid_stride/transformer_120.pth`。

运行测试：
```bash
python test.py --config_file configs/BallShow/vit_transreid_stride.yml TEST.WEIGHT 'logs/BallShow_vit_transreid_stride/transformer_120.pth'
```
