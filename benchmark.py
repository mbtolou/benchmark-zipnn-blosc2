#!/usr/bin/env python3

import time
import json
import hashlib
import numpy as np
import lz4.frame
import zlib
import lzma
import zstandard as zstd
import brotli
import blosc2
import zipnn
import snappy
import zfpy
import gzip
import psutil
import os
from decimal import Decimal, getcontext

print("=" * 70)
print("Complete Compression Benchmark for Snapshot - V2")
print("=" * 70)

CHUNK_SIZE = 64 * 1024 * 1024  # 64MB reference

def get_resource_usage():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)
    cpu = process.cpu_percent(interval=None) 
    return mem, cpu


def safe_zfpy_compress(data: bytes, data_type="float32"):
    # ZFP نیاز دارد بداند ابعاد و نوع داده چیست
    # برای بنچمارک، ما داده را به صورت یک آرایه ۱ بعدی در نظر می‌گیریم
    dtype = np.float32 if data_type == "float32" else np.float16
    try:
        arr = np.frombuffer(data, dtype=dtype)
        # حالت lossless را فعال می‌کنیم
        return zfpy.compress_numpy(arr, tolerance=0) 
    except:
        # اگر داده عددی نبود، از ZFP استفاده نمی‌کنیم
        return b""

def safe_zfpy_decompress(compressed: bytes):
    try:
        return zfpy.decompress_numpy(compressed).tobytes()
    except:
        return b""

# --- SAFE WRAPPERS FOR BLOSC2 ---
def safe_blosc2_compress(data: bytes, typesize: int = 1, use_bitshuffle=False):
    """Compress data using Blosc2 with optional bitshuffle filtering."""
    try:
        filt = blosc2.Filter.BITSHUFFLE if use_bitshuffle else blosc2.Filter.SHUFFLE
        return blosc2.compress(data, typesize=typesize, filter=filt)
    except Exception:
        pad_len = (typesize - len(data) % typesize) % typesize
        padded = data + b'\0' * pad_len
        compressed = blosc2.compress(padded, typesize=typesize, filter=blosc2.Filter.BITSHUFFLE if use_bitshuffle else blosc2.Filter.SHUFFLE)
        return compressed + len(data).to_bytes(8, 'little')

def safe_blosc2_decompress(compressed: bytes, original_len: int = None):
    """Decompress Blosc2 data with integrity check for padding."""
    try:
        decompressed = blosc2.decompress(compressed)
        if original_len is not None:
            return decompressed[:original_len]
        return decompressed
    except Exception:
        if len(compressed) > 8:
            meta_len = int.from_bytes(compressed[-8:], 'little')
            try:
                decompressed = blosc2.decompress(compressed[:-8])
                return decompressed[:meta_len]
            except: pass
        return blosc2.decompress(compressed)

def benchmark_compression(name, data, compressors, data_type="general"):
    """Core benchmark function - logic untouched, only Blosc2 wrapper added"""
    results = {}
    original_hash = hashlib.sha256(data).hexdigest()
    original_len = len(data)
    
    for comp_name, compress_fn, decompress_fn in compressors:
        try:
            mem_before, _ = get_resource_usage()
            start_time = time.time()

            # Special handling for Blosc2
            if "Blosc2" in comp_name:
                start = time.time()
                ts = 2 if data_type == "float16" else 4 if data_type == "float32" else 1
                is_bitshuffle = "BitShuffle" in comp_name
                compressed = safe_blosc2_compress(data, ts, is_bitshuffle)
                compress_time = time.time() - start
                
                start = time.time()
                decompressed = safe_blosc2_decompress(compressed, original_len)
                decompress_time = time.time() - start
            else:
                # Original logic for all other compressors
                start = time.time()
                compressed = compress_fn(data)
                compress_time = time.time() - start
                
                start = time.time()
                decompressed = decompress_fn(compressed)
                decompress_time = time.time() - start
            
            # Verificar integridade
            decompressed_hash = hashlib.sha256(decompressed).hexdigest()
            integrity_ok = original_hash == decompressed_hash
            
            ratio = len(data) / len(compressed) if len(compressed) > 0 else 0
            compress_speed = len(data) / 1024 / 1024 / compress_time if compress_time > 0 else 0
            decompress_speed = len(data) / 1024 / 1024 / decompress_time if decompress_time > 0 else 0

            end_time = time.time()
            mem_after, cpu_usage = get_resource_usage()

            duration = (end_time - start_time) * 1000
            mem_used = max(0, mem_after - mem_before)
            
            results[comp_name] = {
                "ratio": ratio,
                "compress_speed_mb": compress_speed,
                "decompress_speed_mb": decompress_speed,
                "mem_mb": mem_used,  
                "duration": duration,
                "integrity": integrity_ok,
                "compressed_size": len(compressed)
            }
        except Exception as e:
            results[comp_name] = {"error": str(e)}
    
    return results

