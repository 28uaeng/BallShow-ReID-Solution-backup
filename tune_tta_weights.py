"""
TTA 权重调优脚本
快速测试不同权重组合，找到最佳配置
"""
import torch
import numpy as np
import argparse
from tqdm import tqdm

def test_tta_weights(weights_list, config_file, model_path, device='cuda'):
    """
    测试不同的 TTA 权重配置
    
    Args:
        weights_list: 权重列表，每个元素是 [orig, flip, scale1, scale2]
        config_file: 配置文件路径
        model_path: 模型权重路径
        device: 设备
    
    Returns:
        results: 测试结果列表
    """
    import sys
    sys.path.append('.')
    
    from processor import do_inference
    from datasets.make_dataloader import make_dataloader
    from config import cfg as cfg
    from yacs.config import CfgNode as CN
    
    results = []
    
    for i, weights in enumerate(tqdm(weights_list, desc="Testing TTA weights")):
        print(f"\n{'='*60}")
        print(f"Testing weights {i+1}/{len(weights_list)}: {weights}")
        print(f"  orig={weights[0]:.2f}, flip={weights[1]:.2f}, scale1={weights[2]:.2f}, scale2={weights[3]:.2f}")
        print(f"{'='*60}")
        
        # 加载配置
        cfg.merge_from_file(config_file)
        
        # 修改 TTA 权重
        cfg.defs.TEST.USE_TTA = True
        cfg.defs.TEST.RE_RANKING = False  # 关闭 Re-Ranking
        
        # 修改 processor.py 中的权重
        import processor
        processor.TTA_WEIGHTS = weights
        
        # 创建数据加载器
        val_loader, num_query = make_dataloader(cfg)
        
        # 加载模型
        from model.make_model import make_model
        model = make_model(cfg, num_class=3353, camera_num=5)
        model.load_param(model_path)
        model.to(device)
        
        # 测试
        rank1, rank5 = do_inference(cfg, model, val_loader, num_query)
        
        results.append({
            'weights': weights,
            'rank1': rank1,
            'rank5': rank5
        })
        
        print(f"Results: mAP=Unknown, Rank-1={rank1:.1f}%, Rank-5={rank5:.1f}%")
        print(f"{'='*60}")
    
    # 找到最佳配置
    best_result = max(results, key=lambda x: x['rank1'])
    
    print(f"\n{'='*60}")
    print("="*60)
    print("BEST CONFIGURATION FOUND!")
    print("="*60)
    print(f"Weights: {best_result['weights']}")
    print(f"Rank-1: {best_result['rank1']:.1f}%")
    print(f"Rank-5: {best_result['rank5']:.1f}%")
    print("="*60)
    
    # 打印所有结果对比
    print(f"\n{'='*60}")
    print("ALL RESULTS SUMMARY")
    print("="*60)
    print(f"{'Weights':<20} {'Rank-1':<10} {'Rank-5':<10}")
    print("-"*60)
    for r in results:
        print(f"{str(r['weights']):<20} {r['rank1']:>8.1f}%{r['rank5']:>8.1f}%")
    print("="*60)
    
    return results, best_result


def main():
    parser = argparse.ArgumentParser(description='TTA Weight Tuning Script')
    parser.add_argument('--config', type=str, default='configs/BallShow/vit_transreid_stride.yml',
                        help='Config file path')
    parser.add_argument('--weights', type=str, nargs='+',
                        help='Weights to test (e.g., "0.6 1.5 0.8 1.0")')
    parser.add_argument('--model', type=str, default='logs/BallShow_vit_transreid_stride/transformer_120.pth',
                        help='Model weights path')
    parser.add_argument('--device', type=str, default='cuda',
                        help='Device to use (cuda/cpu)')
    
    args = parser.parse_args()
    
    # 解析权重列表
    weights_list = []
    for weights_str in args.weights:
        weights = [float(w) for w in weights_str.split()]
        if len(weights) != 4:
            print(f"Error: Each weights config must have 4 values (orig, flip, scale1, scale2)")
            print(f"Got: {weights} (length: {len(weights)})")
            return
        weights_list.append(weights)
    
    print(f"Testing {len(weights_list)} weight configurations...")
    print("="*60)
    
    # 运行测试
    results, best_result = test_tta_weights(weights_list, args.config, args.model, args.device)
    
    # 保存最佳配置到文件
    with open('best_tta_weights.txt', 'w') as f:
        f.write(f"Best TTA Weights Configuration\n")
        f.write("="*60 + "\n")
        f.write(f"Weights: {best_result['weights']}\n")
        f.write(f"Rank-1: {best_result['rank1']:.1f}%\n")
        f.write(f"Rank-5: {best_result['rank5']:.1f}%\n")
        f.write("="*60 + "\n")
        f.write("\nAll Results:\n")
        f.write("-"*60 + "\n")
        for r in results:
            f.write(f"{str(r['weights'])} {r['rank1']:.1f}% {r['rank5']:.1f}%\n")
    
    print("\nBest configuration saved to: best_tta_weights.txt")


if __name__ == '__main__':
    main()
