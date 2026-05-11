# Compression Benchmark Suite for Structured Data

A high-performance benchmarking tool designed to evaluate the efficiency of various compression algorithms on structured datasets, including floating-point arrays, CSVs, logs, and configuration files.

## Overview
This suite provides a comprehensive comparison of modern compression libraries. It measures **Compression Ratio**, **Throughput (MB/s)**, **RAM usage**, and **Integrity** to help developers choose the optimal algorithm for their specific data storage and transfer requirements.

### Supported Algorithms
*   **Generic:** LZ4, ZLIB, ZSTD, Brotli, LZMA, Snappy.
*   **Numerical/Specialized:** Blosc2 (with BitShuffle), ZFP, ZipNN.

## Prerequisites
Ensure you have the necessary system dependencies. The benchmark requires `psutil` for resource monitoring and specific compression libraries:

```bash
# Clone the repository
git clone <your-repo-url>
cd compression-benchmark

# Install dependencies
pip install -r requirements.txt
# If you don't have a requirements file, use:
pip install psutil numpy lz4 zstandard brotli blosc2 zipnn snappy zfpy
```

## How it Works
The benchmark runs a series of tests on different data types:
1.  **Code/Text:** Evaluates compression for source code and logs.
2.  **Configurations:** Tests performance on structured JSON/YAML data.
3.  **Numerical Data:** Focuses on FP16/BF16/FP32 arrays (crucial for data-dense applications).
4.  **Checkpoints:** Tests mixed-type binary files.

It tracks:
- **Ratio:** Original size vs. Compressed size.
- **Speed:** Encoding and decoding throughput in MB/s.
- **Resource Usage:** Peak RAM consumption during the process.
- **Integrity:** Verification via SHA-256 hashing.

## Running the Benchmark
Simply execute the main script:

```bash
python3 benchmark.py
```

## Sample Output
The results are displayed in a formatted table for easy comparison:

برای نمایش حرفه‌ای نتایج شما در فایل‌های Markdown (مانند `README.md` یا گزارش‌های گیت‌هاب)، جداول زیر را بر اساس داده‌های ارسالی شما آماده کرده‌ام:

### 1. Python Code (.py)
| Algorithm | Ratio | Comp Speed | Decomp Speed | RAM | Time | Size |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Blosc2-BitShuffle | 6.2x | 1301 MB/s | 1859 MB/s | 0.0 MB | 6334.8 ms | 565.2 KB |
| Blosc2-Std | 40.3x | 2834 MB/s | 5991 MB/s | 0.0 MB | 3726.7 ms | 86.6 KB |
| Brotli-4 | 9958.2x | 734 MB/s | 817 MB/s | 6.4 MB | 10916.0 ms | 0.4 KB |
| LZ4 | 128.4x | 11385 MB/s | 1249 MB/s | 7.0 MB | 4929.8 ms | 27.2 KB |
| LZMA | 3589.4x | 45 MB/s | 1056 MB/s | 3.2 MB | 81211.1 ms | 1.0 KB |
| ZLIB-6 | 202.0x | 377 MB/s | 687 MB/s | 3.4 MB | 16137.1 ms | 17.3 KB |
| ZSTD-3 | 5181.2x | 4851 MB/s | 8412 MB/s | 0.0 MB | 3234.1 ms | 0.7 KB |
| ZipNN | 1.7x | 346 MB/s | 2613 MB/s | 5.9 MB | 13063.2 ms | 2024.3 KB |

### 2. JSON/YAML Configs
| Algorithm | Ratio | Comp Speed | Decomp Speed | RAM | Time | Size |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Blosc2-BitShuffle | 28.4x | 2339 MB/s | 1068 MB/s | 14.0 MB | 27001.9 ms | 507.1 KB |
| Blosc2-Std | 127.9x | 4601 MB/s | 4668 MB/s | 13.8 MB | 13474.0 ms | 112.8 KB |
| Brotli-4 | 78574.5x | 1023 MB/s | 1012 MB/s | 15.0 MB | 35210.6 ms | 0.2 KB |
| LZ4 | 175.2x | 9336 MB/s | 2554 MB/s | 28.3 MB | 15430.2 ms | 82.3 KB |
| LZMA | 6044.2x | 61 MB/s | 1022 MB/s | 14.4 MB | 254596.7 ms | 2.4 KB |
| ZLIB-6 | 269.3x | 385 MB/s | 1077 MB/s | 14.8 MB | 57260.5 ms | 53.6 KB |
| ZSTD-3 | 9629.7x | 7292 MB/s | 11875 MB/s | 0.0 MB | 10559.3 ms | 1.5 KB |
| ZipNN | 2.4x | 1026 MB/s | 5961 MB/s | 0.0 MB | 24134.9 ms | 6109.0 KB |