def print_section_header(section_number, title, size_info=""):
    """Standardized header"""
    print("\n" + "=" * 70)
    print(f"{section_number}. {title} {size_info}")
    print("=" * 70)

def print_results(name, results):
    """Prints benchmark results in a clean table format"""
    # سرتیتر جدول
    header = f"{'Algorithm':<20} | {'Ratio':>9} | {'Comp':>10} | {'Decomp':>10} | {'RAM':>8} | {'Time':>12} | {'Size':>11}"
    separator = "-" * len(header)
    
    print(separator)
    print(header)
    print(separator)
    
    for comp, r in sorted(results.items()):
        if isinstance(r, dict) and "error" not in r:
            # تبدیل به مقادیر مناسب برای نمایش
            ratio = f"{r['ratio']:.1f}x"
            comp_sp = f"{r['compress_speed_mb']:.0f} MB/s"
            decomp_sp = f"{r['decompress_speed_mb']:.0f} MB/s"
            ram = f"{r['mem_mb']:.1f} MB"
            time_ms = f"{r['duration']*1000:.1f} ms"
            size = f"{r.get('compressed_size', 0)/1024:.1f} KB"
            
            print(f"{comp:<20} | {ratio:>9} | {comp_sp:>10} | {decomp_sp:>10} | {ram:>8} | {time_ms:>12} | {size:>11}")
        elif isinstance(r, dict) and "error" in r:
            print(f"{comp:<20} | ERROR: {r['error']}")
            
    print(separator + "\n")

# Initialize ZipNN
znn = zipnn.ZipNN()
znn_bf16 = zipnn.ZipNN(bytearray_dtype="bfloat16")

# Compressors definitions - unchanged logic
compressors_general = [
    ("LZ4", lz4.frame.compress, lz4.frame.decompress),
    ("ZLIB-6", lambda d: zlib.compress(d, 6), zlib.decompress),
    ("ZSTD-3", zstd.compress, zstd.decompress),
    ("Brotli-4", lambda d: brotli.compress(d, quality=4), brotli.decompress),
    ("LZMA", lzma.compress, lzma.decompress),
    ("ZipNN", znn.compress, znn.decompress),
    ("Blosc2-Std", None, None),
    ("Blosc2-BitShuffle", None, None),
]

compressors_model = [
    ("LZ4", lz4.frame.compress, lz4.frame.decompress),
    ("ZLIB-6", lambda d: zlib.compress(d, 6), zlib.decompress),
    ("ZSTD-3", zstd.compress, zstd.decompress),
    ("Brotli-4", lambda d: brotli.compress(d, quality=4), brotli.decompress),
    ("LZMA", lzma.compress, lzma.decompress),
    ("ZipNN", znn.compress, znn.decompress),
    ("Blosc2-Std", None, None),
    ("Blosc2-BitShuffle", None, None),
]

# Suggested sizes for model weights (number of float16 elements)
WEIGHT_SIZES = [100, 5000, 25000, 350000, 7000000]

def run_python_code_benchmark():
    """1. Python Code - fixed size"""
    print_section_header(1, "CODIGO PYTHON (.py)", "(~190MB)")
    code_template = """
import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer

class LLaMAModel(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.embedding = nn.Embedding(config.vocab_size, config.hidden_size)
        self.layers = nn.ModuleList([TransformerBlock(config) for _ in range(config.num_layers)])
        self.norm = nn.LayerNorm(config.hidden_size)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size)
    
    def forward(self, input_ids, attention_mask=None):
        x = self.embedding(input_ids)
        for layer in self.layers:
            x = layer(x, attention_mask)
        x = self.norm(x)
        return self.lm_head(x)
""" 
    code = code_template * 5000
    code_data = code.encode()
    print(f"Original Size: {len(code_data)/1024/1024:.2f} MB")
    results = benchmark_compression("Python Code", code_data, compressors_general, data_type="text")
    print_results("Python Code", results)

def run_json_config_benchmark():
    """2. JSON Configs"""
    print_section_header(2, "JSON/YAML CONFIGS", "(~15MB)")
    config = {
        "model": {"name": "llama-7b", "hidden_size": 4096, "num_layers": 32},
        "training": {"lr": 1e-5, "batch_size": 32, "epochs": 100},
        "layers": [{"dim": 4096, "heads": 32, "dropout": 0.1}] * 100
    }
    json_str = json.dumps(config, indent=2) * 2000
    json_data = json_str.encode()
    print(f"Original Size: {len(json_data)/1024/1024:.2f} MB")
    results = benchmark_compression("JSON Config", json_data, compressors_general, data_type="text")
    print_results("JSON Config", results)

def run_training_logs_benchmark():
    """3. Training Logs"""
    print_section_header(3, "LOGS DE TREINAMENTO", "(~9MB)")
    log_line = "2024-12-17 10:00:00 | Epoch 1/100 | Step 500/10000 | Loss: 2.3456 | LR: 1e-5 | GPU: 45%\n"
    logs = log_line * 100000
    log_data = logs.encode()
    print(f"Original Size: {len(log_data)/1024/1024:.2f} MB")
    results = benchmark_compression("Training Logs", log_data, compressors_general, data_type="text")
    print_results("Training Logs", results)

def run_csv_data_benchmark():
    """4. CSV Data"""
    print_section_header(4, "CSV DATA", "(~12MB)")
    csv_lines = "id,text,label,score,timestamp\n"
    for i in range(100000):
        csv_lines += f'{i},"Sample text {i}",{i%5},{np.random.random():.4f},2024-12-17\n'
    csv_data = csv_lines.encode()
    print(f"Original Size: {len(csv_data)/1024/1024:.2f} MB")
    results = benchmark_compression("CSV Data", csv_data, compressors_general, data_type="text")
    print_results("CSV Data", results)

def run_model_weights_benchmarks():
    """5. Model Weights - Multiple sizes as requested"""
    print_section_header(5, "PESOS FP16/BF16 (Data)", "")
    np.random.seed(42)
    
    for idx, num_elements in enumerate(WEIGHT_SIZES):
        print(f"\n--- Teste {idx+1}/{len(WEIGHT_SIZES)}: {num_elements:,} elementos FP16 ---")
        weights = np.random.randn(num_elements).astype(np.float16) * 0.02
        weight_data = weights.tobytes()
        size_mb = len(weight_data) / 1024 / 1024
        print(f"Size: {size_mb:.3f} MB")
        
        results = benchmark_compression(f"Model Weights {num_elements}", weight_data, 
                                       compressors_model, data_type="float16")
        print_results(f"Model Weights {num_elements}", results)

def run_checkpoint_benchmark():
    """6. PyTorch Checkpoint"""
    print_section_header(6, "CHECKPOINTS PyTorch (.pt)", "(~80MB)")
    checkpoint = b""
    checkpoint += np.random.randn(5000000).astype(np.float32).tobytes()
    checkpoint += json.dumps({"epoch": 100, "loss": 0.001, "lr": 1e-6}).encode() * 100
    print(f"Original Size: {len(checkpoint)/1024/1024:.2f} MB")
    results = benchmark_compression("Checkpoint", checkpoint, compressors_general, data_type="mixed")
    print_results("Checkpoint", results)

# ====================== Decimal32 Generator ======================
def generate_decimal32_data(num_elements: int, scale: int = 4) -> bytes:
    """شبیه‌سازی Decimal32 ClickHouse (ذخیره به صورت Int32)"""
    getcontext().prec = 9  # Decimal32
    
    # تولید اعداد واقع‌گرایانه (مثل قیمت، مقدار، درصد)
    magnitudes = np.random.normal(0, 3, num_elements).astype(np.float64)
    values = (10 ** magnitudes) * np.random.uniform(0.5, 2.0, num_elements)
    
    # اعمال scale
    scaled = np.round(values * (10 ** scale)).astype(np.int32)
    return scaled.tobytes()

def run_model_weights_benchmarks():
    print_section_header(5, "MODEL WEIGHTS (FP16)", "")
    sizes = [100_000, 1_000_000, 5_000_000]
    
    for num_elements in sizes:
        print(f"\n--- {num_elements:,} elements FP16 ---")
        data = np.random.randn(num_elements).astype(np.float16) * 0.05
        data_bytes = data.tobytes()
        print(f"Raw Size: {len(data_bytes)/1024/1024:.2f} MB")
        
        results = benchmark_compression(f"FP16_{num_elements}", data_bytes, compressors_general, data_type="float16")
        print_results(f"FP16 Weights", results)


def run_decimal_benchmarks():
    print_section_header(6, "DECIMAL32 BENCHMARKS", "")
    sizes = [25_000, 500_000, 4_000_000 ]
    scales = [0, 2, 5, 7]
    
    for num in sizes:
        for scale in scales:
            print(f"\n--- Decimal32 | {num:,} elements | Scale = {scale} ---")
            data = generate_decimal32_data(num, scale)
            print(f"Raw Size: {len(data)/1024/1024:.2f} MB")
            
            results = benchmark_compression(f"Dec32_s{scale}", data, compressors_general, data_type="decimal32")
            print_results(f"Decimal32 (scale={scale})", results)

def main():
    print("=" * 70)
    
    run_python_code_benchmark()
    run_json_config_benchmark()
    run_training_logs_benchmark()
    run_csv_data_benchmark()
    run_model_weights_benchmarks()
    run_checkpoint_benchmark()
    run_decimal_benchmarks()
    
    print("\n" + "=" * 70)
    print("BENCHMARK RESULT")
    print("=" * 70)

if __name__ == "__main__":
    main()