### 3. Training Logs
| Algorithm | Ratio | Comp Speed | Decomp Speed | RAM | Time | Size |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Blosc2-BitShuffle | 252.3x | 3094 MB/s | 1131 MB/s | 8.5 MB | 15124.8 ms | 34.1 KB |
| Blosc2-Std | 281.7x | 4906 MB/s | 4351 MB/s | 8.0 MB | 8440.0 ms | 30.5 KB |
| Brotli-4 | 90721.6x | 1126 MB/s | 1101 MB/s | 0.0 MB | 19595.4 ms | 0.1 KB |
| LZ4 | 217.7x | 14456 MB/s | 3850 MB/s | 5.1 MB | 7536.6 ms | 39.5 KB |
| LZMA | 5914.0x | 76 MB/s | 732 MB/s | 5.9 MB | 126704.7 ms | 1.5 KB |
| ZLIB-6 | 293.6x | 406 MB/s | 1645 MB/s | 8.5 MB | 30451.3 ms | 29.3 KB |
| ZSTD-3 | 9777.8x | 7333 MB/s | 6986 MB/s | 8.2 MB | 6777.8 ms | 0.9 KB |
| ZipNN | 2.0x | 2271 MB/s | 3964 MB/s | 0.0 MB | 10292.3 ms | 4287.3 KB |

### 4. CSV Data
| Algorithm | Ratio | Comp Speed | Decomp Speed | RAM | Time | Size |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Blosc2-BitShuffle | 3.8x | 524 MB/s | 848 MB/s | 3.4 MB | 15815.3 ms | 1188.3 KB |
| Blosc2-Std | 7.6x | 685 MB/s | 1317 MB/s | 2.8 MB | 11935.9 ms | 585.5 KB |
| Brotli-4 | 6.5x | 113 MB/s | 759 MB/s | 16.9 MB | 46667.3 ms | 686.2 KB |
| LZ4 | 3.6x | 793 MB/s | 1739 MB/s | 8.9 MB | 10408.6 ms | 1249.1 KB |
| LZMA | 17.4x | 2 MB/s | 210 MB/s | 5.5 MB | 1857582.6 ms | 256.8 KB |
| ZLIB-6 | 5.6x | 86 MB/s | 613 MB/s | 4.3 MB | 60590.5 ms | 793.2 KB |
| ZSTD-3 | 7.6x | 458 MB/s | 1507 MB/s | 4.3 MB | 14694.2 ms | 590.1 KB |
| ZipNN | 1.9x | 1836 MB/s | 1985 MB/s | 0.0 MB | 6873.8 ms | 2315.8 KB |

### 5. Numerical Weights (7M Elements)
| Algorithm | Ratio | Comp Speed | Decomp Speed | RAM | Time | Size |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Blosc2-BitShuffle | 1.1x | 917 MB/s | 3728 MB/s | 1.8 MB | 25373.5 ms | 12903.4 KB |
| Blosc2-Std | 1.2x | 1281 MB/s | 2891 MB/s | 12.8 MB | 22429.5 ms | 11542.4 KB |
| LZ4 | 1.0x | 1941 MB/s | 4194 MB/s | 26.5 MB | 17776.5 ms | 13672.7 KB |
| ZSTD-3 | 1.1x | 636 MB/s | 1561 MB/s | 15.3 MB | 36805.9 ms | 12506.5 KB |
| ZipNN | 1.2x | 2247 MB/s | 5092 MB/s | 0.0 MB | 15723.7 ms | 11528.6 KB |

### 6. PyTorch Checkpoint
| Algorithm | Ratio | Comp Speed | Decomp Speed | RAM | Time | Size |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Blosc2-BitShuffle | 1.1x | 899 MB/s | 965 MB/s | 0.0 MB | 51308.2 ms | 18485.7 KB |
| Blosc2-Std | 1.1x | 1083 MB/s | 1489 MB/s | 0.0 MB | 40732.6 ms | 18049.9 KB |
| LZ4 | 1.0x | 1881 MB/s | 2619 MB/s | 57.1 MB | 28777.8 ms | 19532.7 KB |
| ZSTD-3 | 1.1x | 692 MB/s | 1364 MB/s | 0.0 MB | 51815.0 ms | 18077.4 KB |
| ZipNN | 1.1x | 2184 MB/s | 5681 MB/s | 4.9 MB | 22283.1 ms | 17323.2 KB |

## Contributing
Feel free to open issues or pull requests if you would like to add new algorithms or dataset types to the benchmarking suite.

---

### نکاتی برای استفاده بهتر از این README:
1. **فایل `requirements.txt`:** حتماً یک فایل با این نام بسازید و تمام کتابخانه‌هایی که استفاده کردید (`numpy`, `psutil`, `blosc2` و غیره) را داخلش لیست کنید تا کاربر با یک دستور `pip install -r requirements.txt` همه را نصب کند.
2. **شخصی‌سازی:** بخش `<your-repo-url>` را با آدرس گیت‌هاب پروژه خود جایگزین کنید.
3. **توضیح نتایج:** در بخش `Running the Benchmark` می‌توانید اضافه کنید که خروجی مستقیماً در کنسول نمایش داده می‌شود و نیازی به نصب ابزار جانبی ندارید.
